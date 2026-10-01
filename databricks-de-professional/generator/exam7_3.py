Q = [
dict(d="Monitoring & Alerting", q="""A multi-task job has slowed down gradually over the last month. The data engineer wants to see, run by run, which task's duration has been growing. Which UI view is the most direct way to see this?""",
a=["The job's Runs page in matrix view, which shows each task's duration and status across recent runs",
   "The Spark UI of the most recent run",
   "The SQL warehouse's query history",
   "The cluster's event log"],
e="""The matrix view on a job's Runs page puts runs in columns and tasks in rows, with the duration and status of each. Trends and regressions for individual tasks are easy to spot there.

The Spark UI only covers one run on one cluster."""),

dict(d="Monitoring & Alerting", q="""The on-call team wants an email whenever an update of a particular SDP pipeline fails. What is the simplest way to set this up?""",
a=["Add a notification to the pipeline's settings, with the on-call email and the update failure event selected",
   "Write a SQL query against `system.billing.usage` and create a SQL alert on it",
   "Add an expectation with `ON VIOLATION FAIL UPDATE` to every table",
   "Wrap the pipeline in a notebook that sends an email with `smtplib`"],
e="""Pipelines have their own notification settings. You can send emails for events such as update success, update failure, fatal update failure, and flow failure.

If the pipeline runs as a task in a job, job-level notifications also work."""),

dict(d="Monitoring & Alerting", q="""A platform engineer needs historical CPU and memory use for every node of the classic compute in the account, so they can find clusters that are consistently underused. Which system table provides this?""",
a=["`system.compute.node_timeline`",
   "`system.compute.clusters`",
   "`system.billing.list_prices`",
   "`system.lakeflow.job_task_run_timeline`"],
e="""`system.compute.node_timeline` records minute-level resource metrics for each node, such as CPU, memory, and network use. `system.compute.clusters` only records cluster configurations and how they change over time."""),

dict(d="Cost & Performance Optimization", q="""A job reads one 2 GB Parquet file on a cluster with 64 cores. The read stage runs with only 16 tasks, which leaves most cores idle. Which setting increases the number of read tasks?""",
a=["Lower `spark.sql.files.maxPartitionBytes` (for example to 32 MB)",
   "Raise `spark.sql.shuffle.partitions` to 512",
   "Raise `spark.sql.autoBroadcastJoinThreshold`",
   "Turn on Change Data Feed on the source"],
e="""The number of input splits for file sources depends on `spark.sql.files.maxPartitionBytes`, which defaults to 128 MB, so 2 GB gives about 16 splits. Lowering the value creates more, smaller input tasks.

The shuffle partition setting only applies after a shuffle."""),

dict(d="Cost & Performance Optimization", q="""On a SQL warehouse, an analyst runs a heavy aggregation query that takes 40 seconds. A minute later, a colleague runs exactly the same query and gets the results almost instantly. No data has changed in between.

What explains this?""",
a=["The query result cache returned the cached results of the identical query, because the underlying tables hadn't changed.",
   "The second run used Photon, and the first run didn't.",
   "The warehouse automatically created a materialized view after the first run.",
   "Delta automatically Z-ordered the table during the first query."],
e="""SQL warehouses cache query results. An identical query on unchanged data can be answered from the cache without running it again. The cache is invalidated when the underlying Delta tables change.

The disk cache also speeds up later reads of the same files, but it doesn't skip computation."""),

dict(d="Cost & Performance Optimization", k=2, q="""A batch job writes a Delta table as about 2,000 small files per run. Which two changes would reduce the number of small output files? Choose 2 answers:""",
a=["Call `coalesce(50)` on the DataFrame before writing",
   "Enable optimized writes (`delta.autoOptimize.optimizeWrite = true`) on the target table",
   "Call `repartition(5000)` on the DataFrame before writing",
   "Increase `spark.sql.shuffle.partitions` to 4,000",
   "Disable auto compaction on the target table"],
e="""- `coalesce` reduces the number of partitions without a full shuffle, so fewer files are written.
- Optimized writes rebalance data before writing, so files are fewer and larger.

More partitions mean more files, and disabling auto compaction removes a mechanism that combines small files."""),

dict(d="Cost & Performance Optimization", q="""A query adds row numbers with the following code, and it runs as one very long task:

```
df.withColumn("rn", F.row_number().over(Window.orderBy("event_ts")))
```

What is the cause?""",
a=["The window has no `partitionBy`, so Spark moves all rows to a single partition to compute a global order.",
   "`row_number` is a Python UDF and runs on the driver.",
   "Ordering by a timestamp turns off Adaptive Query Execution.",
   "Window functions always run on one executor, whatever the window specification."],
e="""A window with no partitioning gives one global ordering, so all the data goes to a single task. Spark even logs a warning about this.

Partition the window by a key when you can, or, if you only need unique IDs rather than consecutive ones, use `monotonically_increasing_id()`."""),

dict(d="Cost & Performance Optimization", q="""A team has to keep a complex Python function as a UDF, because it can't be written with built-in functions. The UDF is a bottleneck. Which change will most likely improve its performance?""",
a=["Make it a pandas UDF, or an Arrow-optimized Python UDF (`useArrow=True`), so data moves between the JVM and Python in vectorized Arrow batches",
   "Make it a row-at-a-time `@udf` with an explicit return type",
   "Call the function inside `rdd.map()` instead of using a DataFrame UDF",
   "Set `spark.sql.shuffle.partitions` to 1 so the UDF runs on one large partition"],
e="""Standard Python UDFs serialize data row by row with pickle. Arrow-based execution, through pandas UDFs or Arrow-optimized Python UDFs, sends columnar batches and greatly reduces serialization cost.

RDD code loses optimizer benefits. A single partition removes parallelism."""),

dict(d="Cost & Performance Optimization", q="""A 50 TB Delta table is partitioned by `event_date`. Only the last 7 days get new writes, and the team wants to compact only those partitions. Which command should they use?""",
a=["`OPTIMIZE events WHERE event_date >= current_date() - INTERVAL 7 DAYS`",
   "`OPTIMIZE events`",
   "`VACUUM events RETAIN 168 HOURS`",
   "`OPTIMIZE events WHERE user_id IS NOT NULL`"],
e="""On a partitioned table, `OPTIMIZE` takes a `WHERE` clause that limits compaction to the matching partitions, which avoids reprocessing all the historical data. The predicate can only use partition columns.

VACUUM removes old files and doesn't compact anything."""),

dict(d="Cost & Performance Optimization", q="""A streaming SDP pipeline gets highly variable traffic: steady most of the day, with large spikes at peak hours. The team wants compute to follow the load without being over-provisioned.

What should they configure?""",
a=["Enhanced autoscaling for the pipeline (or serverless pipelines), which scales on streaming backlog and utilization",
   "A fixed-size cluster sized for the peak load",
   "Standard cluster autoscaling with the minimum and maximum workers set to the same value",
   "A new pipeline that is started manually before each peak"],
e="""Enhanced autoscaling is built for streaming workloads. It adds or removes workers based on task slot use and backlog, and shuts down underused nodes without disrupting processing. Serverless pipelines manage this for you.

A fixed cluster sized for the peak wastes money the rest of the day."""),

dict(d="Security & Compliance", q="""A production job currently runs as the engineer who created it. What is the recommended change, so the job keeps running when people leave and doesn't run with an individual's broad permissions?""",
a=["Set the job's Run as identity to a service principal that has only the privileges the job needs",
   "Share the engineer's personal access token with the team",
   "Make every job owner a workspace admin",
   "Run the job on a cluster in no isolation shared access mode"],
e="""A service principal is an identity for automation. Running production workloads as a service principal separates them from any one person, supports least privilege, and keeps them working when staff change. Set it through `run_as` in the job or in bundles.

Sharing a personal token or giving everyone admin rights goes against security best practice."""),

dict(d="Security & Compliance", q="""An external orchestrator such as Airflow must call the Databricks REST API to trigger jobs. Which authentication approach is recommended?""",
a=["OAuth machine-to-machine (M2M) with a service principal's client ID and secret (or workload identity federation), so short-lived tokens are issued automatically",
   "A personal access token created by a data engineer, with no expiration",
   "The workspace admin's username and password, using basic authentication",
   "An anonymous request from an allowed IP address"],
e="""For unattended automation, Databricks recommends OAuth M2M with service principals, or workload identity federation, which avoids long-lived secrets. Tokens are short-lived and are refreshed for you by the SDKs and CLI.

Long-lived personal tokens tied to a user are discouraged, and basic authentication with passwords isn't supported."""),

dict(d="Security & Compliance", q="""A newly acquired business unit loaded hundreds of tables into Unity Catalog, and nobody knows which columns hold sensitive data such as emails or credit card numbers. The governance team wants these columns found and tagged automatically.

Which feature should they use?""",
a=["Data classification in Unity Catalog, which scans tables, detects sensitive data, and suggests or applies tags",
   "Delta Lake file statistics, which flag columns that contain PII",
   "Lakehouse Federation, which classifies data in foreign catalogs",
   "`DESCRIBE HISTORY`, which lists the PII columns written in each commit"],
e="""Unity Catalog data classification uses automated detection to find sensitive data types in tables and tags the columns that contain them. Those tags can then drive ABAC masking policies.

File statistics only hold min, max, and null counts."""),

dict(d="Security & Compliance", q="""Security policy says the Databricks workspace UI and REST APIs may only be reached from the corporate network ranges. What should the workspace admin configure?""",
a=["Workspace IP access lists that allow only the corporate IP ranges",
   "A row filter on every table that checks the client IP address",
   "Cluster policies that require a particular instance type",
   "Secret ACLs on every secret scope"],
e="""IP access lists restrict which source IP addresses can reach the workspace's web application and REST APIs. Private connectivity (Private Link) can add further network isolation.

Row filters, cluster policies, and secret ACLs control different things."""),

dict(d="Security & Compliance", q="""The table `users` has Change Data Feed enabled. A data engineer deletes one user's rows to meet an erasure request. Where can that user's data still be found until it is cleaned up?""",
a=["In older table versions (through time travel) and in the Change Data Feed files under `_change_data`, until `VACUUM` removes them after the retention period",
   "Nowhere. A DELETE immediately removes the data from all files and logs.",
   "Only in the Spark UI of the cluster that ran the DELETE",
   "Only in the `_delta_log` JSON commit files, which keep a full copy of every row"],
e="""DELETE creates a new table version. Older data files are still reachable through time travel, and with CDF enabled the delete event itself, including the row's values, is written to the change data files. `VACUUM` removes those files once they are past the retention threshold.

The transaction log records file paths and metadata, not row data."""),
]
