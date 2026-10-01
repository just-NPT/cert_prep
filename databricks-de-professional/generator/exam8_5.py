Q = [
dict(d="Debugging & Deploying", q="""A nightly job sometimes fails because of short-lived problems, such as cloud storage throttling or a source API returning HTTP 503. Running the task again a few minutes later always succeeds. How should the job be configured?""",
a=["Set task-level retries (for example, 3 retries with a minimum interval of a few minutes between them), and send failure notifications only after the final retry",
   "Set unlimited retries with no delay on every task",
   "Turn off failure notifications so the occasional failures go unnoticed",
   "Increase the cluster size so throttling can't happen"],
e="""Task retries with a delay handle transient errors automatically, and the delay gives the external system time to recover. Muting notifications until the last retry avoids alert noise while real failures still get reported.

Retrying immediately and without limit can make throttling worse."""),

dict(d="Data Modeling", q="""A gold layer serves a BI tool whose users find it hard to work with star-schema joins, and its dashboards query the same five dimensions over and over. The team is considering a denormalized "one big table" (OBT) for this use case.

Which statement describes the trade-off correctly?""",
a=["An OBT pre-joins the facts and dimensions, which makes queries simpler and avoids joins at query time, at the cost of redundant data and more work to rebuild it when dimension attributes change.",
   "An OBT always uses less storage than a star schema, because columns are stored only once.",
   "An OBT removes the need for any upstream silver tables.",
   "An OBT automatically tracks SCD Type 2 history for every attribute."],
e="""Denormalized wide tables trade storage and maintenance for query simplicity and speed. When a dimension attribute changes, many rows may need updating. Teams often build OBTs as materialized views on top of a star schema for specific consumers."""),
]
