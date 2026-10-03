"""Assign exam-domain labels to the `section` field of exam-1..4.

LABELS holds hand-reviewed domains (one code per question, in file order). The keyword
RULES are only a fallback for questions beyond the reviewed range.
Usage: python label_domains.py          # dry run, prints labels
       python label_domains.py --write  # writes `section` into exam-1..4.json
"""
import json, re, sys, os
from collections import Counter

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ING, TRF, SHR, MON, PERF, SEC, GOV, DEP, MOD, DEV = (
    "Data Ingestion", "Transformation, Cleansing & Quality", "Data Sharing & Federation",
    "Monitoring & Alerting", "Cost & Performance Optimization", "Security & Compliance",
    "Data Governance", "Debugging & Deploying", "Data Modeling", "Developing Code (Python & SQL)")

CODES = dict(ING=ING, TRF=TRF, SHR=SHR, MON=MON, PERF=PERF, SEC=SEC, GOV=GOV, DEP=DEP, MOD=MOD, DEV=DEV)

# hand-reviewed, 10 per row
LABELS = {
    1: """DEP  MOD  SEC  SEC  MOD  TRF  TRF  PERF TRF  TRF
          TRF  PERF DEV  TRF  DEV  TRF  TRF  ING  PERF PERF
          GOV  PERF MOD  SEC  MON  DEV  DEV  DEP  TRF  SEC
          GOV  DEV  GOV  ING  SEC  DEP  DEV  PERF PERF PERF
          MON  GOV  DEV  SHR  SHR  SHR  GOV  PERF DEP  DEP
          TRF  DEP  ING  SEC  DEV  MON  SEC  TRF  PERF""",
    2: """SEC  MOD  DEP  TRF  TRF  TRF  TRF  MOD  TRF  TRF
          ING  TRF  MOD  TRF  TRF  MOD  PERF SEC  PERF TRF
          DEV  SEC  GOV  MON  DEP  DEV  DEP  DEP  DEP  DEP
          SEC  PERF TRF  DEP  DEV  SHR  SHR  SHR  ING  MOD
          PERF DEP  SHR  PERF DEP  SEC  PERF SHR  DEP  PERF
          TRF  MOD  SEC  DEV  DEV  ING  TRF  MON  SEC""",
    3: """SEC  SEC  MOD  PERF PERF MOD  TRF  TRF  MOD  TRF
          PERF MOD  PERF SEC  DEV  MOD  MON  SEC  DEP  PERF
          PERF DEV  TRF  GOV  DEP  DEP  DEP  DEP  PERF PERF
          TRF  SHR  MON  MON  DEP  PERF GOV  ING  SHR  DEP
          DEP  MON  SHR  MOD  DEP  TRF  TRF  DEP  TRF  TRF
          PERF DEV  DEP  ING  TRF  SHR  DEP  SHR  SEC""",
    4: """ING  SEC  SEC  DEV  DEV  TRF  MOD  SEC  DEP  PERF
          TRF  SEC  SEC  MON  DEP  DEV  DEP  DEP  GOV  TRF
          TRF  MOD  GOV  TRF  DEP  PERF DEV  DEP  PERF SEC
          TRF  SEC  PERF DEP  DEP  ING  TRF  MON  SHR  DEP
          DEP  ING  TRF  SHR  GOV  PERF SHR  MON  DEP  DEV
          SEC  TRF  PERF MOD  MON  ING  GOV  DEV  DEP""",
}
LABELS = {k: [CODES[c] for c in v.split()] for k, v in LABELS.items()}

# keyword fallback, first match wins
RULES = [
    (SHR, r"delta sharing|lakehouse federation|foreign catalog|sharing identifier|recipient|connection named|external (postgresql|mysql)|clean room|oracle databases"),
    (SEC, r"secret|sha-?2|hash|mask|row filter|row-level|forgotten|gdpr|sensitive|pii|social security|password|anonymi|encrypt"),
    (MON, r"system table|system\.|alert|notification|event log|lakehouse monitoring|data profiling|dashboard to track|anomal|query profile|spark ui|observability|monitor"),
    (DEP, r"asset bundle|automation bundle|\bdabs?\b|rest api|\bcli\b|repair|multi-task job|\bjob\b|jobs|cron|cluster|git|pull request|wheel|library|init script|%sh|%pip|sys\.path|notebook source|working directory|dbutils\.notebook|production"),
    (GOV, r"unity catalog|grant|privilege|permission|owner|catalog|lineage|comment|tag"),
    (PERF, r"optimi[sz]|compaction|file size|z-?order|liquid clustering|partition|skew|spill|broadcast|pruning|deletion vector|file statistics|data skipping|performance|slow|photon|cache|vacuum"),
    (ING, r"auto ?loader|cloudfiles|kafka|ingest|copy into|binaryfile|image files|json data"),
    (MOD, r"\bscd\b|slowly changing|type 0|type 1|type 2|medallion|bronze|silver|gold|clone|location keyword|ctas|create table .* as select|multiplex|singleplex|data model"),
    (TRF, r"stream|watermark|dedup|duplicate|merge|change data|cdf|cdc|expect|constraint|data quality|sdp|declarative pipelines|dlt|materialized view|late-arriving"),
    (DEV, r"."),
]

def classify(text):
    t = text.lower()
    for dom, pat in RULES:
        if re.search(pat, t):
            return dom

def main(write):
    for i in range(1, 5):
        p = os.path.join(D, f"exam-{i}.json")
        data = json.load(open(p, encoding="utf-8"))
        labels = LABELS.get(i, [])
        if len(labels) != len(data["results"]):
            print(f"exam-{i}: {len(labels)} reviewed labels for {len(data['results'])} questions, rest use keyword fallback")
        for n, q in enumerate(data["results"], 1):
            dom = labels[n - 1] if n <= len(labels) else classify(q["question_plain"])
            q["section"] = dom
            if not write:
                print(f"{i}.{n:<3} {dom[:22]:22} | {q['question_plain'][:110]}")
        print(f"exam-{i}:", ", ".join(f"{d} {c}" for d, c in Counter(q["section"] for q in data["results"]).most_common()))
        if write:
            json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    if write:
        print("written")

if __name__ == "__main__":
    main("--write" in sys.argv)
