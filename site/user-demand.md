# Inference Demand Dashboard

- Updated on: **2026-03-30**
- Standard metric: **Total processed tokens**

A practical framework for estimating how inference demand scales from individual users and mapping the value chain winners.

## Headline Metrics

- **OpenRouter monthly tokens**: 30T — Current platform-wide monthly volume on OpenRouter's public rankings/state-of-AI pages.
- **Gemini monthly tokens**: 980T+ — Google said Gemini was processing more than 980 trillion monthly tokens by July 2025.
- **OpenAI daily messages**: 2.63B — OpenAI research reported 2.627 billion daily ChatGPT messages in June 2025.
- **OpenAI weekly users**: 800M+ — OpenAI said ChatGPT had more than 800 million weekly users by November 2025.

## Comparable Demand Tape

### OpenRouter
- Standardized lens: **30T monthly tokens**
- Evidence type: Direct tokens
- WoW: Starts once snapshot archive is live
- MoM: Starts once monthly archive is live
- YoY: n/a
- Confidence: **high**
- Notes: Best transparent marketplace tape, but not the whole industry.

### Google / Gemini
- Standardized lens: **980T+ monthly tokens**
- Evidence type: Direct reported tokens
- WoW: n/a
- MoM: +104% versus May 2025
- YoY: +4,849% versus May 2024
- Confidence: **high**
- Notes: Cleanest big-lab token disclosure currently available.

### OpenAI / ChatGPT
- Standardized lens: **~79T monthly token-equivalent (base case)**
- Evidence type: Estimated from message volume
- WoW: n/a
- MoM: +20% versus July 2025 daily messages
- YoY: +482% versus June 2024 daily messages
- Confidence: **medium**
- Notes: Direct token disclosure is sparse, so scale is inferred from messages and users.

### Anthropic / Claude
- Standardized lens: **>=8.8T monthly floor**
- Evidence type: OpenRouter floor plus official proxies
- WoW: Pending archive
- MoM: n/a
- YoY: n/a
- Confidence: **low-to-medium**
- Notes: Likely much larger in reality, but first-party total token figures are not public.

## Tracking Cadence

### Weekly
- Focus: OpenRouter live tape
- Coverage: Top models, author share, top apps, and total marketplace token flow
- Status: **Live now**

### Monthly
- Focus: Direct provider token and throughput disclosures
- Coverage: Gemini monthly tokens, OpenRouter monthly totals, any new lab token disclosures
- Status: **Partial coverage**

### Quarterly
- Focus: Users, seats, customers, capex, and revenue read-throughs
- Coverage: OpenAI users and seats, hyperscaler capex, cloud AI monetization signals
- Status: **High-value proxy layer**

### Annual
- Focus: Economic-index and research datasets
- Coverage: OpenAI usage papers, Anthropic Economic Index, marketplace retrospectives
- Status: **Context and calibration**

## Metric Stack

### Direct processed tokens
- Importance: **Best**
- Closest to actual inference compute served. Prefer monthly or weekly totals from provider disclosures or marketplace rankings.

### Token throughput
- Importance: **Best when totals are absent**
- Useful when companies publish tokens per minute or similar throughput rates instead of period totals.

### Messages or requests
- Importance: **Proxy**
- A strong demand read-through when token totals are not available, but requires a token-per-message assumption.

### Users, seats, and customers
- Importance: **Adoption**
- Shows how broadly inference products are diffusing across consumer and enterprise surfaces.

### Revenue, capex, and utilization
- Importance: **Economic confirmation**
- Confirms that token growth is translating into spending power and infrastructure demand.

## Provider Scorecards

### OpenRouter
- Confidence: **high**
- Measurement: Direct tokens and model-level weekly usage
- Headline: Weekly token volumes by model and app are publicly visible.
- Current metric: Public monthly volume = 30T (2026-03-30; Need weekly snapshots to compute platform WoW and MoM cleanly.)
- 2025-11-30: Study dataset size = 100T+ tokens over 13 months (n/a)
- 2026-03-30: Public monthly volume = 30T (n/a)
- 2026-03-30: Tracked user base = 5M+ users (n/a)
- Best publicly accessible weekly token leaderboard across frontier and open models.
- Useful as a live inference-demand tape even though it represents marketplace traffic rather than the whole industry.
- Can support true WoW and MoM growth tracking once we start persisting snapshots.

