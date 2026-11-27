# VOD Import + AI Clipping: Technical Research Report & Implementation Plan

**Status:** Research and architecture proposal, not yet implemented
**Date:** 2026-11-27
**Scope:** Paste a Kick, Twitch or YouTube VOD link, then analyze it, find moments, auto-edit (trim, captions, reframe, hooks), review in a batch and export for TikTok, Shorts and Reels.

> **How to read prices and limits in this document.** Every price, quota and platform rule here was checked in November 2026 where a source is cited. These numbers change often. Treat them as planning estimates and re-check them against the official page before you commit to a contract or a pricing model. Items marked **(verify)** could not be confirmed from a primary source.

---

## 0. Executive summary

1. **Platform access is the main constraint. AI models are not.** No platform (Twitch, YouTube or Kick) has an official API that hands a third party the media file of a past broadcast. Chat replay for past VODs is also missing from every official API. The product needs an ingest layer built around **permissioned sources**:
   - files the user uploads
   - a live companion that records chat, and optionally a copy of the stream, *while the creator is live*
   - official metadata and signal APIs, such as Twitch clip density
   - link import, gated per platform behind a rights check and a legal decision.
2. **Never move 8 hours of 1080p through the pipeline.** Analyze a 16 kHz mono audio track and a ~160p / 1–2 fps video track. Fetch full-quality frames only for the 10–20 seconds around each clip you actually render. This one decision cuts bandwidth, storage and GPU time by more than 95% and makes a 6-hour VOD analyzable in **about 10–15 minutes of wall time**, with first results in about 5.
3. **Moment finding is a fusion problem.** Cheap signals generate candidates: audio arousal, laughter and scream detection, chat velocity, clip density and scene changes. A semantic pass over the transcript then finds story-shaped moments (setup, then payoff) that signals miss. An LLM judge reranks the union using transcript, chat and keyframes, and writes the "why this moment" explanation. User selections and edits feed a learned ranker over time.
4. **One render spec, two renderers.** Captions and hooks are authored as an ASS subtitle document. The browser renders them with libass compiled to WebAssembly (JASSUB), and the server burns them in with FFmpeg and libass. Preview and export then match pixel for pixel. Layout is a crop and stack graph that maps one-to-one to CSS transforms in the editor and FFmpeg filters on the server.
5. **Recommended stack:** Next.js dashboard (matches this repo's stack) · Postgres with pgvector · Cloudflare R2 (zero egress, which matters for video) · Temporal for durable multi-hour workflows · Modal for scale-to-zero GPU workers · FFmpeg with NVENC on L4 GPUs for rendering · Claude Opus 5.5 for ranking, hooks and titles · an ASR API in v1, moving to self-hosted Parakeet or Whisper at scale.
6. **Build order:** the editor, captions and render path come first because every later feature outputs into them. AI moment finding comes second. Auto-reframe and hooks come third. Live companion, link import and direct publishing come last, because they carry the most platform and legal risk.
7. **Estimated variable cost for a 6-hour VOD with 10 rendered clips × 3 formats: about $2–6** (Section 9). This is low enough that pricing can be set by value rather than cost.

---

## 1. Platform access: what is actually allowed

This section comes first because it shapes the architecture. Everything below is about **VOD media**, **chat**, and **other engagement signals**.

### 1.1 Twitch

| Need | Official option | Notes |
|---|---|---|
| VOD metadata | Helix `Get Videos` | Duration, created_at, type (archive/highlight/upload), `muted_segments`. Use `muted_segments` so the system never suggests a clip inside DMCA-muted audio. |
| VOD media file | **None.** | No Helix endpoint returns a past-broadcast file. Broadcasters can download their own VODs manually from the Video Producer. Third-party HLS fetching (what yt-dlp-style tools do) is not an official API. Twitch's terms restrict downloading outside provided functionality, so this needs a legal decision (Section 1.4). |
| Clip files | Helix **`Get Clips Download`** | GA since 2026-01-16. Returns temporary download URLs for clips. Requires broadcaster or editor authorization (`editor:manage:clips` / `channel:manage:clips`). Useful for importing a creator's own clips. |
| Clip metadata (any public channel) | Helix `Get Clips` | Returns `vod_offset`, `view_count`, `created_at` and `duration`. **This is a strong, legitimate crowd signal:** the timestamps where viewers clipped are where highlights are. It works with an app token for public channels. |
| Live chat | EventSub `channel.chat.message` (WebSocket or webhook) or IRC | Live only. Needs chat-read and bot scopes. Record it yourself. |
| Past-VOD chat replay | **None official.** | Community tools use Twitch's private GQL endpoint. It is undocumented and can break or be blocked at any time. Do not build a core feature on it. |
| Stream markers | Helix `Get Stream Markers` | Creator-placed markers are a high-precision highlight signal when they exist. |
| Retention | n/a | Past broadcasts are kept about 7 days (non-affiliates), 14 days (affiliates) and 60 days (Partners, Turbo and Prime). Highlights and uploads have been capped at 100 hours per channel since May 2025. **Product implication:** a creator has a short window to import a VOD, which is another reason for the live companion. |

### 1.2 YouTube

| Need | Official option | Notes |
|---|---|---|
| Video metadata | Data API v3 `videos.list` | Default quota is 10,000 units per day. |
| Media file | **None, not even for the owner.** | The Data API does not serve media. YouTube's ToS prohibits downloading except through YouTube's own features or with permission. Owners can download their own videos from YouTube Studio or Google Takeout and upload the file. Operationally, YouTube also aggressively blocks automated downloading from datacenter IPs. Server-side link import is fragile as well as risky. |
| Captions | `captions.download` | Owner only. Auto-captions have poor timing for subtitles. Use your own ASR anyway. |
| Live chat | `liveChatMessages.list` / `streamList` | **Live only.** Once chat ends, the API returns `LIVE_CHAT_ENDED` (403/FAILED_PRECONDITION), and there is no replay endpoint. Capture during the stream or not at all. |
| Publishing | `videos.insert` | Costs about 1,600 quota units per upload, so about 6 uploads per day on the default quota **(verify)**. Uploads from unverified API projects are locked to private until the project passes an audit. |
| Retention analytics | YouTube Analytics API | Owner-authorized. Gives real post-publish performance to train the ranker (Phase 4). |

### 1.3 Kick

| Need | Official option | Notes |
|---|---|---|
| API | Public API at `api.kick.com/public/v1`, OAuth 2.1 with PKCE | Official coverage is mainly channels, livestreams and chat. |
| Live chat | Webhook `chat.message.sent` | At-least-once delivery. Deduplicate on `Kick-Event-Message-Id`. Kick auto-unsubscribes after persistent delivery failures, so you need monitoring. Verify webhook signatures with the public key from the API. Third-party docs disagree on the algorithm, so follow the official KickDevDocs repo. |
| VOD media | **No official endpoint found.** | Kick VODs are served as HLS from a public CDN, but there is no documented API. This is the same legal and ToS question as Twitch. |
| Past-VOD chat | None official | Internal v2 endpoints exist but are reverse-engineered and unsupported. |

### 1.4 Recommended ingest policy

Implement ingest as pluggable **adapters**. Each one records a `rights_basis` on the source:

| Adapter | Rights basis | Quality | Chat | Build phase |
|---|---|---|---|---|
| **Direct upload** (resumable tus / S3 multipart) | User attests ownership or permission | Original | Optional: import a chat log file (e.g. from the creator's own logger) | Phase 1 |
| **Live companion: chat capture** (EventSub, Kick webhooks, YouTube streamList) | Creator OAuth | n/a | ✅ Complete and official | Phase 4 (start design in Phase 2) |
| **Live companion: stream copy** (creator adds our RTMP/SRT URL as a second output in OBS or a restream service) | Creator-initiated | Original | ✅ (paired with chat capture) | Phase 4 |
| **Official signal APIs** (Twitch Get Clips/markers/videos, YouTube metadata) | Public data / app token | n/a | Partial proxy (clip density) | Phase 2 |
| **Platform link import** (fetch HLS for a pasted URL) | Requires creator OAuth proving ownership or editor status, **or** a recorded permission attestation for clipper agencies | Up to source | ❌ (or unofficial) | Phase 4, behind a per-platform feature flag, **after legal review** |

The UX stays "paste a link" in every case. The backend resolves the link, finds the official metadata, and then:

- (a) runs link import if the user's connected account owns the channel and policy allows it, or
- (b) asks the user to connect the channel or upload the file, while running the official signal APIs immediately so the user sees value (clip-density heatmap, chat-spike timeline if captured live).

> ⚠️ **Decision for founders and counsel.** Most commercial clipping tools accept arbitrary links. That is a business-risk choice, not a technical one. Possible consequences include ToS enforcement, IP blocking (already severe on YouTube), and copyright claims when clipping someone else's content. Kick's ecosystem actively uses third-party clippers, but permission from the *creator* is still the defensible basis. Store a `rights_basis` and an audit trail for every source either way.

---

## 2. System architecture

### 2.1 Overview

```
┌──────────────────────────── Browser (Next.js dashboard) ─────────────────────────────┐
│ Paste link · Upload · Moments list · Transcript search · Trimmer · Caption editor     │
│ Layout editor · Batch review · Export   (hls.js, WebCodecs, JASSUB, peaks.js)        │
└───────────────┬──────────────────────────────────────────────▲───────────────────────┘
                │ REST/tRPC                                     │ SSE progress events
┌───────────────▼──────────────────────────────────────────────┴───────────────────────┐
│ API (Next.js route handlers or a small TS service) — auth, CRUD, signed URLs,        │
│ OAuth connections (Twitch/Kick/YouTube/TikTok/Meta), rights checks                    │
└───────┬───────────────────────────┬──────────────────────────────┬───────────────────┘
        │                           │                              │
┌───────▼────────┐        ┌─────────▼──────────┐         ┌─────────▼─────────┐
│ Postgres       │        │ Temporal (workflows)│         │ Cloudflare R2      │
│ + pgvector     │◄──────►│ ingest→analyze→rank │◄───────►│ media, renditions, │
│ + FTS          │        │ render→publish      │         │ Parquet features   │
└────────────────┘        └───┬───────────┬─────┘         └────────────────────┘
                              │           │
                 ┌────────────▼──┐   ┌────▼─────────────────────────┐
                 │ CPU workers   │   │ GPU workers (Modal: L4/L40S)  │
                 │ ffmpeg remux, │   │ ASR, audio tagging, face/scene│
                 │ chat features │   │ models, NVENC rendering       │
                 └───────────────┘   └───────────────────────────────┘
┌──────────────────────────── Live companion service (always on) ─────────────────────┐
│ EventSub WS / Kick webhooks / YouTube streamList → chat Parquet + per-second stats  │
│ RTMP/SRT ingest (MediaMTX) → HLS segments to R2                                     │
└──────────────────────────────────────────────────────────────────────────────────────┘
                              │
                     LLM: Claude API (ranking, hooks, titles, caption cleanup)
```

### 2.2 Technology decisions

| Layer | Choice | Why | Alternative if needed |
|---|---|---|---|
| Frontend | **Next.js (App Router), React** | Same stack as this repo. SSR for the library, client components for the editor. | n/a |
| Database | **Postgres** (Neon or Supabase) + `pgvector` + built-in full-text search | One store for relational data, transcript FTS, semantic search and job state. | Typesense or Meilisearch if transcript search needs typo tolerance at scale |
| Object storage | **Cloudflare R2** | Zero egress fees. The editor streams proxies constantly, and on S3 egress would dominate cost. | S3 + CloudFront |
| Orchestration | **Temporal** (Cloud) | Workflows run for hours, fan out to many GPU tasks, need retries, heartbeats and resumability, and span Python and TypeScript. Temporal is built for this. | Inngest or Trigger.dev for a lighter v1. You would outgrow them on long fan-out jobs. |
| GPU compute | **Modal** | Per-second billing, scale-to-zero, fast cold starts, L4/L40S/H100. Spiky per-VOD load is the ideal case for it. | Reserved GPUs (RunPod, Lambda, CoreWeave) once utilization is steady and above ~40% |
| Media toolkit | **FFmpeg** (NVDEC/NVENC builds), **PyAV** | The industry standard. L4 GPUs include NVENC (H.264, HEVC, AV1). | GStreamer |
| Realtime progress | Postgres `job_events` table + **SSE** from the API | Simple and durable. Reconnecting clients replay from the last event id. | Pusher or Ably |
| Live ingest | **MediaMTX** (RTMP/SRT → HLS) | Single binary, records segments. | SRS |
| LLM | **Claude Opus 5.5** (`claude-opus-5-5`), structured outputs, prompt caching, Batch API for non-urgent passes | Long context (1M) holds a full 6-hour transcript. Strong judgment for ranking and writing. Vision for keyframes. | See Section 5.6 for an optional video-native second opinion |

**Repo note:** this repository is the AirPoint dew-point site. Build the clipper as a separate app, either a monorepo `apps/clipper` plus `services/pipeline` (Python), or its own repository. That keeps the AdSense marketing site and the GPU pipeline from sharing deploys.

---

## 3. Long-VOD processing pipeline

### 3.1 Principle: analyze cheap representations and render from the source

At ingest, produce:

| Rendition | Spec | Size for 6 hours | Used by |
|---|---|---|---|
| `audio_16k` | 16 kHz mono FLAC or Opus | ~250–450 MB | ASR, audio events, arousal |
| `analysis_video` | ~256×144, 2 fps, all-intra JPEG frames or low-bitrate H.264 | ~300–700 MB | Scene, face, layout and OCR models |
| `thumb_sprites` | 1 frame every 5 s, 160 px tiles | ~20 MB | Full-VOD timeline scrubbing |
| `mezzanine` | **Remux only** (no transcode) of the source into fMP4/HLS with an index | Source size | Fetching exact segments for proxies and final renders |
| `proxy` (per clip, created on demand) | 720p H.264, keyframe every 0.5–1 s (or all-intra), clip window ±30 s | ~10–30 MB per clip | Frame-accurate editor playback |

For link-import or live-capture HLS sources, download the **audio-only rendition first**. Twitch and YouTube both offer audio-only variants. Transcription can then start within seconds, while video renditions download in parallel. The mezzanine does not need to be downloaded at all: keep the playlist and fetch only the needed segments at render time.

### 3.2 Chunked parallelism

Split the timeline into **20-minute chunks with 30-second overlap**. A 6-hour VOD makes 18 chunks. Fan out per chunk:

```
VodAnalysisWorkflow(vod_id)
 ├─ ResolveSource → rights check → metadata (official API)
 ├─ IngestAudio  (stream download → audio_16k)            [progress 0–10%]
 ├─ parallel:
 │   ├─ for chunk in chunks: Transcribe(chunk)            [10–45%]  → stream results to DB
 │   ├─ for chunk in chunks: AudioEvents(chunk)            (laughter/scream/cheer/music)
 │   ├─ IngestVideoAnalysisRendition → for chunk: VisualFeatures(chunk)
 │   └─ FetchSignals (Twitch clips/markers, captured chat)
 ├─ MergeChunks (dedupe overlap by word timestamps)
 ├─ BuildTimeline (per-second feature store → Parquet in R2)
 ├─ CandidateGeneration (signal peaks ∪ LLM transcript pass) [45–75%]
 ├─ BoundaryRefinement
 ├─ LLMRerank + Explanations                                [75–95%]
 └─ Publish moments → status READY                          [100%]
```

**Progressive results:** each chunk's transcript goes into the database as soon as it finishes, so users can **search the transcript before analysis completes**. Moments are first published from the signal pass (labeled "preliminary") and then replaced by reranked results.

**Throughput targets (estimates, benchmark in Phase 0):**

- ASR for 6 hours of audio: about 1–2 min with self-hosted Parakeet on parallel chunks, about 3–8 min with Whisper large-v3-turbo on 4 L4s, or the vendor's batch turnaround (usually minutes) on an API.
- Audio tagging (CNN14/BEATs-class model): under 3 min on one GPU.
- Visual features at 2 fps (43,200 frames): embeddings plus face detection in about 3–6 min on one L4.
- LLM pass: 2–5 min.
- **End to end: about 10–15 min for a 6-hour VOD, with first searchable transcript in about 2–3 min.**

### 3.3 Feature timeline (the core data structure)

Store one row per second of VOD (`vod_id, t`) in Parquet, with a downsampled copy in Postgres for UI charts:

| Group | Features |
|---|---|
| Speech | words/sec, speaking-time ratio, speaker id(s), overlap (crosstalk), question marks, profanity flags |
| Prosody / arousal | short-term loudness (LUFS), loudness delta vs. a 5-min rolling median, f0 mean/variance, spectral flux, voice/noise ratio |
| Audio events | P(laughter), P(scream/shout/yell), P(cheer/applause/crowd), P(music), P(gunshot/explosion) |
| Chat (if available) | msgs/sec, unique chatters/sec, emote-category counts (laugh / hype / shock / sad / "clip it"), caps ratio, repeated-message (copypasta) burst, subs/bits/donations |
| Crowd signal | Twitch clip count covering t (weighted by views), creator stream markers |
| Visual | shot boundary, motion energy, scene type, face present / face size / expression intensity, on-screen text events (OCR) |

**Normalization matters more than the model.** Streamers have very different baselines: a quiet streamer's "loud" is another's normal, and a 50k-viewer chat is always fast. Compute **robust z-scores** per feature against a rolling 10-minute median and MAD, plus a per-channel prior learned across that channel's past VODs.

**Chat lag alignment.** Chat reacts about 5–15 seconds after the event (stream latency plus reaction time). For each VOD, cross-correlate the chat-velocity curve with the audio-arousal curve over lags of 0–30 s and take the best lag. Use 8 s when correlation is weak. Shift chat features back by that lag before fusing.

---

## 4. Speech recognition and searchable transcripts

### 4.1 Options compared

| Option | Accuracy (stream audio) | Speed | Price (Nov 2026) | Word timing | Diarization | Ops difficulty | Notes |
|---|---|---|---|---|---|---|---|
| **AssemblyAI** Universal-2 / Universal-3.5 Pro (API) | High | Batch, minutes | ~$0.15/hr (U-2) / ~$0.21/hr (U-3.5 Pro), per-second billing; diarization +$0.02/hr, keyterms +$0.05/hr | ✅ | ✅ | Very low | Cheapest strong API. Keyterm prompting helps with streamer names. |
| **Deepgram Nova-3** (API) | High | Very fast batch | ~$0.0043/min (~$0.26/hr) monolingual pre-recorded; multilingual ~$0.0052/min | ✅ | ✅ (add-on) | Very low | Keyterm prompting. Fast turnaround. |
| **ElevenLabs Scribe** (API) | High | Batch | (verify) | ✅ | ✅ | Very low | Can tag non-speech audio events such as laughter, which is a useful extra signal **(verify current feature set)**. |
| **NVIDIA Parakeet-TDT-0.6B-v3** (self-host) | High on English and 25 European languages (~6.3% avg WER on the Open ASR leaderboard) | Extremely fast (RTFx in the thousands at batch 128) | GPU time only, cents per VOD | ✅ native word/segment/char timestamps | ❌ (pair with pyannote) | Medium | Up to 24 min per pass with full attention on an A100 (3 h with local attention). Use 20-min chunks. CC-BY-4.0 model license **(verify)**. |
| **Whisper large-v3 / v3-turbo** via faster-whisper + **WhisperX** (self-host) | High, ~99 languages | Fast with batching (tens× real time per GPU) | GPU time only | ✅ via wav2vec2 forced alignment | ✅ via pyannote | Medium | Can hallucinate during music or silence. Gate with VAD. Best for non-European languages. |

**Stream audio is much harder than benchmark audio.** It has game sound effects, music, crosstalk, slang and emote words ("KEKW", "W", "chat"). Leaderboard WER will not transfer.

**Recommendation:**

- **v1:** use an API. Run a one-day bake-off between AssemblyAI and Deepgram on 5–10 of your own labeled VOD excerpts and pick the winner by WER on *names and slang*. A 6-hour VOD costs about $0.90–1.60. Zero ops cost lets the team focus on the editor.
- **At scale:** self-host Parakeet-TDT-v3 for English and European languages and Whisper-v3-turbo for everything else, both on Modal. Cost drops more than 10×. Keep the API as a fallback.
- **Custom vocabulary per channel:** maintain a glossary (streamer name, friends, recurring bits, games). Feed it as keyterms on APIs or as a prompt on Whisper, and use it in the LLM cleanup pass (Section 6.2).

### 4.2 Diarization

Diarization helps hooks ("his friend says…"), captions (speaker colors) and context. For v1, use the API's diarization add-on. Self-hosted: pyannote `speaker-diarization` (3.x / community pipelines) on GPU takes single-digit minutes for 6 hours in chunks, with cross-chunk speaker linking by embedding clustering. Expect errors when the streamer's voice overlaps a Discord call or a video they're reacting to.

### 4.3 Transcript storage and search

- `transcript_segments(vod_id, id, start_ms, end_ms, speaker, text, tsv tsvector, embedding vector(1024))`. A segment is a sentence or a pause-delimited unit of about 2–15 s.
- Word arrays (`[{w, s, e, conf, speaker}]`) live in JSONB per segment, or in Parquet for very long VODs.
- **Keyword search:** Postgres FTS (`websearch_to_tsquery`) plus `pg_trgm` for fuzzy name matching. Hits return the exact word timestamp so the player can jump to it.
- **Semantic search** ("when did they talk about their ex"): embed 30-second windows and query by cosine similarity. Rerank the top 50 with the query.
- **Chat search** works the same way over chat messages ("where did chat spam 'W'").
- UI: results grouped by time with a 2-line context snippet, a heat strip on the timeline showing hit density, and click to seek with a 3-second pre-roll.

---

## 5. Moment detection: finding real viral potential

### 5.1 Why random or fixed-length cutting fails

Viral clips have **narrative shape**: a setup the viewer understands without the prior 3 hours, an escalation, a payoff, and a reaction tail. Loudness peaks alone find screaming but not *why* it's funny. Transcript-only LLM passes miss purely visual moments, such as a clutch play or a jump scare. The design below combines both and then judges the combined candidates in context.

### 5.2 Stage A: candidate generation (high recall)

1. **Signal-peak candidates.** Build a fused excitement curve:
   `E(t) = Σ wᵢ · z_i(t)` over arousal, laughter, scream, chat velocity (lag-corrected), clip density and markers.
   Smooth it with a 3-second window and use peak-picking with prominence and a minimum gap of 20 s. Start with hand-set weights and learn them later (Section 5.7). Each peak gives a rough window `[peak − 25 s, peak + 10 s]`.
2. **Typed detectors.** Run narrow rules for specific moment types:
   - laughter burst ≥ 1.5 s plus chat laugh emotes → *funny*
   - scream with a shot change or motion spike → *scare / intense*
   - crosstalk plus rising loudness plus negative-sentiment words → *argument*
   - OCR of "VICTORY" / "ACE" / kill-feed bursts → *gameplay win* (game-specific, added later)
   - donation or sub event plus a reaction → *reaction*
3. **LLM semantic pass over the transcript.** Send the full transcript with sparse signal annotations, e.g. `[03:12:44 laughter↑ chat×4.2]`, to Claude Opus 5.5 in 30–60-minute sections (cached system prompt and rubric). Ask for story-shaped moments with start and end word IDs, so timestamps come from real word timings and not from the model inventing times. This finds moments that signals miss: an unhinged hot take, a confession, a perfectly timed one-liner, a long-running bit's payoff.
4. **Union and non-maximum suppression.** Merge overlapping candidates. Target about 3–5× the final list size (e.g., 60–100 candidates for a top-20).

### 5.3 Stage B: boundary refinement

For each candidate:

- **Start:** walk back to the start of the *setup*: the sentence that introduces the topic, the question that prompted the reaction, or the start of the round. Snap to a sentence boundary and a silence gap of at least 150 ms. If a shot cut falls within 0.5 s, prefer it.
- **End:** include the payoff plus a 0.5–2 s reaction tail. Cut before the energy dies or the streamer changes topic. Snap to word end plus 80–150 ms.
- **Length targets:** 15–60 s by default (configurable per platform; Shorts and Reels allow up to about 3 min). Flag candidates that need more context as "long-form". Offer a "tight" and a "full context" version.
- **Muted or blocked ranges:** drop or trim around Twitch `muted_segments` and detected copyrighted-music stretches (P(music) high and low speech). Warn rather than silently drop.

### 5.4 Stage C: LLM judge and rerank (precision plus explanations)

Each refined candidate gets one Claude call with:

- the clip transcript (with speakers), plus 45 s of *preceding* transcript for context checking
- signal summary: peak z-scores, chat sample (top 30 messages by emote density in the lag-corrected window), clip-density count
- 6–8 keyframes (scene-change-aware sampling) as images
- channel context: streamer name and glossary, game or category

Return **structured output** (JSON schema via `output_config.format`):

```json
{
  "scores": {
    "hook_strength": 0-10,        // would the first 2s stop a scroll?
    "self_contained": 0-10,       // understandable with zero prior context?
    "payoff": 0-10,
    "emotional_intensity": 0-10,
    "novelty": 0-10,
    "rewatchability": 0-10,
    "risk": 0-10                  // TOS/brand/defamation/sensitive-content risk
  },
  "category": "funny|argument|intense_gameplay|unexpected|wholesome|rage|hot_take|story|reaction",
  "why": "One or two sentences citing concrete evidence: what is said and what chat/audio did.",
  "evidence": [{"type":"quote","word_ids":[...]}, {"type":"signal","name":"laughter","t":11532.4}],
  "suggested_trim": {"start_word_id": "...", "end_word_id": "..."},
  "needs_context": false
}
```

Implementation notes:

- Cache the rubric and system prompt with prompt caching. Run reranking through the **Message Batches API** (50% cheaper) when the user isn't waiting. Use interactive calls when they are.
- **Final score** in v1: `0.5·LLM_composite + 0.3·signal_score + 0.2·crowd_score`, with a penalty for `risk` and `needs_context`. These weights are a starting point to tune against the evaluation set.
- **Diversity:** use maximal-marginal-relevance re-ranking so the top 20 aren't 8 clips of the same argument. Penalize temporal proximity and same-category clusters.
- **Explanations shown to users** come straight from `why` plus clickable evidence chips ("Laughter 3.1σ above baseline", "Chat ×4.2", "7 viewer clips here").

### 5.5 Audio emotion, laughter, shouting and excitement: model options

| Model | What it gives | Accuracy | Speed | License / cost | Notes |
|---|---|---|---|---|---|
| **PANNs CNN14** (AudioSet) | 527 classes incl. Laughter, Screaming, Shout, Yell, Cheering, Applause, Music, Gunshot, Explosion | AudioSet mAP ≈ 0.43 | Hours of audio in minutes on GPU, real-time on CPU | MIT (verify) | Easiest start. |
| **BEATs / EfficientAT / AST** | Same label space | mAP ≈ 0.46–0.48 | EfficientAT is very fast; AST is heavier | Varies (verify) | Upgrade path. EfficientAT is a good speed/accuracy point. |
| **YAMNet** | 521 classes | mAP ≈ 0.31 | Extremely fast (CPU) | Apache-2.0 | Fallback or cheap first pass. |
| **Dedicated laughter detector** (e.g., Gillick et al. 2021-style models) | Laughter segments | Better laughter precision than general taggers | Fast | Check license | Laughter is the #1 funny signal. Worth a specialized model. |
| **Prosody (DIY)**: torchaudio/librosa loudness, f0 via `torchcrepe`/`penn`, spectral flux | Arousal proxies | Robust after per-channel normalization | Very fast | Permissive | openSMILE/eGeMAPS is the research standard, but **commercial use needs a license**. |
| **Speech emotion recognition** (emotion2vec-class, wav2vec2-SER) | Categorical emotion / valence-arousal | Moderate on in-the-wild audio | Fast | Check each model's license | Use as a weak feature, never alone. |

**Game audio confound:** game explosions and music trigger the same classes as real excitement. Mitigations, in order of cost:

1. Weight voice-gated features: only count arousal when ASR or VAD says the streamer is speaking.
2. Use the facecam as a second modality (mouth open or expression intensity).
3. Optionally run voice/music source separation (Demucs-class) on *candidate windows only*, never on the full 6 hours.

### 5.6 Visual understanding

| Task | Tool | Speed | Notes |
|---|---|---|---|
| Shot / scene boundaries | **TransNetV2** (GPU) or **PySceneDetect** AdaptiveDetector (CPU) | Hundreds+ fps on low-res | Streams have few hard cuts; boundaries mostly mark scene switches (BRB screen, game change). |
| Scene type (gameplay+facecam, gameplay-only, just-chatting / full cam, IRL, desktop / reacting to video, BRB/starting, ad break) | **SigLIP-2 / CLIP embeddings** + logistic-regression head. Zero-shot prompts first, then train on user-confirmed labels. | ~1,000+ frames/s on L4 | Embeddings are reused for semantic frame search and dedupe. |
| On-screen text / HUD | **PaddleOCR** (Apache-2.0) | Run only at shot changes and on candidates | Kill feeds, "VICTORY", donation alerts, on-screen chat box (to mask or crop out). |
| Frame captioning for the LLM | Claude Opus 5.5 vision on 6–8 keyframes per candidate | Per candidate only | Avoids sending hours of video to any model. |
| Optional video-native second opinion | Gemini video input on candidate windows | ~258 tokens/s of video at 1 fps (**verify**: about 15k tokens per minute) | Never on the full VOD (6 h ≈ 5.6M tokens). Useful for purely visual gameplay moments. |
| Open-weights alternative | Qwen-VL family (self-host) | GPU | For bulk frame captioning if API costs ever matter. |

### 5.7 Learning loop: getting better over time

- **Log everything:** suggested → viewed → selected → trimmed (start and end deltas) → exported → published → performance (YouTube Analytics retention and views; TikTok and Instagram insights where the APIs allow).
- **Learning-to-rank:** after about 2–5k labeled candidates, train a LightGBM LambdaMART ranker on [signal features + LLM sub-scores + category + channel priors]. The LLM stays as a feature and as the explanation generator.
- **Per-channel personalization:** channel-level priors (what this audience laughs at, typical clip length) as features.
- **Evaluation set (build in Phase 0):** 20 VODs with human-labeled highlight spans, from your own or creator-provided streams, across 5+ genres (FPS, variety, just-chatting, IRL, horror). Metrics:
  - Precision@10, Recall@20 vs. human picks
  - boundary IoU
  - **trim delta** (seconds users move in/out points; lower means better boundaries)
  - **accept rate** (selected / shown)

---

## 6. Captions and subtitles

### 6.1 Pipeline

1. **Words with timing** come from ASR (Parakeet native timestamps, or WhisperX forced alignment). For each clip, re-run **forced alignment** on the clip's audio (CTC aligner, e.g. wav2vec2 / NeMo forced aligner) for frame-accurate timing after any text corrections.
2. **LLM cleanup, alignment-safe.** Claude receives the clip's word list with IDs plus the channel glossary. It returns *edit operations* (`replace word 17 "kekw"→"KEKW"`, `merge 22-23 "gonna"`, punctuation and casing on IDs), never free text. Changed words are re-aligned. This fixes names, slang and casing without breaking timing.
3. **Chunking into caption pages:** 1–4 words per page for vertical shorts (configurable). Break at punctuation, pauses over 250 ms and speaker changes. Max about 14–18 characters per line at the default size, max 2 lines. Minimum page duration 0.3 s; merge micro-pages.
4. **Emphasis selection:** the LLM marks 1–2 key words per sentence (names, numbers, punchlines, emotional words), boosted by loudness peaks at that word. Emphasized words get the style's highlight treatment.
5. **Styling → ASS document generation:** a deterministic generator turns `{words, pages, emphasis, style_preset, safe_zone}` into an `.ass` file using `\k`/`\kf` karaoke tags, `\t()` transforms (pop / scale / bounce), `\fad`, `\bord`, `\shad` and colors.

### 6.2 Style system

Presets are JSON, so users can save brand kits:

```json
{
  "id": "bold-pop",
  "font": {"family": "Montserrat ExtraBold", "size_pct_of_height": 4.6, "uppercase": true},
  "fill": "#FFFFFF", "stroke": {"color": "#000000", "width_px": 10}, "shadow": {"y": 4, "blur": 0, "alpha": 0.6},
  "active_word": {"mode": "color|box|scale", "color": "#FFE600", "scale": 1.12},
  "emphasis": {"color": "#00FF88", "scale": 1.2},
  "animation": {"page_in": "pop", "duration_ms": 120},
  "position": {"anchor": "center", "y_pct": 62},
  "max_words_per_page": 3,
  "emoji": {"enabled": false, "max_per_clip": 3}
}
```

**Match the clip's energy:** the clip `category` from Section 5.4 selects a default preset. *funny* gets a bouncy colored active word, *intense* gets bold white with red emphasis and a fast pop, *story* or *wholesome* gets clean sentence case with a subtle fade. The user can override, and the override is remembered per channel.

### 6.3 Platform safe zones

Show safe-zone overlays in the editor and run a validator at export. Approximate guidance for a 1080×1920 canvas **(verify against each platform's current overlay templates and store them as data, not code)**:

| Platform | Keep text out of |
|---|---|
| TikTok | top ~150–200 px; bottom ~400–480 px (caption, sound, nav); right ~120–140 px (action buttons) |
| YouTube Shorts | top ~150 px; bottom ~350–420 px; right ~120 px |
| Instagram Reels | top ~200 px; bottom ~420–500 px; right ~120 px |

Default caption anchor: about 55–65% of height. The default hook zone sits just below the top unsafe band.

### 6.4 Preview and render parity

- **Browser:** JASSUB (libass compiled to WASM) renders the same `.ass` over the `<video>` in the editor.
- **Server:** FFmpeg `subtitles=`/`ass=` filter (libass) burns it in.
- Same fonts (bundled and self-hosted) and the same engine give identical line breaks and animation.
- **Word editing UI:** a transcript strip under the timeline. Click a word to edit text, drag edges to adjust timing, split or merge pages, toggle emphasis and change the speaker. Edits update the caption track JSON, and the ASS is regenerated. Never edit ASS by hand.

**Why not Remotion for v1?** Remotion (React to video) is excellent for heavy motion design and keeps React parity. But per-frame headless-Chrome rendering is far slower than libass burn-in on a GPU pipeline. Its company license for automated rendering is $0.01 per render with a $100/month minimum. Keep it as the Phase 5 option for premium animated templates, not the default path.

---

## 7. Intelligent reframing (9:16, 1:1, 4:5, 16:9, custom)

### 7.1 Model of a layout

A layout is a list of **regions**. Each region is a source crop rectangle (normalized coordinates, optionally keyframed over time) mapped to a destination rectangle on the output canvas, plus fill rules:

```json
{
  "canvas": {"w": 1080, "h": 1920},
  "regions": [
    {"name": "facecam", "src": {"x":0.02,"y":0.05,"w":0.22,"h":0.22}, "dst": {"x":0,"y":0,"w":1080,"h":640}, "fit": "cover"},
    {"name": "gameplay", "src_track": "gameplay_path_v1", "dst": {"x":0,"y":640,"w":1080,"h":1280}, "fit": "cover"}
  ],
  "background": {"type": "blur", "source": "full"}
}
```

Templates:

- `stacked_cam_top` (facecam ~33% / gameplay ~67%)
- `gameplay_full` (motion-tracked crop)
- `cam_full` (face-tracked)
- `split_two_speakers`
- `letterbox_blur` (fit the full 16:9 frame with a blurred fill; a safe fallback)
- `pip` (gameplay with a small cam bubble)

### 7.2 Per-shot analysis

1. **Scene type** per shot, from Section 5.6.
2. **Facecam detection** (streamer overlays are the hard part):
   - Detect faces at 2 fps.
   - A *facecam face* is small (under ~15% of frame area), positionally stable across the shot, and inside a region whose border is persistent. Accumulate Canny edges across N frames, keep edges that persist (overlay frames don't move while gameplay does), and run a Hough line/rectangle search for the box enclosing the face.
   - Fallback: expand the face box to a 16:9 or 4:3 box with a margin and ask the user to confirm.
   - **Per-channel layout memory:** once a user confirms or adjusts the facecam box for a channel and scene type, store it in `channel_layout_profiles`. Streamer overlays rarely change, so later VODs need no correction. Detect overlay changes by comparing persistent-edge maps and re-prompt only when they differ.
   - **v2:** train a small detector for "facecam box" on accumulated user corrections. Choose a permissively licensed architecture (e.g. RT-DETR, Apache-2.0).
3. **Gameplay region of interest:** remove the facecam rectangle and static HUD/overlay pixels (low temporal variance). Within the rest, compute a motion/saliency heatmap. Choose the crop window (at the target aspect) that maximizes covered saliency, and bias toward the screen center for FPS crosshair games. Allow **per-game presets** ("Valorant: center 56% width").
4. **Full-cam / IRL:** person and face detection plus **ByteTrack** (MIT) tracking. Choose the subject with **active speaker detection** (Light-ASD / TalkNet-class audio-visual models) when there are several people. If two speakers alternate quickly, use `split_two_speakers`.
5. **Desktop / reacting-to-video:** use OCR plus layout detection to find the content window being watched. Default to `stacked_cam_top` with the content window instead of gameplay.

### 7.3 Smooth, professional camera paths

The analysis is offline because the whole clip is available, so we can do better than a real-time follower:

- Build raw target centers from detections (with confidence). Interpolate across misses.
- Solve for a smooth path: an **L1-optimal camera path** (Grundmann et al., the approach behind YouTube's stabilizer) gives the "static, then deliberate pan" look of a human operator. A simpler v1 is a dead-zone (no movement while the subject stays in the central 60%) plus a critically damped spring with look-ahead.
- Clamp velocity and acceleration. Never pan during the first 0.5 s of a clip.
- **Layout switching with hysteresis:** minimum 2 s per layout; switch only on shot boundaries or sustained (over 1 s) scene-type change. Use hard cuts between layouts (they look intentional), not animated morphs.

### 7.4 Manual control

The editor shows the source frame with draggable or resizable crop rectangles per region, a **keyframe toggle** for moving crops, a layout switcher on the timeline (split the clip into layout segments), and "apply to all clips from this VOD / this channel". Every manual change is saved as a correction label for training.

### 7.5 License warnings for vision models

Common choices carry restrictions:

- InsightFace pretrained models (SCRFD/RetinaFace weights): **non-commercial**.
- Ultralytics YOLO: **AGPL-3.0**.
- WIDER FACE-trained weights: dataset terms apply.

Safer defaults are **MediaPipe face detection (Apache-2.0)** and **OpenCV YuNet (MIT)**. Get a license review of every model and dataset before launch.

---

## 8. Hooks and on-screen text

### 8.1 Generation

Inputs:

- the clip transcript and the 45 s before it
- the category and the `why` from ranking
- keyframe descriptions
- detected entities (people, game and items named)
- channel glossary
- target platform

Claude returns structured output with **5 variants**, one per style: `curiosity`, `funny`, `dramatic`, `controversial`, `surprising`. Each variant has:

```json
{"style":"curiosity","text":"He did NOT expect chat to find out","emphasis":["NOT","chat"],
 "emoji":"😳","grounding":{"word_ids":["w812","w813"]},"spoiler_risk":0.2}
```

### 8.2 Anti-generic and safety guardrails (automated, before showing to the user)

1. **Grounding check:** the hook must reference something concrete from the clip, such as a named entity, specific object or action, or a quoted phrase, matched against the transcript or entities. Reject "You won't believe what happened" patterns.
2. **Generic-hook filter:** compute embedding similarity against a bank of about 300 generic hooks and reject above a threshold.
3. **Truthfulness check:** a second, cheap LLM judgment confirms the hook doesn't claim anything the clip doesn't show. Misleading clickbait hurts retention and can breach platform policies.
4. **Real-person safety:** streamers and their guests are real people. The `controversial` style must frame debate ("Chat is split on this take") rather than allege wrongdoing. Block defamatory, harassing or sexualizing phrasing, and anything about minors.
5. **Curiosity gap:** score `spoiler_risk` and prefer hooks that tease the payoff without revealing it.

### 8.3 Timing and presentation

- Appears at frame 0, with a pop or slide-in of 120–180 ms. Default hold is about 2.5 s or until the payoff starts, whichever is first, then a 150 ms fade. Sits in the top hook zone (below the unsafe band), styled from the caption preset with a contrasting box option.
- Capitalization and emphasis rules follow the style preset: Title Case vs. ALL CAPS on emphasis words. Emoji is optional, at most 1 in the hook.
- Rendered through the same ASS pipeline (a separate `Hook` style), so it is editable in the same editor: text, timing handles, position drag.
- **Phase 5, "cold open":** prepend a 1–1.5 s teaser of the payoff frame or line, then cut back to the setup. This is a proven retention pattern. It is an EDL operation, so it composes with everything else.

### 8.4 Titles, descriptions, hashtags

One structured call per clip and platform:

- **YouTube:** title of 100 characters or fewer, search-oriented. Description with credit and source VOD link.
- **TikTok:** caption with 3–5 hashtags.
- **Instagram:** caption with hashtags.

Hashtags come from game, streamer, category and topic. Forbid spammy or irrelevant trending tags. Store them with the clip for batch export.

---

## 9. Rendering, batch export and platform presets

### 9.1 Edit decision list (the source of truth for a clip)

```json
{
  "source": {"vod_id": "…", "timebase": "1/1000"},
  "segments": [{"in_ms": 11520400, "out_ms": 11548900}, {"in_ms": 11549600, "out_ms": 11561200}],
  "layout_track": [{"from_ms": 0, "layout_id": "stacked_cam_top", "overrides": {}}],
  "captions": {"track_id": "…", "style_id": "bold-pop"},
  "hook": {"variant_id": "…", "overrides": {}},
  "audio": {"loudnorm_lufs": -14, "crossfade_ms": 15},
  "outputs": ["tiktok_9x16", "shorts_9x16", "reels_9x16", "square_1x1"]
}
```

Times are in **source time**. Multiple segments implement dead-space removal and cold opens. Every edit is a new immutable EDL version, which gives undo and history for free.

### 9.2 Render worker (GPU, FFmpeg)

1. Fetch only the source segments covering `[first_in − 2 s, last_out + 2 s]`: HLS segments or byte ranges of the remuxed mezzanine.
2. NVDEC decode. Build a filter graph:
   - `trim`/`atrim` plus `concat`, with 10–20 ms audio crossfades at cut points to avoid clicks
   - per region: `crop` (moving crops are driven by `sendcmd`, since the `crop` filter accepts x/y/w/h commands at runtime) → `scale` → `overlay`/`vstack` onto the canvas
   - blurred-background fill when needed
   - `ass=` captions plus hook
   - `loudnorm` (two-pass EBU R128 to about −14 LUFS integrated, −1 dBTP)
3. NVENC encode: H.264 High, 1080×1920, source fps capped at 60 (30 for TikTok-safe presets), ~10–16 Mbps VBR, AAC-LC 48 kHz 192 kbps, `+faststart`.
4. Upload to R2, write the `render` row, emit progress events. FFmpeg `-progress pipe:1` is parsed into percent.

**Expected speed:** a 45 s 1080×1920 clip renders in about 5–15 s wall time on an L4 including fetch. Ten clips × three formats run in parallel across GPUs in about 1–2 minutes total.

**Dead-space removal:** propose cuts where VAD shows no speech for more than 0.6 s *and* visual motion is low. Never cut gameplay action just because nobody is talking. Show the cuts as toggleable ranges, with a global "tightness" slider (0.4–1.5 s threshold).

### 9.3 Export presets (store as data; verify periodically)

| Preset | Canvas | Max length | Notes |
|---|---|---|---|
| TikTok | 1080×1920, 9:16 | Per creator: query `creator_info` (`max_video_post_duration_sec`) before posting | H.264, 30/60 fps |
| YouTube Shorts | 1080×1920 (or 1:1) | Up to 3 min | |
| Instagram Reels | 1080×1920 | ~3 min in app (**verify** API limit) | 4:5 (1080×1350) for feed |
| Square | 1080×1080 | n/a | X / Facebook / LinkedIn |
| Landscape | 1920×1080 | n/a | Compilations |
| Custom | any W×H | n/a | Layout engine works in normalized coords |

### 9.4 Direct publishing (Phase 4)

| Platform | API | Gating |
|---|---|---|
| TikTok | Content Posting API (Direct Post or Upload-to-Inbox) | **Unaudited apps can post only to private accounts**, with at most 5 posting users per 24 h. Public posting requires passing TikTok's audit. Creators are capped at about 15 posts/day, shared across all apps. |
| YouTube | `videos.insert` | Quota about 1,600 units per upload **(verify)**. Uploads stay private until the API project passes Google's audit. Request a quota increase. |
| Instagram | Graph API content publishing (`media_type=REELS`) | Business or Creator accounts only. Rolling 24-hour publishing cap: Meta's docs show 50 and 100 in different places, so **query `content_publishing_limit` at runtime**. |

Until audits pass, ship **"Download + copy caption"** and **"Send to TikTok inbox"** (draft) flows.

### 9.5 Cost model for one 6-hour VOD (estimates)

| Item | Basis | Estimate |
|---|---|---|
| ASR via API | 6 h × $0.15–0.26/hr | $0.90–1.60 |
| ASR self-hosted (alternative) | ~5 GPU-min on L4 | ~$0.05–0.15 |
| Audio events + prosody | ~3 GPU-min | ~$0.05 |
| Visual features (2 fps, low-res) | ~6 GPU-min | ~$0.10 |
| LLM transcript pass | ~80–100k input tokens (6 h ≈ 55k words) × Claude Opus 5.5 at $4/M in, ~$20/M out; cached rubric | ~$0.50–0.80 |
| LLM rerank (~60 candidates × ~10k tokens incl. images) | ~600k in / 60k out; Batch API halves it | ~$1.50–3.70 |
| Hooks, titles, cleanup (10 clips) | ~10 × 8k tokens | ~$0.40 |
| Rendering (10 clips × 3 formats) | ~5 GPU-min L4 | ~$0.10 |
| Storage and egress | R2 storage of renditions; no egress fees | cents/month |
| **Total** | | **≈ $2–6** (≈ $1.5–4.5 with self-hosted ASR) |

Rerank is the biggest lever. If unit costs ever matter, the options to evaluate *with quality measured against the eval set* are fewer candidates, fewer images, and Batch API for non-interactive runs.

---

## 10. Dashboard UX (paste → export)

1. **Paste or upload bar** on the home screen. The URL is parsed and resolved instantly (platform, title, duration, thumbnail from the official API). If ingest needs a connection or upload, the screen says so in one sentence with the action button.
2. **Analysis view**, with progress in stages: *Downloading audio → Transcribing (searchable now) → Listening for reactions → Reading chat → Watching gameplay → Ranking moments*. There is an ETA, and partial results appear as they land.
3. **Moments board:**
   - a ranked list of cards: thumbnail, timestamp, duration, category chip, score, the one-line *why* and evidence chips
   - a **VOD-wide heat timeline** (excitement curve, chat velocity, clip density, search hits) with brushing to find moments manually
   - multi-select with "Create 10 clips"
4. **Transcript and search panel:** keyword, semantic and chat search; click to seek; "make clip from selection" by highlighting transcript text.
5. **Clip editor** (one screen):
   - player with safe-zone overlay toggle
   - trimmer timeline with waveform, thumbnails, word strip and layout segments
   - side panels: Layout · Captions · Hook · Text/Title · Export
   - shortcuts: `Space` play/pause, `J/K/L` shuttle, `I/O` set in/out, `←/→` ±1 frame, `Shift+←/→` ±10 frames, `Alt+←/→` jump to previous/next word boundary, `[ ]` nudge selected edge, `X` toggle dead-space cut
   - **"Extend context" buttons:** +2 s / +5 s at the start and end, and "include the setup" (jump to the previous sentence boundary)
6. **Batch review:** a grid of all clips autoplaying muted on hover. Apply style, hook style, layout and preset to all or a selection. Approve or reject per clip. One "Export all (TikTok + Shorts + Reels)" button with per-render progress.
7. **Library:** clips grouped by source VOD, with source link, original timestamps, versions, renders, and publish status.

**Frame-accurate editing in the browser:**

- **Proxy:** 720p H.264 with a keyframe every 0.5 s (or all-intra for the clip window), so seeking is instant.
- **Frame display:** `requestVideoFrameCallback` gives exact presented frame times. Use WebCodecs `VideoDecoder` with an MP4 demuxer for true frame stepping where `<video>` seeking is imprecise.
- **Timeline:** canvas-rendered at 60 fps with waveform peaks from BBC `audiowaveform` JSON generated server-side.
- **Wide navigation:** full-VOD scrubbing uses the sprite sheets and the 144p analysis rendition, never the mezzanine.

---

## 11. Data model (Postgres)

```sql
channels(id, user_id, platform, platform_channel_id, display_name, oauth_ref, glossary jsonb, created_at)
channel_layout_profiles(id, channel_id, scene_type, layout_id, regions jsonb, overlay_signature bytea, confirmed_by_user bool, updated_at)

sources(id, user_id, channel_id, platform, url, platform_video_id, title, duration_ms,
        rights_basis text check (rights_basis in ('upload_attested','owner_oauth','live_capture','permission_attested')),
        rights_evidence jsonb, status, created_at)
assets(id, source_id, kind /* audio_16k, analysis_video, sprites, mezzanine_hls, proxy */, uri, meta jsonb)

analysis_runs(id, source_id, pipeline_version, model_versions jsonb, status, progress, started_at, finished_at)
transcript_segments(id, source_id, start_ms, end_ms, speaker, text, words jsonb, tsv tsvector, embedding vector(1024))
chat_stats(source_id, t_sec, msgs, uniq, emote_laugh, emote_hype, emote_shock, clipit, events jsonb)   -- per-second aggregate
-- raw chat + per-second feature timeline → Parquet in R2 (uri on analysis_runs)

moments(id, source_id, run_id, start_ms, end_ms, score, sub_scores jsonb, category, why text,
        evidence jsonb, rank int, status /* suggested, selected, dismissed */)
clips(id, user_id, source_id, moment_id, current_version int, title, created_at)
clip_versions(id, clip_id, version, edl jsonb, captions jsonb, hook jsonb, layout jsonb, metadata jsonb, created_at)
renders(id, clip_version_id, preset, status, progress, output_uri, duration_ms, error, created_at)
publications(id, render_id, platform, account_ref, remote_id, status, published_at, metrics jsonb)
feedback_events(id, user_id, entity, entity_id, type /* shown, selected, trim_delta, layout_override, caption_edit */, payload jsonb, at)
job_events(id bigserial, job_type, job_id, stage, progress, message, at)    -- SSE source
```

Indexes:

- `GIN(tsv)`
- `GIN(text gin_trgm_ops)`
- `ivfflat/hnsw(embedding)`
- `(source_id, start_ms)` on segments and moments
- partition `job_events` and `feedback_events` by month.

---

## 12. API surface (initial)

```
POST   /api/sources                 {url} | {upload_id}  → resolve, rights check, start workflow
GET    /api/sources/:id             status, progress, metadata
GET    /api/sources/:id/moments     ranked moments (+ ?category=, ?min_score=)
GET    /api/sources/:id/search      ?q=…&mode=keyword|semantic|chat
GET    /api/sources/:id/timeline    downsampled feature curves for heat timeline
POST   /api/clips/batch             {moment_ids[], defaults:{style_id, layout, hook_style, presets[]}} → creates clips + auto-edit workflows
GET    /api/clips/:id               current version + renders
PUT    /api/clips/:id/versions      new EDL/captions/layout/hook (optimistic concurrency on version)
POST   /api/clips/:id/hooks:regenerate {style?}
POST   /api/renders                 {clip_version_id, presets[]}
POST   /api/renders/batch           {clip_ids[], presets[]}
GET    /api/events?since=…          SSE stream of job_events for the user
POST   /api/uploads                 → tus / multipart init (signed R2 URLs)
POST   /api/connections/:platform   OAuth flows (Twitch, Kick, YouTube, TikTok, Meta)
```

---

## 13. Implementation roadmap

Assumes 2–3 engineers (1 frontend-leaning, 1–2 backend/ML). Each phase ships something usable.

### Phase 0: Foundations and decisions (1–2 weeks)
- Legal review: ingest policy (Section 1.4), model and dataset licenses (Section 7.5), ToS for each publishing API.
- **Evaluation dataset:** 20 labeled VODs (highlight spans, ideal in/out points, facecam boxes, scene types).
- Benchmark harness: ASR bake-off (AssemblyAI vs Deepgram vs Parakeet on your audio), timing and cost per VOD-hour.
- Infra skeleton: separate app/monorepo, Postgres, R2, Temporal namespace, Modal account, CI.

### Phase 1: "Upload → transcript → manual clip → export" (4–6 weeks)
*Delivers the editor and render quality everything else depends on.*
- Resumable upload. Ingest workflow: remux mezzanine, audio_16k, analysis rendition, sprites.
- ASR via the chosen API. Transcript storage, keyword search, click to seek.
- Trimmer with proxy generation, waveform, frame stepping, shortcuts and an EDL model.
- Layouts: `letterbox_blur`, static `stacked_cam_top` with a **manually drawn** facecam box, static center crop. Aspect presets 9:16 / 1:1 / 4:5 / 16:9.
- Captions: word-timed ASS generation, 3 style presets, word editor, JASSUB preview, safe-zone overlay.
- GPU render worker (FFmpeg/NVENC, loudnorm). Download export. SSE progress.
- **Exit criteria:** a non-expert can make a captioned 9:16 clip from a 4-hour upload in under 3 minutes, with no render/preview mismatch.

### Phase 2: "AI moment finder" (4–6 weeks)
- Audio events + prosody. Per-second feature timeline with robust normalization.
- Official signals: Twitch Get Clips density, markers, `muted_segments`. Chat-log import from file.
- Candidate generation (peaks + typed detectors + LLM transcript pass), boundary refinement, LLM rerank with explanations and evidence, MMR diversity.
- Moments board, heat timeline, semantic transcript search, batch "create clips".
- Feedback logging.
- **Exit criteria:** Precision@10 of at least 0.6 against eval-set human picks, and median trim delta under 3 s.

### Phase 3: "Auto-edit" (4–6 weeks)
- Scene-type classifier, auto facecam detection, **per-channel layout memory**, gameplay ROI crop, IRL face tracking with smoothed paths, layout switching with hysteresis, manual crop keyframes.
- LLM caption cleanup (alignment-safe), emphasis words, category-to-style matching, emoji option.
- Hooks (5 styles + guardrails), titles, descriptions, hashtags per platform.
- Dead-space removal. Batch review grid and batch export across formats.
- **Exit criteria:** layout override rate under 25% of clips, caption word-edit rate under 3%, and hook acceptance (unchanged or lightly edited) over 50%.

### Phase 4: "Live companion, link import, publishing" (4–8 weeks)
- Live companion: Twitch EventSub chat, Kick webhooks (signature verification, dedupe, re-subscribe monitor), YouTube `streamList`. Raw chat to Parquet, per-second stats.
- RTMP/SRT stream-copy ingest (MediaMTX) with auto-analysis when the stream ends: clips ready minutes after going offline.
- Link import adapters per platform **behind feature flags, per legal decision**, with rights checks via connected accounts.
- Direct publishing (TikTok inbox → Direct Post after audit; YouTube after audit; Instagram Reels). Scheduling.
- Performance ingestion (YouTube Analytics etc.) feeding `feedback_events`.

### Phase 5: "Learned and premium" (ongoing)
- LambdaMART ranker on accumulated labels, per-channel priors.
- Learned facecam detector, active-speaker split layouts, game-specific detectors (OCR kill feeds).
- Cold-open edits, B-roll and zoom punch-ins on emphasis, premium animated templates (Remotion), brand kits, team workspaces.

### Why this order
- **Editor and render first:** every AI feature outputs into them, users get value on day one, and it exposes output-quality problems early, when they are cheapest to fix.
- **Ranking second:** it needs only audio and a transcript, which Phase 1 already produces.
- **Reframing third:** it is the most model-heavy and benefits from Phase 1–2 manual-layout data.
- **Live and link ingest last:** they carry the most external dependency and legal risk. They should arrive once the core product is proven on uploads.

---

## 14. Quality, operations and risk

**Metrics dashboard:**

- analysis minutes per VOD-hour (p50/p95)
- time to first searchable transcript
- render seconds per clip
- cost per VOD-hour
- Precision@k
- accept rate
- trim delta
- layout override rate
- caption edit rate
- hook acceptance
- export success rate
- publish success rate

**Reliability:**

- Temporal retries with idempotent activities keyed by (run_id, chunk).
- Heartbeats on long GPU tasks.
- Poison-pill detection for corrupt sources (ffprobe validation at ingest).
- Per-user concurrency limits.
- Pipeline and model versions stored on every run so results are reproducible and can be reprocessed.

**Risks and mitigations:**

| Risk | Mitigation |
|---|---|
| Platform ToS or IP blocking on link import | Permissioned adapters first. Feature flags. `rights_basis` audit trail. No core feature depends on unofficial endpoints. |
| Copyrighted music (DMCA) in exports | Music detector warning. Respect `muted_segments`. Option to duck or replace music. |
| Defamatory or harmful auto-text about real people | Hook guardrails (Section 8.2). Human review before publish. Report flow. |
| Chat unavailable for most past VODs | Live companion. Twitch clip density as a crowd proxy. Fusion works without chat (weights renormalize). |
| ASR errors on names and slang | Channel glossary, keyterms, alignment-safe LLM cleanup, fast word editor. |
| Model licenses (non-commercial / AGPL) | License review gate before launch. Prefer Apache/MIT models (Section 7.5). |
| GPU cost spikes | Low-res analysis renditions, scale-to-zero, Batch API for non-interactive LLM work, per-plan quotas. |
| Sensitive or adult content | Content classifier flag on moments. Platform-policy-aware export warnings. |

---

## Sources

- Twitch: [Get Clips Download (open beta announcement)](https://discuss.dev.twitch.com/t/get-clips-download-twitch-api-endpoint-now-available-in-open-beta/64334) · [Twitch API change log (GA 2026-01-16)](https://dev.twitch.tv/docs/change-log/) · [Twitch API reference](https://dev.twitch.tv/docs/api/reference/) · [Clips docs](https://dev.twitch.tv/docs/api/clips/) · [TechCrunch: 100-hour highlights/uploads cap](https://techcrunch.com/2025/02/20/twitch-caps-streamers-storage-at-100-hours-of-highlights-and-uploads) · [Shacknews: deadline extended to May 2025](https://shacknews.com/article/143893/twitch-vod-limit-deadline-extended) · [ArchiveTeam: Twitch retention](https://wiki.archiveteam.org/index.php/Twitch)
- Kick: [KickDevDocs (official)](https://github.qingwei-s.workers.dev/KickEngineering/KickDevDocs) · [kickcom.py webhook setup](https://predaaa.github.io/kickcom.py/webhooks/setup/) · [kick-api Rust crate](https://docs.rs/crate/kick-api/0.1.8/source/README.md)
- YouTube: [liveChatMessages.streamList](https://developers.google.com/youtube/data/live/reference/rest/v3/liveChatMessages/streamList) · [liveChatMessages](https://developers.google.com/youtube/data/live/reference/rest/v3/liveChatMessages) · [Streaming live chat](https://developers.google.com/youtube/data/live/streaming-live-chat)
- TikTok: [Content Sharing Guidelines](https://developers.tiktok.com/doc/content-sharing-guidelines) · [Direct Post reference](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) · [Content Posting API get started](https://developers.tiktok.com/doc/content-posting-api-get-started)
- Instagram: [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) · [IG User Content Publishing Limit](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/content_publishing_limit)
- ASR: [Deepgram pricing](https://deepgram.com/pricing) · [Activepieces: Deepgram 2026 rates](https://www.activepieces.com/blog/deepgram-pricing-2026-per-minute-rates-and-add-ons.md) · [AssemblyAI pricing (blog)](https://assemblyai.com/blog/speech-to-text-api-pricing) · [AssemblyAI billing docs](https://www.assemblyai.com/docs/billing-and-pricing.md) · [Dupple: AssemblyAI 2026 pricing](https://dupple.com/learn/assemblyai-pricing) · [Parakeet-TDT-0.6B-v3 model card](https://build.nvidia.com/nvidia/parakeet-tdt-0_6b/modelcard) · [Parakeet-TDT collection (NGC)](https://catalog.ngc.nvidia.com/orgs/nvidia/-/collections/parakeet-tdt-0.6b/) · [Together AI: Parakeet v3](https://www.together.ai/models/parakeet-tdt-0-6b-v3-realtime)
- Video LLM: [Vertex AI generative AI pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) · [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) · [Gemini forum: video token math](https://discuss.ai.google.dev/t/gemini-live-2-5-token-counting-what-is-the-expected-cost-of-long-running-video-session/99245)
- Rendering: [Remotion pricing](https://www.remotion.dev/docs/pricing) · [Remotion license FAQ](https://www.remotion.dev/docs/license/faq)
- Claude API model IDs and pricing: Anthropic Claude API documentation (Claude Opus 5.5: $4 / $20 per million input/output tokens, 1M context).
