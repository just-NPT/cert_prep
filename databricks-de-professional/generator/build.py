"""Build exam-N.json files (Udemy practice-test JSON shape) from part modules.

Each part module exposes Q = [dict(d=domain, q=question, a=[answers], e=explanation, k=n_correct)].
Authoring convention: the first k answers are correct; answers are shuffled deterministically here.
Text supports ```code fences``` and `inline code`.
"""
import glob, html, importlib.util, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)


def to_html(text):
    out = []
    for i, chunk in enumerate(re.split(r"```(?:\w+)?\n?", text.strip())):
        if i % 2:  # inside a fence
            out.append('<pre class="prettyprint linenums">' + html.escape(chunk.rstrip("\n"), quote=False) + "</pre>")
        else:
            for para in re.split(r"\n\s*\n", chunk.strip()):
                if para.strip():
                    out.append("<p>" + inline(para.strip()).replace("\n", "<br>") + "</p>")
    return "".join(out)


def answer_html(a):
    if "\n" in a.strip() or a.startswith("```"):
        return '<pre class="prettyprint linenums">' + html.escape(a.strip().strip("`").strip("\n"), quote=False) + "</pre>"
    return "<p>" + inline(a) + "</p>"


def plain(h):
    return html.unescape(re.sub(r"<[^>]+>", "", h.replace("<br>", " ")))


def build(exam):
    parts = sorted(glob.glob(os.path.join(HERE, f"exam{exam}_*.py")))
    qs = []
    for p in parts:
        spec = importlib.util.spec_from_file_location(os.path.basename(p)[:-3], p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        qs.extend(m.Q)
    # balanced correct-answer positions for single-answer questions
    slots = [0, 1, 2, 3] * (len(qs) // 4 + 1)
    random.Random(exam).shuffle(slots)
    results = []
    for n, q in enumerate(qs, 1):
        k = q.get("k", 1)
        answers = list(q["a"])
        assert len(answers) >= 4 and 1 <= k < len(answers), (exam, n)
        rng = random.Random(exam * 1000 + n)
        if k == 1 and len(answers) == 4:
            order = list(range(1, 4))
            rng.shuffle(order)
            order.insert(slots.pop(), 0)
        else:
            order = list(range(len(answers)))
            rng.shuffle(order)
        shuffled = [answers[i] for i in order]
        correct = sorted(chr(97 + order.index(i)) for i in range(k))
        qhtml = to_html(q["q"])
        results.append({
            "_class": "assessment",
            "id": 990000000 + exam * 1000 + n,
            "assessment_type": "multi-select" if k > 1 else "multiple-choice",
            "prompt": {
                "question": qhtml,
                "relatedLectureIds": [],
                "links": [],
                "feedbacks": [""] * len(shuffled),
                "explanation": to_html(q["e"]),
                "answers": [answer_html(a) for a in shuffled],
            },
            "correct_response": correct,
            "section": q["d"],
            "question_plain": plain(qhtml),
            "related_lectures": [],
        })
    path = os.path.join(OUT, f"exam-{exam}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"count": len(results), "next": None, "previous": None, "results": results}, f, ensure_ascii=False, indent=4)
    print(path, len(results), "questions")


if __name__ == "__main__":
    for e in map(int, sys.argv[1:]):
        build(e)