### Google / Gemini
- Confidence: **high**
- Measurement: Direct tokens, token throughput, MAU, and developer adoption
- Headline: Google is the cleanest big-lab source for direct token throughput disclosures.
- Current metric: Direct API throughput = 10B tokens/min (2026-02-04; +42.9% versus 7B tokens/min in Q3 2025.)
- 2024-05-14: Monthly tokens processed = 9.7T (Baseline)
- 2025-05-20: Monthly tokens processed = 480T+ (+4,849% YoY versus May 2024)
- 2025-07-23: Monthly tokens processed = 980T+ (+104% versus May 2025)
- 2025-10-29: Direct API throughput = 7B tokens/min (Baseline for Q3 2025)
- 2026-02-04: Direct API throughput = 10B tokens/min (+42.9% versus Q3 2025)
- 2025-05-20: Gemini app MAU = 400M+ (Baseline)
- 2025-10-29: Gemini app MAU = 650M+ (+62.5% versus May 2025)
- 2026-02-04: Gemini app MAU = 750M+ (+15.4% versus Q3 2025)
- Google gives the strongest first-party token metrics among the major labs.
- The jump from 9.7T to 480T+ to 980T+ monthly tokens is one of the clearest public inference-demand curves in the market.
- Direct API throughput and MAU let us separate developer demand from consumer adoption.

### OpenAI / ChatGPT
- Confidence: **medium**
- Measurement: Messages, users, seats, and estimated token-equivalent throughput
- Headline: OpenAI discloses scale through message counts and user growth more than token totals.
- Current metric: Weekly users = 800M+ (2025-11-05; +14.3% versus 700M+ by July 2025.)
- 2024-06-26: Daily ChatGPT messages = 451M (Baseline)
- 2025-06-26: Daily ChatGPT messages = 2.627B (+482% YoY)
- 2025-07-22: Daily messages across OpenAI tools = 2.5B+ (In line with June 2025 research)
- 2025-08-01: Daily messages globally = 3B (+20% versus July 2025)
- 2025-07-01: Weekly active users = 700M+ (Baseline)
- 2025-11-05: Weekly active users = 800M+ (+14.3% versus July 2025)
- 2025-11-05: Paid business customers = 1M+ (n/a)
- 2025-11-05: ChatGPT for Work seats = 7M+ (n/a)
- Estimated token-equivalent range: low 0.79T / day, base 2.63T / day, high 3.94T / day
- OpenAI is enormous on user and message volume, but still relatively sparse on direct token-throughput disclosures.
- Message growth and seat growth make OpenAI one of the best demand proxies even when the token math must be estimated.
- The token-equivalent range is directionally useful for comparing scale with disclosed token metrics from Google and OpenRouter.

### Anthropic / Claude
- Confidence: **low-to-medium**
- Measurement: Usage-composition proxies and marketplace token floors
- Headline: Anthropic publishes strong usage-quality data, but not direct system-wide token totals.
- Current metric: OpenRouter floor = 2.03T/week (2026-03-30; Observed from Claude Sonnet 4.6 plus Claude Opus 4.6 on OpenRouter rankings.)
- 2025-02-10: Occupations with AI use in at least 25% of tasks = 36% (Baseline)
- 2025-02-10: Occupations with AI use in at least 75% of tasks = 4% (Baseline)
- 2025-02-10: Augmentation share = 57% (Baseline)
- 2025-02-10: Automation share = 43% (Baseline)
- 2026-01-15: Economic Index dataset cadence = Millions of anonymized Claude conversations (Longitudinal tracking, not token totals)
- Anthropic is excellent for seeing what Claude is used for, especially the shift toward coding and enterprise automation.
- For total-demand sizing, Anthropic needs to be treated as a partial-information case.
- The best near-term approach is to track Claude's OpenRouter token floor and pair it with Anthropic's official Economic Index updates.

