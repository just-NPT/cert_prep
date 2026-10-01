Q = [
dict(d="Data Sharing & Federation", k=2, q="""A provider shares the Delta table `orders`, which has Change Data Feed enabled, with a Databricks recipient (Databricks-to-Databricks sharing) using `WITH HISTORY`.

Which two capabilities does `WITH HISTORY` give the recipient? Choose 2 answers:""",
a=["Querying earlier versions of the shared table with time travel",
   "Reading the shared table with Structured Streaming, including reading its Change Data Feed",
   "Querying the current version of the shared table",
   "Writing changes back to the provider's table",
   "Running `VACUUM` on the provider's table to free storage"],
e="""When a table is shared `WITH HISTORY`, the recipient can access its history. That enables time travel queries and streaming reads, including the Change Data Feed when CDF is enabled on the source table. It can also improve read performance.

Reading the current version works without history. Shared data is always read-only for recipients."""),

dict(d="Cost & Performance Optimization", q="""A team is deciding which workloads to run on Photon-enabled compute. Which workload is likely to benefit the least from Photon?""",
a=["A pipeline that spends most of its time in row-at-a-time Python UDFs and RDD transformations",
   "Large joins and aggregations over Delta tables written in Spark SQL",
   "Large Delta `MERGE` operations that upsert millions of rows",
   "Wide scans of Parquet and Delta data with selective filters"],
e="""Photon is a vectorized native engine that speeds up SQL and DataFrame operations such as scans, filters, joins, aggregations, and Delta writes and MERGE.

Code Photon can't run, such as Python UDFs and RDD operations, falls back to the standard engine, so those workloads gain little."""),

dict(d="Cost & Performance Optimization", q="""Which statement correctly compares the Databricks disk cache with Spark caching (`df.cache()`)?""",
a=["The disk cache automatically keeps copies of remote Parquet and Delta data files on the workers' local SSDs and notices when files change. Spark caching stores a DataFrame result that you have to manage and unpersist yourself.",
   "Both caches keep data only in JVM heap memory and are lost after every query.",
   "The disk cache stores query results, while Spark caching stores raw data files.",
   "Spark caching is refreshed automatically when the underlying Delta table changes, but the disk cache must be cleared by hand."],
e="""The disk cache (formerly Delta cache) speeds up repeated reads of remote files by caching them on local SSD. It works transparently and stays consistent when files change.

`df.cache()` and `persist()` store a computed DataFrame in memory or on disk. They use executor memory, are not refreshed when the source changes, and should be unpersisted when no longer needed."""),

dict(d="Cost & Performance Optimization", q="""After a shuffle, a stage runs 2,000 tasks, and each task processes only about 1 MB of data. Most of the stage's time goes to task scheduling overhead.

Which setting addresses this most directly?""",
a=["Enable Adaptive Query Execution partition coalescing so small shuffle partitions are combined into fewer, larger ones at runtime.",
   "Increase `spark.sql.shuffle.partitions` to 8,000.",
   "Add a `BROADCAST` hint to both sides of every join in the query.",
   "Call `repartition(10000)` before the shuffle."],
e="""AQE can coalesce post-shuffle partitions based on their actual sizes at runtime (`spark.sql.adaptive.coalescePartitions.enabled`). This reduces the number of tiny tasks.

Raising the partition count or repartitioning to more partitions makes the problem worse, and broadcast hints don't apply to every join."""),

dict(d="Transformation, Cleansing & Quality", q="""A data engineer uses the Python API of Lakeflow Spark Declarative Pipelines and needs to drop records that break either of two rules: `id IS NOT NULL` and `qty > 0`.

Which definition does this?""",
a=["""@dp.table
@dp.expect_all_or_drop({"valid_id": "id IS NOT NULL", "valid_qty": "qty > 0"})
def silver_items():
    return spark.readStream.table("bronze_items")""",
   """@dp.table
@dp.expect_all({"valid_id": "id IS NOT NULL", "valid_qty": "qty > 0"})
def silver_items():
    return spark.readStream.table("bronze_items")""",
   """@dp.table
@dp.expect_all_or_fail({"valid_id": "id IS NOT NULL", "valid_qty": "qty > 0"})
def silver_items():
    return spark.readStream.table("bronze_items")""",
   """@dp.table
@dp.expect_or_drop("valid_id AND valid_qty", "id IS NOT NULL, qty > 0")
def silver_items():
    return spark.readStream.table("bronze_items")"""],
e="""`expect_all_or_drop` takes a dictionary that maps expectation names to SQL conditions, and drops any record that fails one of them. Each expectation's metrics are reported separately.

- `expect_all` only warns.
- `expect_all_or_fail` stops the update.
- `expect_or_drop` takes a single name and a single condition."""),

dict(d="Transformation, Cleansing & Quality", q="""The `orders` table has Change Data Feed enabled. A downstream batch job needs the current values of every row inserted or updated since table version 12. Rows that were deleted and the "before" image of updates must be left out.

Which query returns this?""",
a=["""SELECT * FROM table_changes('orders', 12)
WHERE _change_type IN ('insert', 'update_postimage')""",
   """SELECT * FROM table_changes('orders', 12)
WHERE _change_type IN ('insert', 'update_preimage')""",
   """SELECT * FROM orders VERSION AS OF 12
WHERE _change_type <> 'delete'""",
   """SELECT * FROM table_changes('orders', 12)
WHERE _change_type = 'update'"""],
e="""`table_changes()` returns the change data with the metadata columns `_change_type`, `_commit_version`, and `_commit_timestamp`. An update produces an `update_preimage` row (the old values) and an `update_postimage` row (the new values). To get current values, keep `insert` and `update_postimage`.

Time travel reads a snapshot and has no `_change_type` column."""),

dict(d="Transformation, Cleansing & Quality", q="""The source of a daily SQL MERGE now includes a new column, `loyalty_tier`. The team wants this MERGE to add the column to the target table automatically, without changing the session configuration for other statements.

Which statement should they use?""",
a=["""MERGE WITH SCHEMA EVOLUTION INTO customers t
USING updates s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO customers t OPTIONS ('mergeSchema' = 'true')
USING updates s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """ALTER TABLE customers SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
MERGE INTO customers t USING updates s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO customers t
USING updates s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WITH overwriteSchema = true"""],
e="""`MERGE WITH SCHEMA EVOLUTION` turns on automatic schema evolution for that one statement, so new source columns are added to the target. You could also set `spark.databricks.delta.schema.autoMerge.enabled`, but that affects the whole session.

Column mapping is needed to rename or drop columns, not to add them. The other forms are not valid MERGE syntax."""),

dict(d="Data Ingestion", q="""Auto Loader infers the `amount` column of incoming JSON files as DOUBLE, but the target requires `DECIMAL(18,2)`. All other columns should still be inferred automatically.

Which option should be added to the stream?""",
a=["""`.option("cloudFiles.schemaHints", "amount DECIMAL(18,2)")`""",
   """`.option("cloudFiles.inferColumnTypes", "false")`""",
   """`.option("mergeSchema", "true")`""",
   """`.option("cloudFiles.schemaEvolutionMode", "rescue")`"""],
e="""Schema hints override the inferred types of specific columns while the rest of the schema is still inferred. They are useful for precise types such as decimals or timestamps.

Turning off `inferColumnTypes` makes every JSON column a STRING. The other options control schema evolution, not column types."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming job reads the Delta table `silver_orders` as a source. A nightly maintenance job now runs GDPR `DELETE` statements on that table, and the stream fails with an error about a data update or deletion it can't handle.

The downstream table only needs newly appended records. Which option lets the stream keep running?""",
a=["""`.option("skipChangeCommits", "true")` on the streaming read""",
   """`.option("ignoreMissingFiles", "true")` on the streaming read""",
   """`.option("maxFilesPerTrigger", 1)` on the streaming read""",
   """`.option("startingVersion", "latest")` on the streaming read"""],
e="""A Delta streaming source expects append-only data by default. `skipChangeCommits` tells the stream to ignore transactions that delete or modify existing records, so it only processes appends.

If the deletes have to be propagated downstream, read the Change Data Feed instead. The other options don't change how commits that modify data are handled."""),

dict(d="Monitoring & Alerting", q="""An operations team needs a Slack notification whenever more than 100 records have been quarantined in the last hour. The check should run every 15 minutes.

Which solution fits best?""",
a=["Write a SQL query that counts quarantined records from the last hour, create a Databricks SQL alert on it with the condition `> 100` and a 15-minute schedule, and send it to a Slack notification destination.",
   "Add an email notification for job failures to the ingestion job, and forward the emails to Slack.",
   "Turn on data profiling (Lakehouse Monitoring) on the quarantine table, and wait for the daily drift metrics.",
   "Change the quarantine expectations to `ON VIOLATION FAIL UPDATE`, so the pipeline fails when bad records appear."],
e="""Databricks SQL alerts run a query on a schedule, compare the result to a condition, and notify destinations such as email, Slack, Teams, PagerDuty, or webhooks.

Job failure notifications don't fire on data thresholds, and making the pipeline fail would stop processing for everyone."""),

dict(d="Monitoring & Alerting", q="""A team enables data profiling (Lakehouse Monitoring) with a TimeSeries profile on a Unity Catalog table. Which outputs are created automatically?""",
a=["A profile metrics table, a drift metrics table, and a dashboard that visualizes them",
   "A quarantine table that holds the rows that fail the profile",
   "A set of pipeline expectations added to the table's source pipeline",
   "A Change Data Feed on the monitored table that records every metric change"],
e="""When you create a monitor, Databricks generates two metric tables, `<table>_profile_metrics` (summary statistics) and `<table>_drift_metrics` (changes over time), plus a dashboard. You can add custom metrics and create SQL alerts on the metric tables.

A TimeSeries profile needs a timestamp column and computes metrics for each time window."""),

dict(d="Monitoring & Alerting", q="""A data engineer wants a SQL query that lists all failed job runs in the workspace from the last 7 days, with their start and end times. Which system table should they query?""",
a=["`system.lakeflow.job_run_timeline`",
   "`system.compute.clusters`",
   "`system.billing.usage`",
   "`system.storage.predictive_optimization_operations_history`"],
e="""The Lakeflow system tables record job information:

- `system.lakeflow.jobs` and `system.lakeflow.job_tasks` hold job definitions.
- `system.lakeflow.job_run_timeline` and `system.lakeflow.job_task_run_timeline` hold run start and end times and `result_state`.

Filter on `result_state = 'FAILED'` and `period_start_time` to find recent failures."""),

dict(d="Developing Code (Python & SQL)", q="""The `customer_updates` table has several rows for each `customer_id`. Which query returns only the most recent row for each customer, based on `updated_at`?""",
a=["""SELECT * FROM customer_updates
QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1""",
   """SELECT * FROM customer_updates
WHERE row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1""",
   """SELECT * FROM customer_updates
GROUP BY customer_id
HAVING updated_at = max(updated_at)""",
   """SELECT customer_id, max(*) FROM customer_updates
GROUP BY customer_id"""],
e="""`QUALIFY` filters on the results of window functions, much as `HAVING` filters on aggregates. Window functions can't appear in `WHERE`, because WHERE is evaluated before windows are computed.

The `GROUP BY` versions are invalid, since they select columns that are neither grouped nor aggregated."""),

dict(d="Developing Code (Python & SQL)", q="""The `orders` table has a column `items ARRAY<STRUCT<sku STRING, qty INT, price DOUBLE>>`. The engineer needs each order's total (`qty × price` summed over all items) without exploding the array.

Which expression computes it?""",
a=["""aggregate(items, 0D, (acc, x) -> acc + x.qty * x.price)""",
   """transform(items, x -> x.qty * x.price)""",
   """sum(items.qty * items.price)""",
   """filter(items, x -> x.qty * x.price > 0)"""],
e="""Higher-order functions work on arrays directly. `aggregate(array, start, merge)` reduces an array to a single value. The start value `0D` is a DOUBLE zero, so it matches the type of the products.

`transform` returns an array of line amounts, not a total. `filter` returns a subset of the array. `sum` is an aggregate over rows, not over array elements."""),
]
