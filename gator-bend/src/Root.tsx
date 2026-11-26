import React from "react";
import { Composition } from "remotion";
import { DURATION, Episode, FPS } from "./Episode";

export const Root: React.FC = () => (
  <Composition id="Episode" component={Episode} durationInFrames={DURATION} fps={FPS} width={1080} height={1920} />
);