## OpenRouter Live Tape

- Model #1: MiMo-V2-Pro (xiaomi) — 4.19T, +112%
- Model #5: Claude Sonnet 4.6 (anthropic) — 1.04T, +1%
- Model #6: Claude Opus 4.6 (anthropic) — 987B, 0%
- Model #7: Gemini 3 Flash Preview (google) — 976B, +5%
- Model #10: Grok 4.1 Fast (x-ai) — 628B, +33%

## User-Level Demand Framing

### Knowledge workers (copilot usage)
- Today: ~5k-20k tokens/user/day equivalent
- 2-year view: ~50k-250k tokens/user/day as copilots become always-on
- Notes: Driven by draft/rewrite/search workflows, meeting copilots, and agent handoffs.

### Analysts & developers (heavy users)
- Today: ~50k-300k tokens/user/day
- 2-year view: ~0.5M-3M tokens/user/day with agent loops and code/test automation
- Notes: Reasoning chains plus tool-calling can increase inference per task by 5-20x.

### Personal assistant consumers
- Today: ~1k-10k tokens/user/day for chat-style interactions
- 2-year view: ~20k-150k tokens/user/day with voice, memory, and multimodal assistants
- Notes: Ambient assistant patterns can create many low-latency sessions throughout the day.

## Practical Proxies

- **Model API revenue growth and token disclosures**: Direct read-through for paid inference demand and pricing trends.
- **Hyperscaler AI capex plus inference commentary**: If inference is scaling faster than efficiency gains, infra spend remains elevated.
- **Enterprise seat penetration of AI copilots**: Seat growth is the cleanest adoption proxy for knowledge-worker demand.
- **GPU cloud utilization / spot pricing**: Tight utilization indicates sustained demand at current supply.
- **Utility and grid interconnection disclosures tied to data centers**: Second-order validation that compute demand is persisting physically.

## Beneficiary Stack

- **Model + platform companies**: OpenAI ecosystem, Anthropic ecosystem, hyperscaler model platforms — Capture usage revenue first, but margins depend on inference efficiency and distribution strength.
- **Compute and networking suppliers**: NVIDIA, AMD, Broadcom, Arista, optics suppliers — Benefit when token demand growth outpaces cost/token declines.
- **Power and thermal infrastructure**: Vertiv, Eaton, Trane and electrical chain — Monetize the physical bottlenecks needed to serve larger inference loads.
- **Application wrappers and workflow incumbents**: Microsoft, Google, Salesforce, ServiceNow, vertical SaaS leaders — Win where distribution and workflow integration convert inference into sticky ARR.
- **Second-order grid and industrial beneficiaries**: Utilities, generation, transmission, engineering services — Upside appears with lag but can persist if AI demand translates into long-cycle capex.

## Sources

- [OpenRouter rankings](https://openrouter.ai/rankings)
- [OpenRouter State of AI](https://openrouter.ai/state-of-ai)
- [Google I/O 2025 keynote recap](https://blog.google/technology/ai/io-2025-keynote/)
- [Alphabet Q3 2025 message from the CEO](https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q3-2025/)
- [Alphabet Q4 2025 message from the CEO](https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q4-2025/)
- [ChatGPT usage and adoption patterns at work](https://cdn.openai.com/pdf/a253471f-8260-40c6-a2cc-aa93fe9f142e/economic-research-chatgpt-usage-paper.pdf)
- [How people use ChatGPT](https://cdn.openai.com/pdf/3c7f7e1b-36c4-446b-916c-11183e4266b7/chatgpt-usage-and-adoption-patterns-at-work.pdf)
- [One million business users](https://openai.com/index/one-million-business-users/)
- [The Anthropic Economic Index](https://www.anthropic.com/news/the-anthropic-economic-index/)
- [Anthropic Economic Index hub](https://www.anthropic.com/economic-index/)
