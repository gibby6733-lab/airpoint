import React from "react";
import { AbsoluteFill, Composition, Sequence } from "remotion";
import { DURATION, FPS, Scene } from "./Episode";
import { INTRO_FRAMES, Intro } from "./Intro";

// The full episode: opening titles, then the scene.
const Full: React.FC = () => (
  <AbsoluteFill>
    <Sequence durationInFrames={INTRO_FRAMES}>
      <Intro />
    </Sequence>
    <Sequence from={INTRO_FRAMES}>
      <Scene />
    </Sequence>
  </AbsoluteFill>
);

export const Root: React.FC = () => (
  <>
    <Composition id="Episode" component={Full} durationInFrames={INTRO_FRAMES + DURATION} fps={FPS} width={1080} height={1920} />
    <Composition id="Intro" component={Intro} durationInFrames={INTRO_FRAMES} fps={FPS} width={1080} height={1920} />
    <Composition id="Scene" component={Scene} durationInFrames={DURATION} fps={FPS} width={1080} height={1920} />
  </>
);
