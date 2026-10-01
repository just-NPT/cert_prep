Q = [
dict(d="Data Ingestion", q="""A new Auto Loader pipeline must backfill 5 TB of historical files on its first run, then process new files incrementally on each scheduled run. The team wants every micro-batch to stay a manageable size, including during the backfill.

Which configuration achieves this?""",
a=["Use `trigger(availableNow=True)` with `cloudFiles.maxBytesPerTrigger` (or `cloudFiles.maxFilesPerTrigger`) set to limit the size of each micro-batch.",
   "Use `trigger(once=True)` with `cloudFiles.maxBytesPerTrigger` set, so all available data is processed in exactly one micro-batch of limited size.",
   "Set `cloudFiles.includeExistingFiles` to `false`, so that only new files are processed.",
   "Increase `spark.sql.shuffle.partitions` so the 5 TB backfill is split into smaller micro-batches."],
e="""`availableNow` processes all data available when the query starts, then stops. Unlike the deprecated `once` trigger, it respects rate limits such as `maxBytesPerTrigger` and `maxFilesPerTrigger`, so the backfill runs as several micro-batches of controlled size.

`Trigger.Once` ignores these limits and processes everything in one batch. `includeExistingFiles=false` would skip the backfill entirely."""),

dict(d="Data Ingestion", q="""A partner delivers XML files to cloud storage, and each `<order>` element is one record. The data engineer wants to ingest these files incrementally into a Delta table using Auto Loader.

Which reader configuration should they use?""",
a=["""spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "xml")
  .option("rowTag", "order")
  .option("cloudFiles.schemaLocation", schema_path)
  .load(source_path)""",
   """spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "text")
  .load(source_path)
  .withColumn("order", regexp_extract("value", "<order>(.*)</order>", 1))""",
   """spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("multiLine", "true")
  .load(source_path)""",
   """spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "binaryFile")
  .option("rowTag", "order")
  .load(source_path)"""],
e="""Databricks Runtime supports XML natively, both as a batch data source and as an Auto Loader format. The `rowTag` option sets which element counts as one row. Schema inference and evolution work the same way as for JSON or CSV.

Parsing XML with regular expressions is fragile, and the JSON and binaryFile formats can't parse XML records."""),

dict(d="Data Ingestion", q="""For auditing, a bronze table must record which source file each row came from and when that file was last modified. Data is ingested with Auto Loader.

Which approach captures this information?""",
a=["""Select `_metadata.file_path` and `_metadata.file_modification_time` from the stream, for example: `.select("*", "_metadata.file_path", "_metadata.file_modification_time")`""",
   """Read the `_rescued_data` column, which contains the source file path for every row""",
   """Add `current_timestamp()` as `file_modification_time` and `lit(source_path)` as `file_path`""",
   """Call `spark.conf.get("cloudFiles.path")` in each micro-batch to get the name of the file being processed"""],
e="""File-based sources expose a hidden `_metadata` column with fields such as `file_path`, `file_name`, `file_size`, and `file_modification_time`. Select it explicitly to keep it.

- `_rescued_data` holds unparsed data, not file details.
- `current_timestamp()` records the processing time.
- `lit(source_path)` only gives the directory."""),

dict(d="Data Ingestion", q="""A Structured Streaming query has been reading a Kafka topic for weeks. To reprocess all retained messages, an engineer changed `startingOffsets` from `latest` to `earliest` and restarted the query with the same checkpoint. No old messages were reprocessed.

What explains this?""",
a=["`startingOffsets` only applies when a query starts with a new checkpoint. On restart, the query resumes from the offsets stored in its checkpoint.",
   "Kafka removes messages as soon as Spark reads them, so the earlier messages are gone.",
   "`earliest` only works together with `trigger(availableNow=True)`.",
   "The option has to be set on the `writeStream` side instead of the `readStream` side."],
e="""Once a query has a checkpoint, the stored offsets decide where it resumes, and options such as `startingOffsets` are ignored. To reprocess, start the query with a new checkpoint location, usually after clearing or versioning the target. The data you can reprocess is limited by the topic's retention.

Kafka keeps messages according to its retention policy, not according to whether they were consumed."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming job keeps running totals for about 50 million product keys in a Delta table. Each micro-batch touches only a few thousand keys. The team needs the target table updated after every micro-batch, at the lowest cost.

Which design should they use?""",
a=["Use `outputMode(\"update\")` with `foreachBatch`, and MERGE each micro-batch's changed aggregates into the target table.",
   "Use `outputMode(\"complete\")`, so the full 50-million-row result is rewritten to the table in every micro-batch.",
   "Use `outputMode(\"append\")` with no watermark, so every changed total is appended as a new row.",
   "Write the aggregates to a temporary view and run `INSERT OVERWRITE` from a separate job every minute."],
e="""Update mode emits only the rows that changed in a micro-batch. A Delta sink doesn't support update mode directly, so `foreachBatch` with MERGE is the standard way to upsert those rows.

- Complete mode rewrites the entire result every time, which is expensive at this scale.
- Append mode on an aggregation requires a watermark and only emits windows that are final."""),

dict(d="Transformation, Cleansing & Quality", q="""A data engineer needs to change a running streaming query and restart it from its existing checkpoint. Which change is NOT supported when restarting from the same checkpoint?""",
a=["Changing the grouping keys of a stateful aggregation",
   "Changing the processing-time trigger interval",
   "Adding a stateless `filter()` on the input stream",
   "Changing `maxFilesPerTrigger` on the file source"],
e="""The checkpoint stores state whose schema depends on the stateful operations. Changing the grouping keys, aggregate functions, or other stateful operators makes the existing state incompatible, so you need a new checkpoint.

Triggers, rate limits, and most stateless projections and filters can usually be changed between restarts."""),

dict(d="Transformation, Cleansing & Quality", q="""A bronze streaming table in an SDP pipeline ingests files from a landing zone that deletes files after 14 days. If someone ran a full refresh on this table, more than 14 days of history would be lost permanently.

How can the team prevent a full refresh of this table?""",
a=["Set the table property `pipelines.reset.allowed` to `false` on the bronze streaming table.",
   "Set the table property `delta.appendOnly` to `true` on the bronze streaming table.",
   "Run the pipeline in triggered mode instead of continuous mode.",
   "Give the bronze table the expectation `ON VIOLATION FAIL UPDATE`."],
e="""A full refresh clears a streaming table and reprocesses all data still available in the source. Setting `pipelines.reset.allowed = false` excludes the table from full refreshes, while other tables in the pipeline can still be reset.

`appendOnly` blocks updates and deletes, not a reset. The pipeline mode and expectations have nothing to do with full refresh."""),

dict(d="Transformation, Cleansing & Quality", q="""A gold table must show sales totals per region, aggregated from a silver table. The silver table regularly gets updates and deletes from late corrections, and the gold table must reflect them.

Which SDP dataset type should define the gold table?""",
a=["A materialized view that aggregates the silver table",
   "A streaming table that reads the silver table with `STREAM(silver_sales)`",
   "A temporary view that is recomputed only when the pipeline starts",
   "An append flow that adds each new silver record to the gold table"],
e="""A materialized view always reflects the current state of its sources. It recomputes or incrementally refreshes as needed, so it handles updates and deletes.

Streaming tables assume an append-only source. Updates or deletes upstream break the stream unless they are skipped, and then the gold totals would be wrong."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming table in an SDP pipeline ingests orders from two Kafka topics, `orders_eu` and `orders_us`. Next quarter, a third topic, `orders_apac`, will be added, and the team wants to add it without a full refresh of the table.

Which design supports this?""",
a=["Create the streaming table, then define a separate append flow for each topic that writes into it, adding a new append flow for `orders_apac` later.",
   "Define the streaming table as a `UNION ALL` of the topic streams, and add `orders_apac` to the union later.",
   "Define the table as a materialized view over the topics, and add the new topic to its query.",
   "Write the three topics to separate tables, and join them in a gold materialized view."],
e="""Append flows (`CREATE FLOW ... INSERT INTO ... BY NAME` or `@dp.append_flow`) let several streaming sources write to one streaming table, and each flow has its own checkpoint. You can add a new flow without resetting the existing ones.

Changing a `UNION` in a streaming query changes its checkpointed plan, which normally needs a full refresh."""),

dict(d="Transformation, Cleansing & Quality", q="""An AUTO CDC flow keeps an SCD Type 1 table up to date. The source feed has an `operation` column with the values `INSERT`, `UPDATE`, and `DELETE`.

Which clause makes DELETE events remove the matching rows from the target?""",
a=["""APPLY AS DELETE WHEN operation = "DELETE\"""",
   """TRACK HISTORY ON * EXCEPT (operation)""",
   """CONSTRAINT no_deletes EXPECT (operation <> "DELETE") ON VIOLATION DROP ROW""",
   """WHERE operation <> "DELETE\""""],
e="""In AUTO CDC, `APPLY AS DELETE WHEN <condition>` marks which source events are deletes. Matching rows are removed from an SCD Type 1 target. In SCD Type 2, they close the current version instead.

Filtering or dropping the delete events would leave the deleted rows in the target. `TRACK HISTORY ON` only applies to SCD Type 2."""),

dict(d="Transformation, Cleansing & Quality", q="""An AUTO CDC flow keeps an SCD Type 2 table of user profiles. The source updates `last_login_ts` on almost every event, which creates a flood of new history versions. History should only be kept for changes to the other columns.

Which clause should be added?""",
a=["`TRACK HISTORY ON * EXCEPT (last_login_ts)`",
   "`COLUMNS * EXCEPT (last_login_ts)`",
   "`SEQUENCE BY last_login_ts`",
   "`APPLY AS TRUNCATE WHEN last_login_ts IS NOT NULL`"],
e="""In SCD Type 2, `TRACK HISTORY ON` lists the columns whose changes create a new version. A change to a column outside the list updates the current row in place, without a new history row.

`COLUMNS * EXCEPT` would remove the column from the target entirely. `SEQUENCE BY` sets the event order. `APPLY AS TRUNCATE` only applies to SCD Type 1."""),

dict(d="Cost & Performance Optimization", q="""The optimizer keeps choosing a poor join order for a query that joins five large Unity Catalog tables. The team suspects missing table and column statistics.

What should they do?""",
a=["Run `ANALYZE TABLE ... COMPUTE STATISTICS FOR ALL COLUMNS` on the tables, or let predictive optimization collect the statistics automatically, so the cost-based optimizer has accurate estimates.",
   "Run `VACUUM` on each table so the optimizer reads fewer files when planning.",
   "Turn on Change Data Feed on each table so the optimizer can track row counts.",
   "Set `spark.sql.autoBroadcastJoinThreshold` to `-1` so the optimizer stops estimating table sizes."],
e="""The cost-based optimizer uses table and column statistics (row counts, distinct counts, min/max, nulls) to estimate how many rows each join produces and to pick join orders and strategies. `ANALYZE TABLE` collects these statistics, and predictive optimization can run it automatically on managed tables.

The other options don't give the optimizer better estimates."""),

dict(d="Cost & Performance Optimization", q="""A serverless SQL warehouse serves dashboards for about 50 concurrent users. Each query is small and fast, but at peak times queries spend a long time queued before they start.

Which change addresses this most directly?""",
a=["Increase the warehouse's maximum number of clusters so it can scale out for more concurrent queries.",
   "Increase the warehouse's cluster size (T-shirt size) while keeping it at a single cluster.",
   "Lower the auto-stop timeout so the warehouse restarts more often.",
   "Turn off the warehouse's result cache so every query runs fresh."],
e="""Queueing with many concurrent small queries is a concurrency problem. Scaling out by allowing more clusters lets more queries run at once.

A larger cluster size helps big, complex queries finish faster, but adds less concurrency for small ones. Auto-stop and caching changes won't reduce queueing."""),

dict(d="Cost & Performance Optimization", q="""A daily MERGE upserts the last three days of events into a 10 TB `events` table, which is clustered by `event_date`. The query profile shows that the MERGE scans the entire table.

Which change most effectively reduces the data scanned?""",
a=["Add a predicate on the clustering column to the `ON` clause, for example `AND t.event_date >= current_date() - INTERVAL 3 DAYS`.",
   "Move the date condition into the `WHEN MATCHED` clause as `WHEN MATCHED AND t.event_date >= ...`.",
   "Run `VACUUM events` before every MERGE.",
   "Double the cluster size so the full scan finishes faster."],
e="""The MERGE `ON` condition decides which target files must be read. A predicate on a clustering or partition column lets Delta skip files that can't match.

Conditions in `WHEN MATCHED` are applied after the join, so they don't reduce the scan. VACUUM removes old, unreferenced files, not the files a query reads."""),

dict(d="Security & Compliance", q="""A security team must find out who granted or revoked privileges on the `finance` catalog in the last 30 days. Which source should they query?""",
a=["`system.access.audit`, filtered on Unity Catalog permission-change events (for example, `action_name = 'updatePermissions'`)",
   "`system.access.table_lineage`, filtered on the `finance` catalog",
   "The output of `DESCRIBE HISTORY` for each table in the `finance` catalog",
   "`finance.information_schema.table_privileges`, which keeps a history of past grants"],
e="""Audit logs (`system.access.audit`) record account and workspace events, including Unity Catalog permission changes, with the user who did it, the time, and the request details.

Lineage tracks data flow. `DESCRIBE HISTORY` covers table writes. `information_schema` privilege views show only current grants, not past ones."""),
]
