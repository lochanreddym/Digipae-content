# Digipae local-shop preview (30s, 9:16)

Audience: local shop owners. Goal: introduce Digipae and earn follows. Framing: product preview — never "available now".

## Status
Scenes 3–4, the end card, narration, captions, labels, sign graphic and soundtrack are final.
Scenes 1, 2 and 5 are illustrated stand-ins until the live-action clips are generated.

## Timeline (narration-driven, see `timing.json`)
| Time | Scene | Narration |
|---|---|---|
| 0–5 | 1 · box into bag, tilt up | You run the shop. Checkout shouldn't steal the spotlight. |
| 5–10 | 2 · sign placed (graphic composited) | Meet Digipae. Here's a preview of QR checkout for local shops. |
| 10–18 | 3 · Scan → Review → Confirm (conceptual demo) | A customer scans your code in Digipae, reviews the amount, and confirms with their wallet PIN. |
| 18–24 | 4 · merchant dashboard (conceptual demo) | The payment appears in your merchant dashboard, alongside your sales activity. |
| 24–26.3 | 5 · bag slides to customer | Built around everyday business. |
| 26.3–30 | End card | Follow Digipae for product updates. |

Scan/Review/Confirm switch on the words "scans", "reviews", "confirms"; PIN dots fill on "wallet PIN"; the dashboard row highlights on "appears".

## Generating the live-action clips (Higgsfield)
Cost at time of writing: reference image 0.25 credits; Seedance 2.0 5s 1080p 9:16 ≈ 60 credits per clip (std mode needs a Plus plan).
1. Reference image (`gpt_image_2_5`, 9:16): the shared visual direction + "owner and customer at the pale oak counter, kraft paper bag on the counter".
2. Clips (`seedance_2_0`, 9:16, 5s, 1080p, `generate_audio: false`, the reference image as `image_references`) with the three scene prompts from the brief and the shared negative prompt.
3. Save as `assets/scene1.mp4`, `assets/scene2.mp4`, `assets/scene5.mp4`.

## Swapping footage in
In `templates/index.html.tmpl`, replace the contents of `#set1`, `#set2`, `#set5` with
`<video src="assets/sceneN.mp4" muted playsinline data-start="…" data-duration="…" style="width:100%;height:100%;object-fit:cover"></video>`
(scene 1: start 0; scene 2: start 4.85; scene 5: start 23.85). Keep the sign graphic (`.sign .face`) for scene 2 and
position it over the blank sign once its on-screen corners are known. Then `python3 build.py production/timing.json` and render.

## Rebuild audio
`python3 production/shop_audio.py production/timing.json <dir with l1..l5.wav> assets/mix.wav` (95 BPM electric piano bed, foley, -14 LUFS).
