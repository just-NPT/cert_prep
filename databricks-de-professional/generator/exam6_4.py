Q = [
dict(d="Monitoring & Alerting", q="""On the Structured Streaming tab of the Spark UI, a query's Input Rate has been steadily higher than its Process Rate for the last hour, and Batch Duration keeps growing.

What does this mean?""",
a=["The query is falling behind. Data is arriving faster than it is being processed, so the backlog and latency are growing.",
   "The query is healthy. A higher input rate means the source is being read efficiently.",
   "The query has stopped and is only replaying old batches from its checkpoint.",
   "The watermark is set too long, so late data is being dropped."],
e="""Input Rate is how fast data arrives. Process Rate is how fast the query handles it. When input keeps exceeding processing, the backlog grows and each batch takes longer.

To fix this, scale the compute, tune the partitions and state, use rate limits to smooth out the load, or optimize the transformations."""),

dict(d="Monitoring & Alerting", q="""The compute metrics for a nightly job's cluster show CPU use around 10% and memory use under 30% across all 20 workers for the whole run. Runtime is stable and meets the SLA.

What is the best action?""",
a=["Reduce the number of workers (or use autoscaling with a lower minimum). The cluster is oversized for this workload.",
   "Add more workers to raise CPU use toward 100%.",
   "Switch to memory-optimized instances, because memory is the bottleneck.",
   "Turn off Adaptive Query Execution to reduce CPU overhead."],
e="""Consistently low CPU and memory use while the SLA is met means you're paying for capacity the job doesn't use. Right-size the cluster or use autoscaling to cut cost.

The compute metrics UI shows CPU, memory, network, and disk metrics per node (it replaced Ganglia on newer runtimes)."""),

dict(d="Cost & Performance Optimization", k=2, q="""Which two statements about Delta Lake liquid clustering are correct? Choose 2 answers:""",
a=["The clustering keys can be changed with `ALTER TABLE ... CLUSTER BY` without immediately rewriting existing data.",
   "Liquid clustering works well with high-cardinality columns that would create too many small partitions under Hive-style partitioning.",
   "Liquid clustering can be combined with Hive-style partitioning on the same table.",
   "Every `OPTIMIZE` on a liquid-clustered table must include a `ZORDER BY` clause.",
   "A table can have up to 32 clustering keys."],
e="""Liquid clustering replaces partitioning and Z-ordering. You can redefine the keys at any time, and the new layout applies to future clustering. Clustering on high-cardinality columns works because there are no fixed partitions.

It can't be combined with partitioning or Z-ordering, and a table can have at most 4 clustering keys."""),

dict(d="Cost & Performance Optimization", q="""A nightly batch job on a job cluster is fault tolerant, isn't time critical, and runs with 30 workers. The team wants to cut compute cost while keeping reliability acceptable.

Which configuration should they choose?""",
a=["Use spot instances for the workers, with fallback to on-demand, and keep the driver on an on-demand instance.",
   "Use spot instances for the driver and on-demand instances for all the workers.",
   "Switch to an all-purpose cluster that is shared with interactive users.",
   "Turn off autoscaling and fix the cluster at 60 workers so it finishes in half the time."],
e="""Spot (preemptible) instances cost much less. Spark can recover from losing a worker by recomputing that worker's tasks, but losing the driver fails the job, so the driver should stay on-demand. Falling back to on-demand capacity keeps the job reliable.

All-purpose compute costs more per DBU than jobs compute."""),

dict(d="Cost & Performance Optimization", q="""A query joins sensor readings to maintenance windows with an interval condition:

```
SELECT ... FROM readings p
JOIN windows r ON p.ts BETWEEN r.start_ts AND r.end_ts
```

Most windows last a few minutes, and the join runs very slowly as a nested-loop join. Which optimization is designed for this pattern?""",
a=["Use range join optimization, for example with the hint `/*+ RANGE_JOIN(r, 300) */` and a bin size that suits the typical interval length.",
   "Add the hint `/*+ BROADCAST(p) */` to broadcast the large readings table.",
   "Z-order both tables by `ts`.",
   "Increase `spark.sql.shuffle.partitions` so the nested-loop join gets more tasks."],
e="""Joins on a point-in-interval or overlapping-interval condition don't have an equality key, so Spark falls back to slow nested-loop or cartesian strategies. Databricks range join optimization splits values into bins (the bin size is set by the hint or configuration), which makes the join far faster.

Broadcasting the larger table is the wrong way round, and layout changes don't change the join algorithm."""),

dict(d="Data Modeling", q="""In a medallion architecture, why is the bronze layer usually kept as raw, append-only data with minimal transformation?""",
a=["So history can be replayed: if business logic changes or a bug is found, silver and gold can be rebuilt from bronze without going back to the source systems.",
   "So BI tools can query bronze directly with the best performance.",
   "So bronze tables don't need Delta Lake and can use plain CSV.",
   "So data quality rules can be enforced as strictly as possible at ingestion."],
e="""Bronze keeps the source data as it arrived, plus ingestion metadata. That gives auditability and lets you reprocess downstream layers from scratch when logic changes. Source systems often don't keep history.

Cleaning and validation usually happen in silver, and consumption-ready models in gold."""),

dict(d="Data Modeling", q="""A team is modeling an enterprise data warehouse layer with Data Vault. Which Data Vault entity stores the descriptive attributes of a business key and tracks how they change over time?""",
a=["Satellite", "Hub", "Link", "Bridge"],
e="""In Data Vault:

- **Hubs** store unique business keys.
- **Links** store the relationships between hubs.
- **Satellites** store descriptive, time-variant attributes for a hub or link, with load dates for tracking history.
- **Bridge** and point-in-time tables are helper structures for querying."""),

dict(d="Data Modeling", q="""Regulations require that records in the Delta table `audit_events` are never updated or deleted after they are written. New records must still be appendable.

Which table setting enforces this?""",
a=["`ALTER TABLE audit_events SET TBLPROPERTIES ('delta.appendOnly' = 'true')`",
   "`ALTER TABLE audit_events SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')`",
   "`ALTER TABLE audit_events ADD CONSTRAINT no_updates CHECK (true)`",
   "`ALTER TABLE audit_events SET TBLPROPERTIES ('delta.logRetentionDuration' = 'interval 3650 days')`"],
e="""With `delta.appendOnly = true`, Delta rejects UPDATE, DELETE, and MERGE operations that would modify or remove existing data, while inserts are still allowed.

CDF and log retention only record changes, and a CHECK constraint validates values, not operation types."""),

dict(d="Data Modeling", q="""A data engineer needs to rename the column `cust_nm` to `customer_name` in a large Delta table, without rewriting the data files. Which approach works?""",
a=["""ALTER TABLE customers SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
ALTER TABLE customers RENAME COLUMN cust_nm TO customer_name;""",
   """ALTER TABLE customers RENAME COLUMN cust_nm TO customer_name;
-- works on any Delta table with no prerequisites""",
   """CREATE OR REPLACE TABLE customers AS
SELECT *, cust_nm AS customer_name FROM customers;""",
   """ALTER TABLE customers SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE customers RENAME COLUMN cust_nm TO customer_name;"""],
e="""Column mapping (`delta.columnMapping.mode = 'name'`) separates logical column names from the physical names in Parquet files. This makes `RENAME COLUMN` and `DROP COLUMN` metadata-only operations. Without it, renaming isn't supported.

A CTAS rewrites every file and keeps the old column too. Type widening is about changing data types."""),

dict(d="Data Modeling", q="""The `quantity` column of a large Delta table is INT, and new source values will soon exceed the INT range. The team wants to change the column to BIGINT without rewriting the existing data files.

Which approach supports this?""",
a=["""ALTER TABLE orders SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE orders ALTER COLUMN quantity TYPE BIGINT;""",
   """ALTER TABLE orders SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
ALTER TABLE orders ALTER COLUMN quantity TYPE BIGINT;""",
   """ALTER TABLE orders ALTER COLUMN quantity TYPE BIGINT;
-- supported by default on every Delta table""",
   """ALTER TABLE orders ADD CONSTRAINT big_qty CHECK (quantity <= 9223372036854775807);"""],
e="""Type widening lets supported type changes, such as INT to BIGINT or FLOAT to DOUBLE, be made on a Delta table without rewriting the data. Existing files are read with the wider type.

Column mapping covers renaming and dropping columns, not type changes. A CHECK constraint doesn't change the column type."""),

dict(d="Data Modeling", q="""Sales facts sometimes arrive before the customer's dimension record exists. The fact load must not drop or hold back these sales, and reports must link them correctly once the customer record arrives.

Which modeling technique handles this?""",
a=["Insert a placeholder (\"inferred member\") row into the customer dimension for the unknown business key, and update its attributes when the real record arrives.",
   "Drop the facts that have no matching dimension row, and reload them manually each week.",
   "Use SCD Type 0 on the customer dimension, so missing customers are ignored.",
   "Store the fact rows in the dimension table until the customer arrives."],
e="""Early-arriving facts (late-arriving dimensions) are usually handled with an inferred member. A minimal dimension row is created with the business key and a surrogate key, so facts can link to it right away. Its attributes are filled in when the full record arrives.

Dropping or holding back facts makes revenue reporting incomplete."""),

dict(d="Security & Compliance", q="""A dynamic view must show the full `salary` column only to members of the account-level group `payroll`. Which function should the view use?""",
a=["`is_account_group_member('payroll')`",
   "`is_member('payroll')`",
   "`current_user() = 'payroll'`",
   "`has_privilege('payroll')`"],
e="""In Unity Catalog, `is_account_group_member()` checks membership in account-level groups, which are the groups used for Unity Catalog grants.

`is_member()` checks workspace-local groups, which is legacy behavior. `current_user()` returns a user, not a group. `has_privilege` is not a valid function."""),

dict(d="Debugging & Deploying", q="""A data engineer uses the Databricks CLI with a development workspace and a production workspace, and wants to switch between them easily. Which approach is recommended?""",
a=["Define a separate configuration profile for each workspace in `~/.databrickscfg` (for example, `[DEV]` and `[PROD]`), and pick one per command with `--profile PROD` (or `-p PROD`).",
   "Run `databricks configure` again before every command to overwrite the default host and token.",
   "Put both workspace URLs in `DATABRICKS_HOST`, separated by a comma.",
   "Install two copies of the CLI, one per workspace."],
e="""The CLI and SDKs read named profiles from `.databrickscfg`, each with its own host and authentication method (for example, OAuth via `databricks auth login --profile PROD`). Choosing the profile per command, or with the `DATABRICKS_CONFIG_PROFILE` environment variable, avoids mistakes."""),

dict(d="Debugging & Deploying", q="""Job 123 has a job-level parameter `run_date`. A data engineer needs to trigger a run through the REST API for `2025-06-01`, overriding the default. Which request does this?""",
a=["""POST /api/2.2/jobs/run-now
{ "job_id": 123, "job_parameters": { "run_date": "2025-06-01" } }""",
   """POST /api/2.2/jobs/update
{ "job_id": 123, "new_settings": { "run_date": "2025-06-01" } }""",
   """GET /api/2.2/jobs/runs/get?job_id=123&run_date=2025-06-01""",
   """POST /api/2.2/jobs/runs/submit
{ "job_id": 123, "run_date": "2025-06-01" }"""],
e="""`jobs/run-now` triggers an existing job, and the `job_parameters` map overrides the job-level parameter values for that run only. The response includes the new `run_id`.

`jobs/update` changes the job's settings permanently, `runs/get` only reads run metadata, and `runs/submit` creates one-time runs that aren't tied to a job definition."""),
]
