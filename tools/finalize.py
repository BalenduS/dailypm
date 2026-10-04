#!/usr/bin/env python3
"""Validate a draft quiz, shuffle answer positions, check for repeats, and publish it.

Usage: python3 tools/finalize.py drafts/YYYY-MM-DD.json

- Validates structure: exactly 30 questions, 4 options, 4 rationales, answer index 0-3.
- Rejects questions whose concept or wording repeats anything in ledger/asked.jsonl.
- Shuffles option order (seeded by date) so correct answers are spread across A-D.
- Writes quizzes/YYYY-MM-DD.json, updates quizzes/index.json and ledger/asked.jsonl.
"""
import difflib, json, random, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledger" / "asked.jsonl"
INDEX = ROOT / "quizzes" / "index.json"


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def main(path):
    draft = json.loads(Path(path).read_text())
    date = draft.get("date", "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        fail("draft needs a 'date' of YYYY-MM-DD")
    qs = draft.get("questions", [])
    if len(qs) != 30:
        fail(f"expected 30 questions, got {len(qs)}")

    past = []
    if LEDGER.exists():
        past = [json.loads(l) for l in LEDGER.read_text().splitlines() if l.strip()]
    past = [p for p in past if p.get("date") != date]  # allow re-running the same day
    past_concepts = {norm(p["concept"]): p for p in past}
    past_questions = [(norm(p["question"]), p) for p in past]

    seen_c, problems = set(), []
    for i, q in enumerate(qs, 1):
        for k in ("topic", "concept", "difficulty", "question", "options", "answer", "explanation", "rationales"):
            if k not in q:
                problems.append(f"Q{i}: missing '{k}'")
        if problems:
            continue
        if len(q["options"]) != 4 or len(q["rationales"]) != 4:
            problems.append(f"Q{i}: needs exactly 4 options and 4 rationales")
        if q["answer"] not in (0, 1, 2, 3):
            problems.append(f"Q{i}: answer must be 0-3")
        if len({" ".join(o.lower().split()) for o in q["options"]}) != 4:
            problems.append(f"Q{i}: duplicate options")
        if q["difficulty"] not in ("easy", "medium", "hard"):
            problems.append(f"Q{i}: difficulty must be easy/medium/hard")
        c = norm(q["concept"])
        if c in seen_c:
            problems.append(f"Q{i}: concept repeated within today's quiz: {q['concept']}")
        seen_c.add(c)
        if c in past_concepts:
            p = past_concepts[c]
            problems.append(f"Q{i}: concept already asked on {p['date']}: {q['concept']}")
        nq = norm(q["question"])
        for pq, p in past_questions:
            if difflib.SequenceMatcher(None, nq, pq).ratio() > 0.8:
                problems.append(f"Q{i}: too similar to {p['date']} question: {p['question']}")
                break
    if problems:
        print("\n".join(problems))
        fail(f"{len(problems)} problem(s) — replace those questions and re-run")

    rng = random.Random("dailypm:" + date)
    targets = ([0, 1, 2, 3] * 8)[: len(qs)]  # balanced spread of correct positions
    rng.shuffle(targets)
    out = []
    for i, q in enumerate(qs, 1):
        others = [j for j in range(4) if j != q["answer"]]
        rng.shuffle(others)
        order = others[:]
        order.insert(targets[i - 1], q["answer"])
        out.append({
            "id": f"{date}-{i:02d}",
            "topic": q["topic"],
            "concept": q["concept"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "options": [q["options"][j] for j in order],
            "rationales": [q["rationales"][j] for j in order],
            "answer": order.index(q["answer"]),
            "explanation": q["explanation"],
            **({"source": q["source"]} if q.get("source") else {}),
        })

    quiz = {"date": date, "theme": draft.get("theme", ""), "questions": out}
    (ROOT / "quizzes").mkdir(exist_ok=True)
    (ROOT / "quizzes" / f"{date}.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=1))

    index = json.loads(INDEX.read_text()) if INDEX.exists() else {"quizzes": []}
    entries = [e for e in index["quizzes"] if e["date"] != date]
    entries.append({"date": date, "theme": quiz["theme"], "count": len(out)})
    index["quizzes"] = sorted(entries, key=lambda e: e["date"], reverse=True)
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1))

    LEDGER.parent.mkdir(exist_ok=True)
    lines = [json.dumps(p, ensure_ascii=False) for p in past]
    lines += [json.dumps({"date": date, "topic": q["topic"], "concept": q["concept"], "question": q["question"]}, ensure_ascii=False) for q in out]
    LEDGER.write_text("\n".join(sorted(lines, key=lambda l: json.loads(l)["date"])) + "\n")

    dist = [sum(1 for q in out if q["answer"] == k) for k in range(4)]
    print(f"OK: published {date} — {len(out)} questions; answer spread A-D = {dist}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail("usage: finalize.py drafts/YYYY-MM-DD.json")
    main(sys.argv[1])
