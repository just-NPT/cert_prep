Q = [
dict(d="Monitoring & Alerting", q="""A data engineer called `df.cache()` on a large DataFrame and wants to check how much of it is actually held in memory across the executors. Where can they see this?""",
a=["The Storage tab of the Spark UI, which shows each cached dataset's fraction cached and its size in memory and on disk",
   "The Jobs tab of the Spark UI, under the Event Timeline",
   "The table's `DESCRIBE DETAIL` output",
   "`system.billing.usage`"],
e="""The Storage tab lists persisted RDDs and DataFrames with their storage level, the number of cached partitions, the fraction cached, and their memory and disk sizes. It helps you see whether a cache fits or is being evicted.

Caching is lazy, so nothing appears until an action has run."""),

dict(d="Monitoring & Alerting", q="""A stateful streaming query uses more and more memory over time. The engineer wants to check, from code, how many state rows the query is holding. Which field should they look at?""",
a=["`query.lastProgress[\"stateOperators\"]`, for example the `numRowsTotal` and `memoryUsedBytes` values",
   "`query.status[\"isDataAvailable\"]`",
   "`query.lastProgress[\"sources\"][0][\"endOffset\"]`",
   "`query.exception()`"],
e="""Every `StreamingQueryProgress` includes a `stateOperators` entry for each stateful operator, with total state rows, rows updated, and memory used. A steady increase usually means a missing or too-long watermark.

The status and source offsets don't describe the size of the state."""),

dict(d="Monitoring & Alerting", q="""A job runs a continuous Auto Loader stream. The team wants an alert when the stream falls more than 15 minutes behind the incoming data. What can they configure in the job itself?""",
a=["A streaming backlog health rule (for example, on backlog seconds) with a notification for when the threshold is exceeded",
   "A job timeout of 15 minutes",
   "An email notification for job success",
   "A retry policy with a 15-minute delay between retries"],
e="""For streaming tasks, jobs support health rules on backlog metrics, such as backlog seconds, bytes, records, or files. When a threshold is crossed, a notification is sent while the stream keeps running.

A timeout would stop a continuous stream, and success notifications never fire for a stream that runs indefinitely."""),

dict(d="Monitoring & Alerting", q="""Finance wants an email when a business unit's Databricks spend reaches set thresholds of its monthly limit. Which feature fits best?""",
a=["Budgets in the account console, filtered by the business unit's tags, with email alerts at spending thresholds",
   "A cluster policy that limits each cluster to 10 workers",
   "An SDP expectation on the billing tables",
   "Turning on Photon for all clusters"],
e="""Account budgets track spending, filtered by workspaces or tags, against a target, and send email alerts when thresholds are reached. For more detail, you can also build SQL alerts on `system.billing.usage`.

Cluster policies limit configurations, not spending."""),

dict(d="Monitoring & Alerting", q="""A job failed overnight, and its job cluster has since terminated. The engineer wants to look at the stages and tasks of the failed Spark job. What is the right approach?""",
a=["Open the failed task run in the job's run history and go to its Spark UI, which stays available after the cluster terminates",
   "Restart the job cluster by hand. The Spark UI is only available while the cluster is running.",
   "Run `DESCRIBE HISTORY` on the output table to see the stage details",
   "Look for the stage details in `system.billing.usage`"],
e="""Databricks keeps the Spark UI (history) and logs for terminated job clusters for a time, and you can reach them from the task run's page. For long-term retention, set up cluster log delivery.

Delta history and billing tables don't contain execution details."""),

dict(d="Cost & Performance Optimization", q="""A team enables deletion vectors on a large table that gets many small UPDATE and DELETE operations. Which trade-off should they expect?""",
a=["Writes are much faster because files aren't rewritten, but reads must apply the deletion vectors, so maintenance such as `OPTIMIZE` or purging should run regularly to keep reads efficient.",
   "Both reads and writes are slower, but storage costs go down.",
   "Deletion vectors make the table read-only for streaming queries.",
   "There's no trade-off. Deletion vectors make every operation faster, and no maintenance is needed."],
e="""Deletion vectors use merge-on-read: deletes and updates mark rows as invalid instead of rewriting whole Parquet files. Reads filter out those rows, which adds a little overhead as deletion vectors build up. Compaction (`OPTIMIZE`, `REORG ... APPLY (PURGE)`) applies them to the files. Predictive optimization can do this automatically."""),

dict(d="Cost & Performance Optimization", q="""A join between a 2 TB table and a 3 GB table runs as a sort-merge join, and the sort step dominates the runtime. The 3 GB table is too large to broadcast. Which hint might reduce the cost by avoiding the sort?""",
a=["`/*+ SHUFFLE_HASH(small_tbl) */`",
   "`/*+ BROADCAST(big_tbl) */`",
   "`/*+ MERGE(small_tbl) */`",
   "`/*+ COALESCE(1) */`"],
e="""A shuffle hash join shuffles both sides and builds a hash table from the smaller side's partitions, so no sort is needed. It works well when the build side's partitions fit in memory.

`MERGE` forces the sort-merge join that is already in use. Broadcasting the large table is wrong. `COALESCE` is a partitioning hint."""),

dict(d="Cost & Performance Optimization", q="""Dashboards on a classic cluster run many queries over the same subset of a table each morning. The team wants that data loaded into the disk cache before users arrive. Which command does this?""",
a=["`CACHE SELECT * FROM sales.orders WHERE order_date >= current_date() - INTERVAL 30 DAYS`",
   "`OPTIMIZE sales.orders`",
   "`ANALYZE TABLE sales.orders COMPUTE STATISTICS`",
   "`REFRESH TABLE sales.orders`"],
e="""`CACHE SELECT` loads the selected data into the Databricks disk cache on the workers ahead of time, so later queries read from local SSD.

`OPTIMIZE` compacts files, `ANALYZE` collects statistics, and `REFRESH TABLE` clears cached metadata."""),

dict(d="Cost & Performance Optimization", q="""A notebook builds an expensive DataFrame `enriched`, made from several joins, and then runs five different aggregations on it, each followed by an action. Each action takes as long as running the whole pipeline from scratch.

What is the most effective change?""",
a=["Persist `enriched` (for example with `enriched.cache()`) before the five actions, and unpersist it afterwards.",
   "Call `enriched.count()` before every aggregation.",
   "Turn off Adaptive Query Execution.",
   "Use `repartition(1)` on `enriched` so that the aggregations run on one partition."],
e="""Spark evaluates lazily, so each action runs the whole lineage again, joins included. Persisting the shared intermediate result computes it once.

Extra `count()` calls add work unless the data is cached. A single partition removes parallelism."""),

dict(d="Cost & Performance Optimization", q="""The team turned on predictive optimization for the catalog that holds their Unity Catalog managed tables. Should they keep their scheduled `OPTIMIZE` and `VACUUM` jobs for those tables?""",
a=["No. Predictive optimization runs `OPTIMIZE`, `VACUUM`, and `ANALYZE` automatically on managed tables, so the manual jobs can usually be removed. External tables still need their own maintenance.",
   "Yes. Predictive optimization only collects statistics and never runs `OPTIMIZE` or `VACUUM`.",
   "Yes. Predictive optimization only applies to external tables.",
   "No. Predictive optimization makes `OPTIMIZE` and `VACUUM` unnecessary for every table in the metastore, including external tables."],
e="""Predictive optimization uses usage patterns to decide when to run maintenance, such as compaction, clustering, vacuuming, and statistics collection, on Unity Catalog managed tables. It doesn't cover external tables. You can see what it has done in `system.storage.predictive_optimization_operations_history`."""),

dict(d="Cost & Performance Optimization", q="""A source system stores `event_date` as a STRING in `MM/dd/yyyy` format, and the column was loaded as is. Range filters such as `event_date >= '01/01/2025'` give wrong results and skip few files.

What is the best fix?""",
a=["Convert the column to the DATE type during ingestion (for example, `to_date(event_date, 'MM/dd/yyyy')`), so range comparisons and file statistics work correctly",
   "Turn on Change Data Feed on the table",
   "Z-order the table on the string column",
   "Increase `spark.sql.shuffle.partitions`"],
e="""Strings compare character by character, so `'12/31/2024' > '01/01/2025'`. That breaks range filters, and the min/max statistics used for data skipping don't line up with real date order. Using proper types such as DATE, TIMESTAMP, and numeric types gives correct semantics and effective skipping."""),

dict(d="Cost & Performance Optimization", q="""The data sizes of a set of jobs vary widely from run to run, and no single value of `spark.sql.shuffle.partitions` works well for all of them. What does Databricks offer for this?""",
a=["Set `spark.sql.shuffle.partitions` to `auto`, which lets auto-optimized shuffle choose the number of partitions from the data size",
   "Set `spark.sql.shuffle.partitions` to the number of driver cores",
   "Turn off Adaptive Query Execution, so Spark uses the initial plan",
   "Set `spark.sql.files.maxPartitionBytes` to `auto`"],
e="""On Databricks, `spark.sql.shuffle.partitions = auto` turns on auto-optimized shuffle, which picks the initial number of shuffle partitions from the data size. AQE then coalesces partitions as needed. This removes the need to tune the value per job."""),

dict(d="Security & Compliance", q="""A team protects sensitive rows with a dynamic view, but some users still have `SELECT` on the base table. The security team wants filtering that applies no matter how the data is accessed. What should be used instead?""",
a=["A row filter attached directly to the base table, which applies to every query against the table",
   "A second dynamic view on top of the first",
   "A CHECK constraint that blocks reading rows the user can't see",
   "A comment on the base table that tells users to query the view"],
e="""A dynamic view only protects users who query the view. Anyone with `SELECT` on the base table can get around it. A row filter (or column mask) is attached to the table itself, so Unity Catalog applies it to every query.

CHECK constraints validate writes and don't control reads."""),

dict(d="Security & Compliance", q="""The service principal for a production job reads `prod.bronze.events` and writes to the existing table `prod.silver.events`. What is the minimum set of privileges it needs?""",
a=["`USE CATALOG` on `prod`, `USE SCHEMA` on both schemas, `SELECT` on `bronze.events`, and `SELECT` and `MODIFY` on `silver.events`",
   "`ALL PRIVILEGES` on the `prod` catalog",
   "Metastore admin",
   "`SELECT` on both tables only"],
e="""Least privilege means granting only what the job needs: access to the namespace (`USE CATALOG` and `USE SCHEMA`), read on the source, and read and write on the target. MERGE and UPDATE also need `SELECT` on the target.

`SELECT` on its own lacks the namespace privileges and the write access."""),

dict(d="Security & Compliance", q="""Analysts must be able to join datasets on a pseudonymized email. A plain `sha2(email, 256)` is considered weak, because anyone could hash known email addresses and match them. How can the pseudonymization be strengthened?""",
a=["Hash the email with a secret salt, for example `sha2(concat(email, secret('pii', 'salt')), 256)`, and keep the salt in a restricted secret scope",
   "Use `md5(email)` instead of SHA-256",
   "Use `base64(email)` instead of a hash",
   "Hash the email twice: `sha2(sha2(email, 256), 256)`"],
e="""A secret salt (or a keyed hash, like an HMAC) means outsiders can't recompute the tokens from known emails. Equal inputs still give equal tokens, so the data stays joinable.

MD5 and double hashing without a secret can still be precomputed, and Base64 is just an encoding."""),
]
