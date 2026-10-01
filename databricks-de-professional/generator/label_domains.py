"""Assign exam-domain labels to the `section` field of exam-1..4 (keyword rules + manual overrides)."""
import json, re, sys, os

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ING, TRF, SHR, MON, PERF, SEC, GOV, DEP, MOD, DEV = (
    "Data Ingestion", "Transformation, Cleansing & Quality", "Data Sharing & Federation",
    "Monitoring & Alerting", "Cost & Performance Optimization", "Security & Compliance",
    "Data Governance", "Debugging & Deploying", "Data Modeling", "Developing Code (Python & SQL)")

# first match wins
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

OVERRIDES = {}  # "exam.qnum": domain

def classify(text):
    t = text.lower()
    for dom, pat in RULES:
        if re.search(pat, t):
            return dom

def main(write):
    for i in range(1, 5):
        p = os.path.join(D, f"exam-{i}.json")
        data = json.load(open(p, encoding="utf-8"))
        for n, q in enumerate(data["results"], 1):
            key = f"{i}.{n}"
            dom = OVERRIDES.get(key) or classify(q["question_plain"])
            q["section"] = dom
            if not write:
                print(f"{key:6} {dom[:22]:22} | {q['question_plain'][:110]}")
        if write:
            json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    if write:
        print("written")

if __name__ == "__main__":
    main("--write" in sys.argv)
