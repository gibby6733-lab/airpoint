"""Split collage images into a background plate + cut-out elements (for the 'assemble' style).

usage: python3 mafia/build_layers.py <story_dir>
Reads <story_dir>/images/*.jpg|png. The shared background is estimated as the per-pixel median of all images
(the collages share one paper/newspaper plate). For each image, pixels that differ from that median form the
elements; each connected region becomes one cut-out PNG. Plate + elements re-composite to the original exactly.
Writes <story_dir>/images/layers/<n>_plate.png, <n>_e<k>.png and <story_dir>/layers.json.
"""
import json, os, sys
import cv2
import numpy as np

d = sys.argv[1]
src = sorted(f for f in os.listdir(os.path.join(d, "images")) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
os.makedirs(os.path.join(d, "images", "layers"), exist_ok=True)
imgs = [cv2.imread(os.path.join(d, "images", f), cv2.IMREAD_COLOR) for f in src]
H0, W0 = imgs[0].shape[:2]
# work at video resolution (1080 wide): keeps the renderer's memory small
TW = 1080; H0, W0 = int(round(H0 * TW / W0)), TW
imgs = [cv2.resize(im, (W0, H0), interpolation=cv2.INTER_AREA) for im in imgs]
small = [cv2.resize(im, (W0 // 4, H0 // 4), interpolation=cv2.INTER_AREA).astype(np.int16) for im in imgs]
# background families: split the sequence where the border region jumps, then use a sliding-window median
def edge(a):
    t = cv2.resize(a.astype(np.uint8), (48, 86), interpolation=cv2.INTER_AREA).astype(float)
    return np.concatenate([t[:12].ravel(), t[-10:].ravel(), t[:, :6].ravel(), t[:, -6:].ravel()])
E = [edge(a) for a in small]
group = [0]
for i in range(1, len(small)):
    group.append(group[-1] + (1 if np.abs(E[i] - E[i - 1]).mean() > 30 else 0))
def bg_for(i, win=3):
    idx = [j for j in range(max(0, i - win), min(len(small), i + win + 1)) if group[j] == group[i]]
    if len(idx) < 3:  # too few neighbours share this background: let the caller fall back to scrap assembly
        return None
    return np.median(np.stack([small[j] for j in idx]), axis=0).astype(np.int16)

MAX_EL = 9
out = {"size": [W0, H0], "shots": {}}
for i, (f, im, sm) in enumerate(zip(src, imgs, small)):
    median = bg_for(i)
    base = os.path.splitext(f)[0]
    fname = f"layers/{base}_full.jpg"; cv2.imwrite(os.path.join(d, "images", fname), im, [cv2.IMWRITE_JPEG_QUALITY, 92])
    if median is None:
        out["shots"][f] = {"mode": "scraps", "full": fname}; print(f, "scraps (no shared background)"); continue
    median_full = cv2.resize(median.astype(np.uint8), (W0, H0), interpolation=cv2.INTER_CUBIC)
    diff = np.abs(sm - median).max(axis=2).astype(np.uint8)
    diff = cv2.GaussianBlur(diff, (5, 5), 0)
    m = (diff > 34).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # fill holes inside elements
    ff = m.copy(); h, w = ff.shape; cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 1)
    m = m | (1 - ff)
    m = cv2.dilate(m, np.ones((5, 5), np.uint8))           # keep edges/shadows with the element
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    comps = [(i, stats[i, cv2.CC_STAT_AREA]) for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] > 0.004 * h * w]
    comps.sort(key=lambda c: -c[1])
    # merge the smallest into one last group if there are too many
    groups = [[c[0]] for c in comps[:MAX_EL - 1]] + ([[c[0] for c in comps[MAX_EL - 1:]]] if len(comps) >= MAX_EL else [])
    full_mask = np.zeros((H0, W0), np.float32)
    els = []
    for k, g in enumerate(groups):
        gm = np.isin(lab, g).astype(np.uint8) * 255
        gm = cv2.resize(gm, (W0, H0), interpolation=cv2.INTER_LINEAR)
        gm = cv2.GaussianBlur(gm, (5, 5), 0).astype(np.float32) / 255
        full_mask = np.maximum(full_mask, gm)
        ys, xs = np.where(gm > 0.02)
        x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rgba = np.dstack([im[y0:y1, x0:x1], (gm[y0:y1, x0:x1] * 255).astype(np.uint8)])
        name = f"layers/{base}_e{k}.png"; cv2.imwrite(os.path.join(d, "images", name), rgba)
        els.append({"file": name, "x": int(x0), "y": int(y0), "w": int(x1 - x0), "h": int(y1 - y0), "area": float(gm.sum())})
    # plate: original where no element, shared median background where elements sit
    # fill element areas from this image's own surrounding paper (no ghosts from other images)
    q = 4; ms = cv2.resize((full_mask > .02).astype(np.uint8) * 255, (W0 // q, H0 // q), interpolation=cv2.INTER_NEAREST)
    ms = cv2.dilate(ms, np.ones((7, 7), np.uint8))
    fill = cv2.inpaint(cv2.resize(im, (W0 // q, H0 // q), interpolation=cv2.INTER_AREA), ms, 9, cv2.INPAINT_TELEA)
    fill = cv2.resize(fill, (W0, H0), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    fill += np.random.default_rng(1).normal(0, 6, fill.shape[:2])[..., None]          # paper grain so it isn't smeary
    a = cv2.GaussianBlur(full_mask, (9, 9), 0)[..., None]
    plate = np.clip(im.astype(np.float32) * (1 - a) + fill * a, 0, 255).astype(np.uint8)
    pname = f"layers/{base}_plate.jpg"; cv2.imwrite(os.path.join(d, "images", pname), plate, [cv2.IMWRITE_JPEG_QUALITY, 92])
    # hero first (largest), then the rest from top/back to bottom/front
    hero, rest = els[:1], sorted(els[1:], key=lambda e: e["y"] + e["h"])
    cov = float(full_mask.mean())
    if cov > 0.6 or not els:   # one big piece or no clean split -> torn-scrap assembly instead
        out["shots"][f] = {"mode": "scraps", "full": fname}; print(f, "scraps (coverage %.0f%%)" % (100 * cov)); continue
    out["shots"][f] = {"mode": "assemble", "plate": pname, "elements": hero + rest, "full": fname}
    print(f, "elements:", len(els), "coverage %.0f%%" % (100 * cov))
json.dump(out, open(os.path.join(d, "layers.json"), "w"), indent=1)
