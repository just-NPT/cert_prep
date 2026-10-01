Q = [
dict(d="Transformation, Cleansing & Quality", q="""A streaming query reads from a Delta table and has a checkpoint location. With no custom code, which sink gives end-to-end exactly-once guarantees when the query fails and restarts?""",
a=["A Delta table sink (`writeStream.toTable(...)`)",
   "A Kafka sink",
   "A `foreach` sink that posts each row to a REST API",
   "A `foreachBatch` sink that inserts each micro-batch into a JDBC database"],
e="""The Delta sink uses the checkpoint and Delta transaction metadata to make each micro-batch commit idempotent, so it achieves exactly-once.

- The Kafka sink is at-least-once.
- `foreach` and `foreachBatch` writes to external systems are at-least-once unless you make them idempotent yourself, for example with upserts or the `txnAppId`/`txnVersion` options for Delta."""),

dict(d="Transformation, Cleansing & Quality", q="""In an SDP pipeline, an intermediate dataset joins and cleans two sources. It feeds two downstream tables, but it should not be published to Unity Catalog or be queryable outside the pipeline.

How should it be defined?""",
a=["As a temporary view in the pipeline (for example, `CREATE TEMPORARY VIEW` in SQL)",
   "As a streaming table with the table property `pipelines.reset.allowed = false`",
   "As a materialized view in a schema that no one has been granted access to",
   "As a global temporary view created in a separate notebook"],
e="""Temporary views in a pipeline exist only inside that pipeline. Downstream datasets can use them, but they aren't stored or published to the catalog.

Tables and materialized views are always stored and registered in Unity Catalog. Global temporary views from other notebooks aren't part of the pipeline graph."""),

dict(d="Transformation, Cleansing & Quality", q="""What is the difference between running an SDP pipeline in development mode and in production mode?""",
a=["Development mode reuses the compute and turns off automatic retries so errors show up quickly. Production mode restarts compute for recoverable errors and retries failed updates.",
   "Development mode writes to temporary tables that are dropped after each update, and production mode writes to Unity Catalog.",
   "Development mode only processes a 10% sample of the source data.",
   "Production mode turns off expectations to maximize throughput."],
e="""Development mode is built for quick iteration: the cluster is kept running between updates, and failures aren't retried automatically. Production mode is built for reliability: it restarts the cluster for certain recoverable errors and retries execution.

In both modes the pipeline writes to the same target tables and enforces the same expectations."""),

dict(d="Transformation, Cleansing & Quality", q="""An SDP pipeline must refresh its tables once an hour to meet its SLA, and the team wants to keep compute costs as low as possible.

How should the pipeline run?""",
a=["In triggered mode, scheduled every hour, so compute processes the available data and then shuts down",
   "In continuous mode, so tables are always up to date",
   "In continuous mode with a processing-time trigger of 1 hour",
   "In triggered mode, with a full refresh on every run"],
e="""Triggered pipelines process all available data, then stop their compute. Running one on a schedule that matches the SLA keeps costs down.

Continuous pipelines keep compute running all the time, which you only need for low latency. A full refresh on every run reprocesses everything."""),

dict(d="Transformation, Cleansing & Quality", q="""`silver.customers` has Change Data Feed enabled and receives inserts, updates, and deletes. A gold table that keeps one row per customer must be updated incrementally, including removing customers deleted in silver.

Which approach should be used?""",
a=["Stream silver's Change Data Feed. In `foreachBatch`, keep the latest change per key, then MERGE into gold, deleting matched rows whose `_change_type` is `delete` and upserting the others.",
   "Stream silver as a normal Delta source with `skipChangeCommits` set to `true`, and append the results to gold.",
   "Rebuild gold every hour with `INSERT INTO gold SELECT * FROM silver.customers`.",
   "Read silver with time travel at the previous version and union it with the current version."],
e="""CDF provides row-level change events, including deletes and update postimages, that a stream can read incrementally. A MERGE that takes the latest event per key and acts on `_change_type` keeps gold in sync.

`skipChangeCommits` ignores the deletes. `INSERT INTO` duplicates rows. Union snapshots don't capture the individual changes."""),

dict(d="Transformation, Cleansing & Quality", q="""With ANSI SQL mode enabled, a cleansing query fails because some values in the STRING column `qty` (such as `'N/A'`) can't be cast to INT. Invalid values should become NULL so they can be quarantined later.

Which expression should be used?""",
a=["`try_cast(qty AS INT)`", "`cast(qty AS INT)`", "`qty::INT`", "`int(qty)`"],
e="""In ANSI mode, `CAST` (including the `::` shorthand and functions like `int()`) raises an error on invalid input. `try_cast` returns NULL instead. Similar functions include `try_to_timestamp` and `try_divide`."""),

dict(d="Transformation, Cleansing & Quality", q="""A `foreachBatch` function upserts CDC events into the target table `accounts`. Events can arrive out of order across micro-batches, and each one has a monotonically increasing `seq` number.

Which MERGE stops a late, older event from overwriting a newer state?""",
a=["""MERGE INTO accounts t USING batch s ON t.id = s.id
WHEN MATCHED AND s.seq > t.seq THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO accounts t USING batch s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO accounts t USING batch s ON t.id = s.id AND s.seq > t.seq
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """INSERT INTO accounts SELECT * FROM batch ORDER BY seq"""],
e="""A conditional `WHEN MATCHED AND s.seq > t.seq` only updates when the incoming event is newer than the stored state. The batch should also be reduced to the latest event per key first.

Putting the sequence check in the `ON` clause makes older events miss the match, and they would then be inserted as duplicates. Ordering an INSERT doesn't upsert anything."""),

dict(d="Data Sharing & Federation", q="""A provider updates a shared Delta table several times a day. When do Databricks-to-Databricks recipients see the changes?""",
a=["On their next query, because recipients read the provider's current table version directly and no data is copied",
   "After the provider runs `ALTER SHARE ... REFRESH`",
   "Once a day, when Delta Sharing copies the table to the recipient's metastore",
   "Only after the recipient creates a new catalog from the share"],
e="""Delta Sharing doesn't copy data to recipients. Recipients read the shared table's files directly, using short-lived credentials issued for each query, so each query sees the provider's latest committed version.

The recipient's catalog only holds references to the shared objects."""),

dict(d="Data Sharing & Federation", q="""The bearer-token credential file of an open-sharing recipient was accidentally posted in a public repository. What should the provider do right away?""",
a=["Rotate the recipient's token, set the existing token to expire immediately, and send the new activation link through a secure channel.",
   "Remove all tables from the share and add them back.",
   "Run `VACUUM` on the shared tables so the exposed credential can no longer read old files.",
   "Change the share's comment to mark it as compromised."],
e="""In open sharing, anyone who holds a valid bearer token can read the data. Rotating the token issues a new credential, and setting the old one to expire right away cuts off access through the leaked file. Short token lifetimes and IP access lists reduce this risk further.

Changing the share's contents doesn't invalidate the leaked token."""),

dict(d="Data Sharing & Federation", q="""A provider wants to make sure an open-sharing recipient can only read the shared data from the partner's corporate network ranges. What should the provider configure?""",
a=["An IP access list on the recipient",
   "A row filter on every shared table that checks `current_user()`",
   "A workspace IP access list in the provider's workspace",
   "A cluster policy on the provider's SQL warehouse"],
e="""Delta Sharing lets providers attach an IP access list to an open-sharing recipient, so the recipient's credentials only work from the allowed IP ranges.

A workspace IP access list protects the provider's own workspace, not access to shared data. Row filters can't see the recipient's network address."""),

dict(d="Data Sharing & Federation", q="""Since dashboards started querying a PostgreSQL database through a Lakehouse Federation foreign catalog, the database has been overloaded and dashboard performance is poor. The data only needs to be refreshed hourly.

What should the team do?""",
a=["Materialize the needed federated data into Delta, for example with a materialized view or an ingestion job refreshed hourly, and point the dashboards at the Delta tables.",
   "Give the PostgreSQL connection more Spark executors so federated queries run faster.",
   "Turn on Delta caching for the foreign catalog so PostgreSQL tables are kept on local disks forever.",
   "Grant the dashboard users direct access to the PostgreSQL database."],
e="""Federation works well for ad-hoc and occasional queries, but each query hits the source system. For heavy, repeated workloads, copy the data into Delta on a schedule that matches its freshness needs. This takes load off the source and makes queries faster."""),

dict(d="Data Sharing & Federation", q="""A provider wants to share tables with a partner who uses a Databricks workspace that is not enabled for Unity Catalog. Which sharing method must the provider use?""",
a=["Open sharing (a token-based or OIDC credential), because Databricks-to-Databricks sharing requires the recipient to use Unity Catalog",
   "Databricks-to-Databricks sharing, using the partner's workspace URL as the sharing identifier",
   "Lakehouse Federation from the partner's workspace to the provider's metastore",
   "Deep clone the tables into the partner's DBFS root"],
e="""Databricks-to-Databricks sharing needs a recipient metastore, and the sharing identifier is based on it. Without Unity Catalog, the partner can still read the shares through open sharing, for example with the Spark connector and a credential file."""),

dict(d="Monitoring & Alerting", q="""An ML team logs every model prediction to a Unity Catalog table, with the columns `prediction`, `label` (filled in later), `model_version`, and `request_ts`. They want to monitor prediction drift and model quality over time.

Which data profiling (Lakehouse Monitoring) profile type should they use?""",
a=["InferenceLog", "Snapshot", "TimeSeries", "Expectations"],
e="""The InferenceLog profile is built for model request and response tables. It needs prediction, model ID, and timestamp columns (labels are optional) and computes drift and model quality metrics over time windows and model versions.

TimeSeries profiles general time-partitioned data, and Snapshot profiles the whole table. There's no profile type called Expectations."""),

dict(d="Monitoring & Alerting", q="""A platform team wants to be told automatically when tables in the `prod.sales` schema stop receiving fresh data or receive far fewer rows than usual, without writing rules for each table.

Which feature fits best?""",
a=["Data quality monitoring (anomaly detection) on the schema, which learns each table's usual update pattern and flags freshness and completeness problems",
   "A CHECK constraint on every table in the schema",
   "Expectations with `ON VIOLATION FAIL UPDATE` added to every pipeline",
   "A job email notification on every job that writes to the schema"],
e="""Anomaly detection monitors every table in a schema, models its historical commit patterns and volumes, and flags tables that are stale or incomplete, with no thresholds to define.

Constraints and expectations validate the values of rows that are written. They can't detect data that never arrived."""),

dict(d="Monitoring & Alerting", q="""Finance wants Databricks costs broken down by team, and each team runs its own jobs. Which approach supports this?""",
a=["Add a custom tag such as `team` to job compute (and use budget policies for serverless). Then group `system.billing.usage` by `custom_tags['team']`.",
   "Use a separate SQL warehouse per team. Billing usage can only be attributed to warehouses.",
   "Parse the job names in `system.lakeflow.jobs` and estimate costs from run durations.",
   "Turn on audit logging. Audit events include the DBU cost of every command."],
e="""Custom tags on clusters, pools, jobs, and warehouses, and serverless budget policies, are copied to the `custom_tags` column of `system.billing.usage`. Grouping by a tag gives cost attribution for chargeback.

Audit logs don't include costs."""),
]
