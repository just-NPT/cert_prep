Q = [
dict(d="Data Sharing & Federation", q="""A data provider uses Unity Catalog and needs to share a curated table with an external vendor. The vendor has no Databricks account and reads data with pandas and Apache Spark running on their own infrastructure.

How should the provider share the data?""",
a=["Create a recipient that uses open sharing (token-based or OIDC federation), add the share to it, and send the vendor the activation link so they can get their credentials and read the data with a Delta Sharing connector.",
   "Ask the vendor for their sharing identifier, then create a Databricks-to-Databricks recipient using that identifier.",
   "Create a Lakehouse Federation connection to the vendor's environment and grant it `SELECT` on the table.",
   "Grant `SELECT` on the table directly to the vendor's email address in Unity Catalog."],
e="""Open sharing is for recipients who are not on Databricks with Unity Catalog. The provider creates the recipient, and the recipient gets credentials through an activation link (a bearer-token credential file) or through OIDC federation. They can then read the data with open Delta Sharing clients such as pandas, Spark, or Power BI.

A sharing identifier only exists for Databricks-to-Databricks sharing. Lakehouse Federation is for querying external databases, not for sharing data out."""),

dict(d="Data Sharing & Federation", q="""The table `sales.core.orders` is partitioned by `region`. A data engineer needs to share only the rows where `region = 'EU'` through the existing share `eu_partner_share`.

Which command does this?""",
a=["""ALTER SHARE eu_partner_share ADD TABLE sales.core.orders PARTITION (region = "EU");""",
   """GRANT SELECT ON TABLE sales.core.orders WHERE region = 'EU' TO RECIPIENT eu_partner;""",
   """ALTER SHARE eu_partner_share ADD TABLE sales.core.orders WITH ROW FILTER (region = 'EU');""",
   """CREATE RECIPIENT eu_partner OPTIONS (region = 'EU');"""],
e="""When you add a table to a share, you can include a partition specification. Only the matching partitions are shared, so the recipient never sees the other regions.

Another option is to share a view that filters the rows. A `GRANT ... WHERE` clause does not exist, and recipient options do not filter data."""),

dict(d="Data Sharing & Federation", q="""A team created a foreign catalog with Lakehouse Federation to query an operational SQL Server database from Databricks.

Which statement about the foreign catalog is correct?""",
a=["Queries run against the source database at query time, some operations such as filters can be pushed down, and the foreign tables are read-only.",
   "Creating the foreign catalog copies all source tables into managed Delta tables, which are then refreshed every night.",
   "Foreign tables support `INSERT`, `UPDATE`, and `MERGE`, which write the changes back to SQL Server.",
   "Unity Catalog permissions are bypassed, so access is controlled only by the SQL Server login."],
e="""Lakehouse Federation lets you query external databases without copying the data. Unity Catalog governs access to the foreign catalog: you can grant privileges, tables are discoverable, and lineage and auditing are recorded. Supported operations such as filters and projections are pushed down to the source, and access is read-only.

For a regular, governed copy of the data in the lakehouse, use an ingestion tool instead."""),

dict(d="Data Sharing & Federation", q="""A company needs to incrementally ingest about 40 tables from an on-premises SQL Server database into Unity Catalog Delta tables every hour. They want change tracking handled for them and as little custom code as possible.

Which solution fits best?""",
a=["A Lakeflow Connect managed SQL Server connector (ingestion pipeline)",
   "A Lakehouse Federation foreign catalog over the SQL Server database",
   "A Delta Sharing recipient created for the SQL Server database",
   "An Auto Loader stream reading directly from the SQL Server JDBC endpoint"],
e="""Lakeflow Connect has managed connectors for databases such as SQL Server. The connector incrementally ingests data into streaming tables, using change tracking or CDC, and needs very little code.

Lakehouse Federation queries the source live and doesn't ingest data. Delta Sharing shares Delta data out. Auto Loader reads files from cloud storage, not JDBC endpoints."""),

dict(d="Developing Code (Python & SQL)", q="""A DataFrame `orders` has the columns `customer_id`, `order_date`, and `amount`. A data engineer needs a `running_total` column with the cumulative amount for each customer in date order.

Which expression produces it?""",
a=["""w = Window.partitionBy("customer_id").orderBy("order_date") \\
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
orders.withColumn("running_total", F.sum("amount").over(w))""",
   """w = Window.partitionBy("customer_id")
orders.withColumn("running_total", F.sum("amount").over(w))""",
   """w = Window.partitionBy("customer_id").orderBy("order_date").rowsBetween(-1, 1)
orders.withColumn("running_total", F.sum("amount").over(w))""",
   """w = Window.partitionBy("order_date").orderBy("customer_id")
orders.withColumn("running_total", F.sum("amount").over(w))"""],
e="""A running total partitions by customer, orders by date, and uses a frame from the first row up to the current row.

- Without `orderBy`, the frame covers the whole partition, so every row gets the customer's grand total.
- `rowsBetween(-1, 1)` gives a three-row moving sum.
- Partitioning by date computes totals across customers."""),

dict(d="Developing Code (Python & SQL)", q="""A data scientist has a function `forecast(pdf: pd.DataFrame) -> pd.DataFrame` that fits a small model on one store's history and returns that store's forecasts. The function must run independently for each of 5,000 stores in a Spark DataFrame `sales`, and the work must be distributed across the cluster.

Which approach should the data engineer use?""",
a=["""sales.groupBy("store_id").applyInPandas(forecast, schema=result_schema)""",
   """sales.mapInPandas(forecast, schema=result_schema)""",
   """pdf = sales.toPandas()
results = [forecast(g) for _, g in pdf.groupby("store_id")]""",
   """forecast_udf = F.udf(forecast)
sales.withColumn("forecast", forecast_udf(F.struct("*")))"""],
e="""`groupBy().applyInPandas()` sends all rows for each group to a single Python worker as one pandas DataFrame, and the groups run in parallel across executors. This is the standard pattern for per-group model training.

- `mapInPandas` works on arbitrary batches with no guarantee that a store's rows are together.
- `toPandas()` pulls everything onto the driver.
- A row-at-a-time UDF never sees the whole group."""),

dict(d="Developing Code (Python & SQL)", q="""A team's transformation logic lives in a long notebook that can only be checked by running it on production tables. They want to add fast, automated unit tests.

Which change best supports this goal?""",
a=["Move the transformation logic into functions in Python files (modules) that take and return DataFrames, then call them from pytest tests with small DataFrames built in memory.",
   "Split the notebook into several smaller notebooks and chain them together with `%run`.",
   "Add `display()` calls after each transformation so the outputs can be checked by eye during each scheduled run.",
   "Schedule the notebook as a job on a smaller cluster that points to a copy of the production tables."],
e="""Unit tests check small pieces of logic in isolation, using controlled inputs and expected outputs. Pure functions that transform DataFrames, stored in importable Python modules (for example, workspace files in a Git folder), are easy to test with pytest and `pyspark.testing.assertDataFrameEqual`.

The other options are manual checks or integration and end-to-end testing, not unit testing."""),

dict(d="Developing Code (Python & SQL)", q="""A pipeline uses this Python UDF on a 2-billion-row table:

```
@udf("string")
def fmt_phone(p):
    return None if p is None else p.replace("-", "").replace(" ", "")
```

The stage that runs it is slow. Which change will most likely improve performance?""",
a=["""Replace the UDF with a built-in expression such as `F.regexp_replace("phone", "[- ]", "")`.""",
   "Increase the driver memory so the UDF can cache more results.",
   "Convert the DataFrame to an RDD and apply the function with `map`.",
   "Register the same Python function as a SQL function with `spark.udf.register`."],
e="""Python UDFs serialize every row between the JVM (or Photon) and Python worker processes, and the optimizer can't see inside them. Built-in functions run natively, can use Photon, and avoid that serialization.

Registering the same Python function for SQL doesn't remove the overhead. RDD operations lose Catalyst optimizations."""),

dict(d="Data Ingestion", q="""An Auto Loader stream ingests from a bucket that already holds millions of files across a deep directory tree, and thousands of new files arrive every hour. Most of the time in each micro-batch is now spent listing the directory.

Which change will reduce this overhead the most?""",
a=["Switch Auto Loader from directory listing mode to file notification mode (file events), so new files are discovered from storage event notifications.",
   "Increase `cloudFiles.maxFilesPerTrigger` so that each micro-batch processes more files.",
   "Set `cloudFiles.includeExistingFiles` to `false`.",
   "Change the trigger from `processingTime` to `availableNow=True`."],
e="""In directory listing mode, Auto Loader lists the input path to find new files, which gets expensive with very large directories. File notification mode (or managed file events on Unity Catalog external locations) uses cloud storage events and queues instead, so discovery scales with the number of new files rather than all files.

`includeExistingFiles` only affects the first run. Trigger and batch-size settings don't change how files are discovered."""),

dict(d="Data Ingestion", q="""A data engineer loads CSV files into a Delta table with `COPY INTO`. A bug in the parsing options was fixed, and every file in the source directory must now be loaded again, including files that were already loaded.

Which option should be added to the COPY INTO command?""",
a=["`COPY_OPTIONS ('force' = 'true')`",
   "`COPY_OPTIONS ('mergeSchema' = 'true')`",
   "`FORMAT_OPTIONS ('ignoreLoaded' = 'false')`",
   "No option is needed. `COPY INTO` reprocesses all files on every run."],
e="""`COPY INTO` is idempotent: it tracks which files it has loaded and skips them on later runs. Setting `force` to `true` turns this off and loads every file again. Usually you would truncate the target table or deduplicate first.

`mergeSchema` controls schema evolution, and `ignoreLoaded` is not a real option."""),

dict(d="Transformation, Cleansing & Quality", q="""Two streams are joined with a left outer join. Both have watermarks, and the join condition includes an event-time range:

```
impressions.withWatermark("imp_ts", "1 hour") \\
  .join(clicks.withWatermark("click_ts", "2 hours"),
        expr("click_ad_id = imp_ad_id AND click_ts BETWEEN imp_ts AND imp_ts + interval 1 hour"),
        "leftOuter")
```

The engineer notices that impressions without a matching click are only written after a delay. Which statement explains this?""",
a=["NULL-padded rows for unmatched impressions are only emitted after the watermark passes the join's time bound, because a matching click could still arrive until then.",
   "Outer joins between two streams are not supported, so unmatched rows are written only when the query restarts.",
   "Unmatched rows are emitted right away, but the Delta sink buffers them until the next `OPTIMIZE`.",
   "The delay happens because the `clicks` watermark is longer than the `impressions` watermark. With equal watermarks, unmatched rows would be emitted immediately."],
e="""In a stream-stream outer join, Spark can only be sure that a row has no match once the watermark has advanced past the time constraint. Until then, a matching row could still arrive. The NULL-padded results are therefore delayed by the watermark plus the time bound.

If no new data arrives, the watermark doesn't advance and these rows can be delayed further."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming query computes 10-minute tumbling-window counts with a 15-minute watermark and writes them to a Delta table in append output mode:

```
(events.withWatermark("event_ts", "15 minutes")
   .groupBy(F.window("event_ts", "10 minutes"), "page")
   .count()
   .writeStream.outputMode("append")
   .option("checkpointLocation", cp)
   .toTable("page_counts"))
```

When is a given window's row written to `page_counts`?""",
a=["Once, after the watermark passes the end of the window, with the window's final count.",
   "In every micro-batch, with an updated count that replaces the previous row in the table.",
   "Never, because aggregations can't use append mode.",
   "Immediately when the first event of the window arrives, with later events added through MERGE."],
e="""In append mode, a windowed aggregation emits each window's result only once it is final, which is when the watermark passes the window's end. Late data can't change it after that, so every row is written exactly once.

Update mode would emit changed counts in every micro-batch. Append mode is allowed for aggregations only when a watermark is defined."""),

dict(d="Monitoring & Alerting", q="""A nightly job normally finishes in about 40 minutes. The team wants to be notified if a run takes longer than 90 minutes, but the run must keep going.

How should they configure the job?""",
a=["Set a duration warning threshold (a run-duration health rule) of 90 minutes and add a notification for duration warnings.",
   "Set the job timeout to 90 minutes and add a notification for failures.",
   "Set the maximum number of retries to 1 with a 90-minute delay between retries.",
   "Create a SQL alert on `system.billing.usage` that triggers when the job's DBUs exceed a threshold."],
e="""Jobs support health rules such as a run-duration threshold. When a run passes the threshold, a duration warning is sent to the configured destinations and the run continues.

A timeout cancels the run. Retries and billing alerts don't detect long runs while they are happening."""),

dict(d="Monitoring & Alerting", q="""A data engineer wants to push metrics from each micro-batch of a Structured Streaming query, such as input rows per second and batch duration, to an external monitoring system as soon as each batch completes.

Which approach should they use?""",
a=["Implement a `StreamingQueryListener` that handles `onQueryProgress`, and register it with `spark.streams.addListener()`.",
   "Call `query.awaitTermination()` and read the returned metrics after each batch.",
   "Run `DESCRIBE HISTORY` on the checkpoint directory after every micro-batch.",
   "Set `spark.sparkContext.setLogLevel(\"DEBUG\")` and have the monitoring tool scrape the driver logs."],
e="""A `StreamingQueryListener` gets a callback when a query starts, makes progress (once per micro-batch, with a `StreamingQueryProgress` object), goes idle, or terminates. You can forward those metrics to external systems such as Datadog or Prometheus. Since Spark 3.4, PySpark supports this listener.

`awaitTermination()` blocks and returns no metrics, and a checkpoint is not a Delta table."""),

dict(d="Cost & Performance Optimization", q="""A Delta table has 60 columns. Queries often filter on `region_code`, which is the 45th column in the schema, yet the query profile shows almost no files are skipped.

What is the most likely cause, and how should it be fixed?""",
a=["By default, file statistics are only collected for the first 32 columns. Add `region_code` to `delta.dataSkippingStatsColumns` (or move it into the first 32 columns) and recompute the statistics.",
   "Data skipping only works on partition columns, so the table must be partitioned by `region_code`.",
   "File statistics are not kept for STRING columns. Cast `region_code` to an integer.",
   "Data skipping is turned off until Change Data Feed is enabled on the table."],
e="""Delta Lake records per-file statistics (min, max, null count) that let queries skip files. These are collected only for the first 32 columns by default, a limit set by `delta.dataSkippingNumIndexedCols`. You can choose which columns get statistics with `delta.dataSkippingStatsColumns` and then recompute statistics for existing files.

Data skipping also works on non-partition and STRING columns."""),
]
