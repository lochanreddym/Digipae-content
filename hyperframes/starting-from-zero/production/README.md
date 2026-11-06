# DigiPae — "Stop starting from zero" (Reel, 9:16, 50s)

Positioning: building toward "Plaid for government". Never implies live government integrations:
every concept screen carries **CONCEPT PREVIEW**, scene 6 carries "Future concept — government integrations not live",
and the end card carries "Future vision. Government data integrations are not live yet." Services are labelled as examples;
no seals, agency logos, uniforms or real program interfaces. Purple data lines move only after the user approves.

| Time | Scene | Beat anchored to |
|---|---|---|
| 0–5.7 | Problem: pen → keyboard → ID → another form | "service", "asked", "information" |
| 5.7–9.7 | Repetition: IDENTITY → ADDRESS → INCOME → DOCUMENTS ×3, clicks, then silence | each spoken label |
| 10.2–15.3 | Navy reveal, "What if government data could work more like Plaid?", consent request | "consent-based" |
| 15.3–19.8 | Toggle off unneeded data, press-and-hold "Approve sharing", lines move after release | "requested", "decide", "shared" |
| 19.8–27.5 | Verify once / reuse with permission network | "verified", "reused", "choose" |
| 27.5–33.2 | Document retrieval (future concept), purple tunnel after approval | "retrieving", "permission" |
| 33.2–39.8 | Possible programs → "May match your information" → what you may need | "programs", "situation", "need" |
| 39.8–45.5 | People ↔ DigiPae ↔ Public Services; Consent / Verified Data / Document Access / APIs | "infrastructure" |
| 45.5–50 | Cream end card, CTA "Follow the build →", purple pulse | "Plaid" |

Pipeline: `zero_tts.py` (Kokoro af_heart, ASR-verified) → `words.py` → `zero_timing.py` → `zero_audio.py` (score, SFX, -14 LUFS)
→ `python3 build.py production/timing.json` → `npx hyperframes render`.
Live-action version: scenes 1, 3, 4 and 5 call for an actor; drop generated clips into the matching scene containers when footage exists.
