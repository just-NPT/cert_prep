# Databricks Certified Data Engineer Professional – practice

**Live quiz:** https://just-npt.github.io/cert_prep/databricks-de-professional/quiz.html

- `exam-5.json` … `exam-8.json` – original practice exams (59 questions each), labeled by exam domain. Loaded automatically on the live site.
- `quiz.html` – **Test** mode (feedback after each question) or **Exam** mode (results at the end). You can also drop your own exam JSON files onto the page; they are read in the browser and never uploaded.
- `generator/` – source for exams 5–8; rebuild with `python generator/build.py 5 6 7 8`.
- `generator/label_domains.py` – sets the exam-domain label (`section`) on your own local exam-1…4 files so the domain breakdown works for them too; run `python generator/label_domains.py --write` with those files next to `quiz.html` (they are not in this repo).
