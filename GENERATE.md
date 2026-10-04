# Daily generation instructions

The 8:00 AM IST scheduled task follows these steps every day. They live in the repo so the routine can be refined without recreating the task.

## 1. Get context
- Today's date in IST (Asia/Kolkata) is the quiz date — `YYYY-MM-DD`.
- If `quizzes/<date>.json` already exists, stop: today is done.
- Read `ledger/asked.jsonl`. Every line is a question already asked (`date`, `topic`, `concept`, `question`). **Never repeat a concept or re-word an old question.** Prefer topics and concepts that have appeared least.

## 2. Research what's current (for the news questions)
Use web search for the last ~2 weeks of product-management and AI-product news: model/platform launches, notable product decisions, pricing changes, regulation (EU AI Act, India DPDP rules), commerce/messaging platform changes (WhatsApp Business, Shopify). Only use facts you can confirm from the sources; record a `source` URL on those questions.

## 3. Write 30 questions to `drafts/<date>.json`
Same shape as `drafts/2026-10-04.json`:

```json
{"date": "YYYY-MM-DD", "theme": "Short day theme", "questions": [
  {"topic": "...", "concept": "short unique tag", "difficulty": "easy|medium|hard",
   "question": "...", "options": ["A","B","C","D"], "answer": 0,
   "explanation": "Why the correct answer is right (2-4 sentences, teach the idea)",
   "rationales": ["why option A is right/wrong", "...B", "...C", "...D"],
   "source": "https://... (only for news questions)"}
]}
```

Mix for each day (30 total):
| Topic | Count |
|---|---|
| Strategy (vision, positioning, moats, business models, competitive analysis) | 3 |
| Discovery & research (interviews, JTBD, OST, validation, personas) | 3 |
| Prioritization & frameworks (RICE, ICE, Kano, MoSCoW, opportunity scoring, cost of delay) | 2 |
| Metrics & analytics (North Star, funnels, cohorts, SQL-literate thinking, unit economics) | 3 |
| Experimentation (A/B design, stats pitfalls, interpreting results) | 2 |
| Execution & delivery (agile, specs/PRDs, roadmaps, launches, incidents) | 3 |
| Stakeholders & leadership (alignment, influence, conflict, communication) | 2 |
| Day-to-day scenarios (realistic "what do you do" situations) | 3 |
| AI product management (LLMs, evals, RAG, agents, cost/latency, safety, ML metrics) | 4 |
| Technology for PMs (APIs, webhooks, architecture, data, security, mobile) | 2 |
| Growth, GTM & pricing | 2 |
| Current events in product/AI (from step 2) | 1 |

Rules:
- Difficulty mix: about 10 easy, 13 medium, 7 hard. Scenario questions should be the hard ones.
- Exactly one defensibly correct answer. Distractors must be plausible — common misconceptions, not jokes.
- Every rationale explains *why* that option is right or wrong, so a wrong pick teaches something.
- No "all of the above" / "none of the above". Keep options similar in length.
- Where natural, use contexts like WhatsApp commerce, Shopify, Indian D2C brands, and AI assistants.
- Don't worry about answer positions — the finalize script balances them.

## 4. Validate and publish
```
python3 tools/finalize.py drafts/<date>.json
```
It checks the structure, rejects repeated concepts or near-duplicate wording against the ledger, balances answer positions, writes `quizzes/<date>.json`, and updates `quizzes/index.json` and `ledger/asked.jsonl`. If it reports problems, replace those questions and re-run until it prints `OK`.

## 5. Ship and notify
- Commit everything (`Daily quiz <date>`) and push to `main`.
- Confirm `https://balendus.github.io/dailypm/quizzes/<date>.json` returns the new quiz (Pages can take a minute or two).
- Notify Balendu: "Today's 30 PM questions are ready — <theme>. https://balendus.github.io/dailypm/"

Scores are saved by the page through the `dailypm-scores` Supabase Edge Function (table `public.dailypm_attempts`). The page holds no keys.
