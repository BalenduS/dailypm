# Daily PM

30 product-management multiple-choice questions every morning at 8:00 AM IST — strategy, discovery, metrics, experimentation, execution, stakeholders, AI products, technology, growth, and current events. No question concept repeats.

**Take today's quiz:** https://balendus.github.io/dailypm/

- Answer all 30, submit, and every question shows the correct answer, an explanation, and — if you missed it — why your pick was wrong.
- Scores, topic breakdowns, and streaks are saved online and shown on the home page.

## How it works
| Part | Where |
|---|---|
| Quiz page | `index.html` (static, GitHub Pages) |
| Daily questions | `quizzes/<date>.json`, listed in `quizzes/index.json` |
| No-repeat ledger | `ledger/asked.jsonl` |
| Validation & publishing | `tools/finalize.py` |
| Daily routine | `GENERATE.md`, run by a Claude scheduled task at 8:00 AM IST |
| Score storage | Supabase Edge Function `dailypm-scores` → table `dailypm_attempts` |
