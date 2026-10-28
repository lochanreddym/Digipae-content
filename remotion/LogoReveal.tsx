import { AbsoluteFill, Easing, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

// Digipae brand intro: icon springs in, wordmark rises underneath.
export const LogoReveal = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = spring({ frame: frame - 3, fps, config: { damping: 12 } });
  const word = interpolate(frame, [18, 33], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });

  return (
    <AbsoluteFill style={{ background: "#FEF7FE", alignItems: "center", justifyContent: "center", fontFamily: "Inter, sans-serif" }}>
      <Img src={staticFile("digipae-logo.png")} style={{ width: 520, transform: `scale(${0.6 + 0.4 * scale})`, opacity: Math.min(1, scale * 1.5) }} />
      <div style={{ fontSize: 132, fontWeight: 700, color: "#1E1650", opacity: word, transform: `translateY(${36 * (1 - word)}px)` }}>Digipae</div>
    </AbsoluteFill>
  );
};
