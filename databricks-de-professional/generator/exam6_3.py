Q = [
dict(d="Developing Code (Python & SQL)", q="""A developer wants to write PySpark code in a local IDE, set breakpoints, and run pytest suites locally, while the Spark code itself runs on Databricks compute against Unity Catalog data.

Which tool supports this workflow?""",
a=["Databricks Connect",
   "Databricks SQL Driver for JDBC",
   "The Databricks web terminal",
   "Delta Sharing Python connector"],
e="""Databricks Connect lets IDEs and local Python processes run Spark code on remote Databricks clusters or serverless compute. You can debug interactively and run unit tests locally while the work runs on Databricks.

The JDBC driver runs SQL only. The web terminal runs inside the workspace. Delta Sharing reads shared data."""),

dict(d="Developing Code (Python & SQL)", q="""A Python function builds SQL from user input:

```
spark.sql(f"SELECT * FROM {table_name} WHERE region = '{region}'")
```

A security review flags this as vulnerable to SQL injection. Which rewrite is safe and still supports a dynamic table name?""",
a=["""spark.sql("SELECT * FROM IDENTIFIER(:tbl) WHERE region = :region",
          args={"tbl": table_name, "region": region})""",
   """spark.sql("SELECT * FROM {} WHERE region = '{}'".format(table_name, region))""",
   """spark.sql("SELECT * FROM " + table_name + " WHERE region = '" + region.replace("'", "") + "'")""",
   """spark.sql(f"SELECT * FROM `{table_name}` WHERE region = \\"{region}\\"")"""],
e="""Named parameter markers (`:name`, values passed in `args`) bind values safely instead of splicing them into the SQL text. `IDENTIFIER()` turns a parameter into a table or column name safely.

String formatting or concatenation, even with some sanitizing, can still be exploited."""),

dict(d="Data Ingestion", q="""A SQL-only team wants to incrementally ingest new JSON files from the volume `/Volumes/main/raw/clicks/` into a table, without writing any Python. Which statement does this?""",
a=["""CREATE OR REFRESH STREAMING TABLE bronze_clicks AS
SELECT * FROM STREAM read_files('/Volumes/main/raw/clicks/', format => 'json');""",
   """CREATE OR REPLACE TABLE bronze_clicks AS
SELECT * FROM read_files('/Volumes/main/raw/clicks/', format => 'json');""",
   """CREATE OR REFRESH MATERIALIZED VIEW bronze_clicks AS
SELECT * FROM json.`/Volumes/main/raw/clicks/`;""",
   """CREATE VIEW bronze_clicks AS
SELECT * FROM STREAM json.`/Volumes/main/raw/clicks/`;"""],
e="""`read_files` used inside `STREAM` in a streaming table uses Auto Loader underneath, so each refresh processes only the new files.

A CTAS with `read_files` reloads every file each time it runs. The materialized view and view versions don't ingest incrementally into a stored table."""),

dict(d="Data Ingestion", q="""After an outage, a Structured Streaming query that reads a Kafka topic has a large backlog. The first micro-batch tries to read millions of messages and runs out of memory.

Which option limits how much data each micro-batch reads from Kafka?""",
a=["`maxOffsetsPerTrigger`",
   "`maxFilesPerTrigger`",
   "`cloudFiles.maxBytesPerTrigger`",
   "`spark.sql.shuffle.partitions`"],
e="""For the Kafka source, `maxOffsetsPerTrigger` caps the total number of offsets (messages) read per trigger, spread across topic partitions.

`maxFilesPerTrigger` applies to file and Delta sources, and the `cloudFiles.*` options apply to Auto Loader."""),

dict(d="Data Ingestion", q="""A streaming job must publish alert records from a DataFrame `alerts` to the Kafka topic `alerts-out` as JSON messages. Which code does this?""",
a=["""(alerts.select(to_json(struct("*")).alias("value"))
   .writeStream.format("kafka")
   .option("kafka.bootstrap.servers", brokers)
   .option("topic", "alerts-out")
   .option("checkpointLocation", cp)
   .start())""",
   """(alerts.writeStream.format("kafka")
   .option("kafka.bootstrap.servers", brokers)
   .option("topic", "alerts-out")
   .option("checkpointLocation", cp)
   .start())""",
   """(alerts.select(to_json(struct("*")).alias("message"))
   .writeStream.format("kafka")
   .option("kafka.bootstrap.servers", brokers)
   .option("topic", "alerts-out")
   .start())""",
   """(alerts.writeStream.format("json")
   .option("path", "kafka://alerts-out")
   .option("checkpointLocation", cp)
   .start())"""],
e="""The Kafka sink expects a `value` column (STRING or BINARY), plus an optional `key` and other optional columns. Serialize the record into `value`, for example with `to_json(struct(...))`, and provide a checkpoint location.

Writing arbitrary columns, or a column with any other name, fails."""),

dict(d="Transformation, Cleansing & Quality", q="""A nightly batch reads large JSON files in which a few records are malformed. The job must not fail, valid records must be loaded, and malformed records must be kept for investigation.

Which reader option should be used?""",
a=["""`.option("badRecordsPath", "/Volumes/main/ops/bad_records")`""",
   """`.option("mode", "FAILFAST")`""",
   """`.option("mode", "DROPMALFORMED")`""",
   """`.option("mergeSchema", "true")`"""],
e="""On Databricks, `badRecordsPath` writes unparseable records, and files that can't be read, to a separate location with exception details, while the valid rows are loaded. (`PERMISSIVE` mode with a corrupt record column is another option.)

- `FAILFAST` fails the job.
- `DROPMALFORMED` throws the bad records away.
- `mergeSchema` is about schema evolution."""),

dict(d="Transformation, Cleansing & Quality", q="""A data engineer maintains an SCD Type 2 table with a single MERGE statement. The source is built like this:

```
SELECT u.customer_id AS merge_key, u.* FROM updates u
UNION ALL
SELECT NULL AS merge_key, u.* FROM updates u
JOIN dim_customer d ON u.customer_id = d.customer_id
WHERE d.is_current = true AND u.address <> d.address
```

Why are the rows with a NULL `merge_key` added?""",
a=["A NULL key never matches, so these rows always take the `WHEN NOT MATCHED` path and insert the new version, while the keyed rows match and close the current version.",
   "The NULL keys make MERGE skip the changed customers, so no history is created for them.",
   "NULL merge keys trigger `WHEN NOT MATCHED BY SOURCE`, which deletes the old version.",
   "The UNION ALL removes duplicate customers from the source before the MERGE."],
e="""For an SCD Type 2 change, MERGE has to do two things to the same key: update (close) the current row, and insert a new current row. A single source row can't do both, so the changed records are staged twice. The keyed copy matches and closes the old version (`WHEN MATCHED ... SET is_current = false, end_date = ...`). The NULL-keyed copy can't match, so it is inserted as the new version."""),

dict(d="Transformation, Cleansing & Quality", q="""The source data for `2025-03-14` was corrected, and that day's rows in the Delta table `daily_sales` must be replaced atomically without touching any other dates. The table is not partitioned.

Which statement does this?""",
a=["""INSERT INTO daily_sales REPLACE WHERE sale_date = '2025-03-14'
SELECT * FROM corrected_sales WHERE sale_date = '2025-03-14'""",
   """INSERT OVERWRITE daily_sales
SELECT * FROM corrected_sales WHERE sale_date = '2025-03-14'""",
   """DELETE FROM daily_sales WHERE sale_date = '2025-03-14';
VACUUM daily_sales;
INSERT INTO daily_sales SELECT * FROM corrected_sales""",
   """INSERT INTO daily_sales PARTITION (sale_date = '2025-03-14')
SELECT * FROM corrected_sales"""],
e="""`REPLACE WHERE` (or the `replaceWhere` DataFrame option) atomically replaces only the rows that match the predicate, in a single transaction, and works on any Delta table.

- `INSERT OVERWRITE` without a predicate replaces the whole table.
- The DELETE-then-INSERT version is not atomic and inserts every date again.
- A static `PARTITION` clause needs a partitioned table."""),

dict(d="Data Sharing & Federation", q="""A provider has shared `share_sales` with your Unity Catalog-enabled workspace through Databricks-to-Databricks sharing. The provider appears as `acme_corp`.

How do you make the shared tables available to query?""",
a=["`CREATE CATALOG acme_sales USING SHARE acme_corp.share_sales;`",
   "`CREATE FOREIGN CATALOG acme_sales USING CONNECTION acme_corp;`",
   "Download the credential file from the activation link, and register it as a storage credential.",
   "`CREATE SCHEMA acme_sales LOCATION 'delta-sharing://acme_corp/share_sales';`"],
e="""In Databricks-to-Databricks sharing, the recipient creates a catalog from the share, after which the shared objects can be queried and governed with Unity Catalog grants.

Foreign catalogs are for Lakehouse Federation. Credential files are only used in open sharing."""),

dict(d="Data Sharing & Federation", q="""A data provider wants to monitor which recipients access its shared tables and when. Where can this information be found?""",
a=["In the audit logs (`system.access.audit`), which record Delta Sharing events such as recipient data access requests",
   "In the shared table's `DESCRIBE HISTORY` output, which lists every recipient query",
   "In the recipient's `information_schema`, which the provider can query directly",
   "In the Spark UI of the provider's SQL warehouse"],
e="""Delta Sharing activity is recorded in the provider's audit logs, including the recipient, the shared table accessed, and the time.

`DESCRIBE HISTORY` only lists write operations on the table. The provider has no access to the recipient's metadata, and recipient queries don't run on the provider's compute."""),

dict(d="Data Sharing & Federation", q="""A company is moving from the legacy workspace Hive metastore to Unity Catalog. During the migration, which will take several months, they want the existing Hive metastore tables to be visible and governed in Unity Catalog without copying the data first.

Which feature should they use?""",
a=["Hive metastore federation, which exposes the Hive metastore as a foreign catalog in Unity Catalog",
   "Delta Sharing with open sharing from the Hive metastore",
   "A deep clone of every Hive metastore table into Unity Catalog",
   "Databricks Clean Rooms between the legacy and new environments"],
e="""Hive metastore federation (part of Lakehouse Federation) adds an internal or external Hive metastore to Unity Catalog as a foreign catalog. Its tables can then be governed, discovered, and queried through Unity Catalog while you migrate step by step.

Deep cloning copies the data, which they want to avoid during the migration."""),

dict(d="Data Sharing & Federation", q="""A retailer and a consumer-goods brand want to work out how many customers they share and analyze campaign results together. Neither company is willing to expose its raw customer records to the other.

Which Databricks capability fits this scenario?""",
a=["Databricks Clean Rooms",
   "Open Delta Sharing with a bearer token",
   "Lakehouse Federation between the two companies' databases",
   "Dynamic views shared through Databricks-to-Databricks sharing"],
e="""Clean Rooms give a secure environment where several parties run approved notebooks over their combined data without seeing each other's raw data. This is what privacy-safe joint analysis needs.

Delta Sharing and shared views give the other party direct read access to the data."""),

dict(d="Monitoring & Alerting", q="""An SDP pipeline update failed. The data engineer wants to query the pipeline's event log for the error messages from that update. Which filter returns them?""",
a=["`WHERE level = 'ERROR'` (optionally also filtering on `origin.update_id`)",
   "`WHERE event_type = 'flow_progress' AND details:flow_progress.data_quality IS NOT NULL`",
   "`WHERE event_type = 'cluster_resources'`",
   "`WHERE level = 'METRICS'`"],
e="""Every event-log record has a `level` (INFO, WARN, ERROR, METRICS), an `event_type`, `origin` details such as `update_id`, and a `message` or `error` payload. Filtering on `level = 'ERROR'` for the failed update shows what went wrong.

`flow_progress` with data quality details holds expectation metrics. `cluster_resources` describes autoscaling."""),

dict(d="Monitoring & Alerting", q="""A data engineer needs to find the 20 slowest queries run on the `bi_prod` SQL warehouse in the last week, along with the user who ran each one. Which system table should they query?""",
a=["`system.query.history`",
   "`system.billing.usage`",
   "`system.compute.warehouse_events`",
   "`system.access.column_lineage`"],
e="""`system.query.history` records queries run on SQL warehouses and serverless compute, including the statement text, the user, the warehouse, durations, and the amount of data read. Sort by `total_duration_ms` to find the slowest.

`warehouse_events` records warehouse start, stop, and scaling events, not individual queries."""),

dict(d="Monitoring & Alerting", q="""Which statement correctly describes notifications for Databricks jobs?""",
a=["Notifications can be sent to email addresses and to notification destinations set up by an admin (such as Slack, Microsoft Teams, PagerDuty, or webhooks) for events such as start, success, failure, and duration warnings.",
   "Notifications can only be sent by email, and only when a job fails.",
   "Notifications are set per workspace and apply to every job in that workspace.",
   "Notifications need a SQL alert to be created for each job."],
e="""Each job and each task can have notifications for start, success, failure, duration warning, and streaming backlog events. They can be sent to email or to system destinations that workspace admins configure. You can also choose to mute notifications for skipped or canceled runs, or for every failure except the last retry."""),
]
