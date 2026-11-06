# DigiPae Deck — Sources and Assumptions

Every number in the deck traces to a row below. Re-check each source before external use; dates are as of November 2026.

## Problem and impact (slide 3)

| Claim in deck | Source | Notes |
|---|---|---|
| ≈ 2 in 3 Medicaid disenrollments in the final month of the 2023–24 unwinding were procedural | KFF, [How Did Medicaid Renewal Outcomes Change During the Unwinding?](https://www.kff.org/medicaid/how-did-medicaid-renewal-outcomes-change-during-the-unwinding/) | Procedural share fell from 74% (month 1) to 66% (month 12). KFF's tracker was last updated September 12, 2024. |
| Benefit programs require similar types of information about individuals | GAO, [GAO/HEHS-00-119](https://www.gao.gov/products/hehs-00-119) (2000) | Older report; used for a structural point, not a current statistic. |
| Agencies increasingly use electronic data for verification; GAO recommended more data-source information sharing | GAO, [GAO-21-183](https://www.gao.gov/products/GAO-21-183) (2021) | Speaker notes only. |
| 10.5 billion hours of federal paperwork burden, FY2023 | OMB annual burden report, as reported by [CEI](https://cei.org/blog/from-cuts-to-costs-why-federal-paperwork-keeps-piling-up/) | Government-wide, mostly tax. Used for scale, not market sizing. Confirm against the OMB report itself before external use. |
| WIC served an estimated 53.5% of eligible people in 2022 | USDA FNS, [WIC Eligibility and Program Reach, 2022](https://www.fns.usda.gov/research/wic/eer/2022) | 2023 estimate: 56.1%. |

## Market sizing (slide 9, appendix B)

| Segment | Count | Source |
|---|---|---|
| HRSA-funded community health center awardees | 1,359 | [HRSA UDS national overview](https://data.hrsa.gov/topics/healthcenters/uds/overview/national) (2024 reporting) |
| Medicaid managed-care organizations | 291 | [KFF, Total Medicaid MCOs](https://www.kff.org/medicaid/state-indicator/total-medicaid-mcos/) (July 1, 2024) |
| Community action agencies | ~1,000 | [Community Action Partnership](https://communityactionpartnership.com/impactreport/) |
| 211 agencies | 200+ | [211.org, About](https://www.211.org/about-us) |
| LSC-funded legal aid organizations | 131 | [LSC, 2023 By the Numbers](https://www.lsmo.org/sites/lsmo.org/files/LSC%202023%20By%20The%20Numbers.pdf) |
| Benefits-technology platforms | To confirm | Needs customer research |

**Assumptions (not observed prices):**
- **ACVs:** $12K for community nonprofits (community action agencies, 211, legal aid), $24K for health centers, $150K for Medicaid plans.
- **TAM** ≈ $92.2M: 1,359 × $24K + 291 × $150K + 1,000 × $12K + 200 × $12K + 131 × $12K.
- **SAM** ≈ $48.6M: everything except Medicaid plans, which have longer sales cycles (2,690 orgs).
- **SOM** ≈ $0.9M ARR: 50 customers within 36 months × $18K blended ACV.
- **Next step:** replace every ACV with discovery data, and add the benefits-technology count.

## Competitive landscape (slide 10)

Each focus description summarizes the company's own public materials. The deck makes no claims about what any company lacks.

| Company | Evidence for the focus described |
|---|---|
| Truv | [Government verification overview](https://docs.truv.com/government/overview): consumer-permissioned income, employment and asset verification for SNAP, TANF, Medicaid, housing and child care |
| Equifax The Work Number | [Equifax newsroom](https://www.equifax.com/newsroom/all-news/-/story/streamlining-government-assistance-how-the-work-number-supports-more-efficient-benefits-determinations): employment and income verification for benefits determinations |
| Propel | [How Propel works](https://www.propel.app/snap/what-is-the-propel-app-how-does-it-work/): connects to state EBT portals with user permission |
| Login.gov, ID.me, Socure, Persona, Code for America, Nava PBC, Plaid | Well-known public positioning; confirm the one-line descriptions against each company's site before external use |
| Benefits Data Trust | Closed in August 2024 ([Inquirer](https://www.inquirer.com/health/benefits-data-trust-closing-august-23-20240823.html)); mentioned in speaker notes only |

## Things the deck deliberately does not claim

- Any affiliation with Plaid. "Plaid for government" is an analogy only.
- Live government integrations, agency partnerships, or universal data access.
- That a user's consent alone grants a right to access government data.
- Customers, pilots, revenue, pricing, or production readiness.
- Founder credentials, prior employers, or education.
- That CEIVIS, Inc. exists. The operating company is shown as CEIVIS LLC.
