# DigiPae Investor Pitch Deck

Pre-seed deck positioning DigiPae as the connectivity layer for government services ("Plaid for government", used as an analogy only).

## Deliverables

| File | What it is |
|---|---|
| `DigiPae_Investor_Deck.pptx` | 13-slide investor deck plus 2 appendix slides. Editable; speaker notes on every slide |
| `DigiPae_Investor_Deck.pdf` | PDF of the same deck |
| `DigiPae_YC_7-Slide.pptx` / `.pdf` | 7-slide YC-style version: cover, problem, solution, progress, market, team, ask |
| `Founder_Pitch_Scripts.md` | 90-second founder pitch and 3-minute presentation script |
| `Sources_and_Assumptions.md` | Every statistic, count, and assumption with its source, plus what the deck deliberately does not claim |
| `build/build_deck.cjs` | Generator for both decks (pptxgenjs) |

## How the deck was shaped

Research before writing:

- **Structure:** follows the sequence common to YC's seed-deck guidance and Sequoia's business-plan outline: problem, why it matters, solution, product, business model, market, competition, traction, team, ask. Sources: [YC library](https://ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck); summaries via [The Venture Crew](https://theventurecrew.substack.com/p/y-combinator-guide-how-to-build-your) and [Alexander Jarvis](https://www.alexanderjarvis.com/sequoia-capital-business-plan-template/). YC's site was not reachable from the build environment, so its guidance was taken from these summaries.
- **Patterns from decks that raised:**
  - YC's principles of legibility, simplicity, and obviousness, with every title written as a standalone sentence.
  - Airbnb's seed deck: one idea per slide and big-number callouts ([CB Insights](https://www.cbinsights.com/blog/billion-dollar-startup-pitch-decks)).
  - Front: a sharply defined niche inside a crowded category ([Business Insider](https://www.businessinsider.in/pitch-deck-library-here-are-the-pitch-decks-that-helped-hot-startups-raise-millions/articleshow/68803419.cms)).
  - Pre-seed decks lean on problem and team because traction is thin, so traction here is honest placeholders, not inflated numbers.
- **Market:** sized bottom-up (organizations × ACV), as YC-style guides recommend, from dated public counts.

**Design system:**
- Midnight navy `#081522`, deep blue `#10263B`, electric cyan `#37D5E8`, cool gray `#A4B4C3`, teal used sparingly.
- Inter, oversized sentence-style headlines, and one grid with 0.7" margins.
- Status pills (Prototype / In development / Planned) and amber "To confirm" placeholders.

## Before sharing: fill these in

- **Slide 6:** confirm each component's status label.
- **Slide 9:** benefits-technology platform count, plus real ACVs from discovery.
- **Slide 11:** traction numbers (discovery calls, design partners/LOIs, prototype users, waitlist) and the design-partner target.
- **Slide 12:** founder role and background, cofounder name, role and background, and the founders' own "why us" story.
- **Slide 13:** raise amount, instrument, runway, use-of-funds split, and founder email.
- **Slide 8:** price points.
- **Sources:** re-check the OMB 10.5B-hour figure against OMB's report, and the competitor one-liners against each company's site.

Inter must be installed for the PPTX to look exactly like the PDF; PowerPoint substitutes a similar font otherwise. Inter is free at rsms.me/inter.

## Rebuild

```bash
npm install pptxgenjs@3.12.0 react-icons@5.4.0 react@18.3.1 react-dom@18.3.1 sharp@0.33.5   # in a folder outside this repo
cp build/build_deck.cjs build/digipae-icon.png <that folder>/
cd <that folder> && node build_deck.cjs /path/to/pitch-deck
```
