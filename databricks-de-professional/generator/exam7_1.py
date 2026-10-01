Q = [
dict(d="Developing Code (Python & SQL)", q="""The `orders` DataFrame has an `items` array column, which is empty or NULL for some orders. The output must have one row per item, and orders without items must still appear once with a NULL item.

Which function should be used?""",
a=["`explode_outer(\"items\")`", "`explode(\"items\")`", "`posexplode(\"items\")`", "`flatten(\"items\")`"],
e="""`explode_outer` returns a row with NULL when the array is NULL or empty. `explode` and `posexplode` drop those rows.

`flatten` merges an array of arrays into a single array and doesn't create rows."""),

dict(d="Developing Code (Python & SQL)", q="""A report needs one row per `store_id` and one column per month (`Jan` to `Dec`) holding the total `amount`. The month values are known in advance.

Which code produces this most efficiently?""",
a=["""df.groupBy("store_id").pivot("month", ["Jan","Feb","Mar","Apr","May","Jun",
                                       "Jul","Aug","Sep","Oct","Nov","Dec"]).sum("amount")""",
   """df.groupBy("store_id").pivot("month").sum("amount")""",
   """df.groupBy("month").pivot("store_id").sum("amount")""",
   """df.pivot("month").groupBy("store_id").sum("amount")"""],
e="""`pivot` turns the distinct values of a column into columns. If you don't pass the values, Spark first runs an extra job to compute them. Passing a known list skips that job and also fixes the column order.

Swapping the roles of the two columns gives the wrong shape, and `pivot` must come after `groupBy`."""),

dict(d="Developing Code (Python & SQL)", q="""A data engineer needs a reusable Python function that takes one text value and returns a variable number of rows, one per token, with columns `token` and `position`. It should be callable in the `FROM` clause of SQL queries.

Which construct fits?""",
a=["A Python user-defined table function (UDTF), defined with `@udtf(returnType=\"token: string, position: int\")` on a class whose `eval` method yields rows",
   "A scalar pandas UDF that returns a pandas Series",
   "A SQL scalar UDF created with `CREATE FUNCTION ... RETURNS STRING`",
   "A Python UDF that returns an array, used with `@udf(\"array<string>\")`"],
e="""A UDTF returns a table: zero or more rows, with several columns, for each input. Once registered, you call it in the `FROM` clause.

Scalar UDFs (Python, pandas, or SQL) return exactly one value per input row. An array UDF would still need an extra explode step."""),

dict(d="Developing Code (Python & SQL)", q="""The finance team wants one governed definition of the "net price" calculation. It must be usable from SQL warehouses and notebooks, and calling it should require an explicit permission.

Which approach fits best?""",
a=["""CREATE FUNCTION main.finance.net_price(price DOUBLE, discount DOUBLE)
RETURNS DOUBLE RETURN price * (1 - discount);

GRANT EXECUTE ON FUNCTION main.finance.net_price TO `analysts`;""",
   """CREATE TEMPORARY FUNCTION net_price(price DOUBLE, discount DOUBLE)
RETURNS DOUBLE RETURN price * (1 - discount);""",
   """# shared_utils notebook, included everywhere with %run
def net_price(price, discount):
    return price * (1 - discount)""",
   """spark.udf.register("net_price", lambda p, d: p * (1 - d))
-- run at the start of every session"""],
e="""A Unity Catalog function is stored in a schema, can be found by other users, works across compute types, and is controlled with `EXECUTE` grants.

Temporary functions and session-registered UDFs only exist for one session. A `%run` helper is limited to Python notebooks and isn't governed."""),

dict(d="Developing Code (Python & SQL)", q="""A dashboard shows the number of distinct users per day from a clickstream table with 30 billion rows. `count(DISTINCT user_id)` is slow, and an error of about 1–2% is acceptable.

Which change gives the biggest improvement?""",
a=["Use `approx_count_distinct(user_id)` instead of `count(DISTINCT user_id)`.",
   "Use `count(user_id)` instead of `count(DISTINCT user_id)`.",
   "Call `collect()` on the user IDs and count unique values in Python.",
   "Run `SELECT DISTINCT user_id` first, then count the result in a second query."],
e="""`approx_count_distinct` uses HyperLogLog++ to estimate the number of distinct values with bounded error, using little memory and no full shuffle of distinct values.

`count()` counts every row, including duplicates. Collecting to the driver doesn't scale. A two-step distinct does the same expensive work."""),

dict(d="Developing Code (Python & SQL)", q="""A notebook task ends with this code:

```
try:
    run_pipeline()
except Exception as e:
    log_error(e)
    dbutils.notebook.exit(f"FAILED: {e}")
```

When `run_pipeline()` throws an error, the job run still shows as **Succeeded**. How should this be fixed?""",
a=["After logging, raise the exception again (for example with `raise`) instead of calling `dbutils.notebook.exit`, so the task is marked as failed.",
   "Replace `dbutils.notebook.exit` with `print`, so the message shows up in the task output.",
   "Set the task's retry count to 3 so that the failure is detected.",
   "Pass `status=\"FAILED\"` to `dbutils.notebook.exit`."],
e="""`dbutils.notebook.exit()` ends the notebook successfully and returns a value. A task is only marked failed when an exception goes uncaught. Catch it to log, then raise it again. Retries and notifications also depend on the task being marked as failed.

`exit` has no status argument."""),

dict(d="Data Ingestion", q="""An Auto Loader stream reads CSV files with schema inference, using `cloudFiles.schemaLocation`. Every column in the resulting table is STRING, including numeric and date fields.

How can the engineer get proper column types inferred?""",
a=["""Set `.option("cloudFiles.inferColumnTypes", "true")`.""",
   """Set `.option("cloudFiles.schemaEvolutionMode", "addNewColumns")`.""",
   """Set `.option("mergeSchema", "true")` on the write.""",
   """Delete the schema location before every run."""],
e="""For formats that don't encode types, such as JSON and CSV, Auto Loader infers every column as STRING by default to avoid type mismatches as files evolve. Setting `cloudFiles.inferColumnTypes` to `true` makes it infer the real types. You can also use schema hints for specific columns.

The evolution mode and `mergeSchema` control new columns, not types."""),

dict(d="Data Ingestion", q="""What does Auto Loader store in the directory given by `cloudFiles.schemaLocation`?""",
a=["The inferred schema and its later versions, so restarts use a consistent schema without inferring it again",
   "The offsets of files that have already been processed, which replaces the streaming checkpoint",
   "Copies of the records that went to the `_rescued_data` column",
   "Records that couldn't be parsed, along with their exception details"],
e="""The schema location keeps the schema Auto Loader has inferred and each version as it evolves. Restarts and later runs then use the same schema, and the source doesn't have to be sampled again.

The checkpoint location tracks which files have been processed. Rescued data stays in the target table. Bad records go to `badRecordsPath` when it is configured."""),

dict(d="Data Ingestion", q="""An Auto Loader stream uses file notification mode. Cloud storage notifications aren't guaranteed to be delivered, and the team wants to be sure that every file is eventually processed even if a notification is lost.

Which option should they set?""",
a=["""`cloudFiles.backfillInterval`, for example `"1 day"`""",
   """`cloudFiles.includeExistingFiles = "true"`""",
   """`cloudFiles.maxFilesPerTrigger = "1"`""",
   """`cloudFiles.allowOverwrites = "true"`"""],
e="""`cloudFiles.backfillInterval` makes Auto Loader run an asynchronous directory listing on a schedule. It finds and processes files whose notification was missed, so every file is processed eventually, without the cost of listing on every micro-batch.

`includeExistingFiles` only affects the first run."""),

dict(d="Data Ingestion", q="""A data engineer needs to stream events from Azure Event Hubs into a Delta table, using only the connectors built into Databricks Runtime. Which approach works?""",
a=["Use the Spark Kafka source pointed at the Event Hubs namespace's Kafka-compatible endpoint (port 9093), with SASL_SSL authentication options.",
   "Use Auto Loader with `cloudFiles.format` set to `eventhubs`.",
   "Create a Lakehouse Federation connection to the Event Hubs namespace.",
   "Set up a Delta Sharing recipient for the Event Hubs namespace."],
e="""Event Hubs exposes an endpoint that speaks the Kafka protocol. The built-in Structured Streaming Kafka connector can read from it once `kafka.bootstrap.servers`, `kafka.security.protocol`, and the SASL settings are configured.

Auto Loader reads files. Federation and Delta Sharing don't read message streams."""),

dict(d="Data Ingestion", q="""Which statement correctly compares Auto Loader and `COPY INTO` for loading files from cloud storage?""",
a=["Auto Loader scales to millions of files, supports file notification mode, and can infer and evolve schemas. `COPY INTO` is a simple, idempotent SQL command suited to directories with thousands of files.",
   "`COPY INTO` scales better than Auto Loader for directories that hold billions of files.",
   "Auto Loader can only run in continuous mode, while `COPY INTO` can be scheduled.",
   "Only `COPY INTO` keeps track of which files were already loaded. Auto Loader reprocesses all files on every run."],
e="""Both tools load each file exactly once. Auto Loader records processed files in its checkpoint (RocksDB), supports directory listing and file notifications, handles schema evolution, and runs with `availableNow` or continuously. `COPY INTO` tracks loaded files in the target table's metadata and is a good fit for smaller or ad-hoc SQL loads."""),

dict(d="Data Ingestion", q="""A SQL-only team wants a streaming table that continuously ingests the Kafka topic `events`. Which statement should they use?""",
a=["""CREATE OR REFRESH STREAMING TABLE kafka_events AS
SELECT * FROM STREAM read_kafka(
  bootstrapServers => 'broker1:9092',
  subscribe => 'events');""",
   """CREATE OR REFRESH STREAMING TABLE kafka_events AS
SELECT * FROM STREAM read_files('kafka://broker1:9092/events');""",
   """CREATE FOREIGN CATALOG kafka USING CONNECTION kafka_conn;
CREATE TABLE kafka_events AS SELECT * FROM kafka.default.events;""",
   """CREATE MATERIALIZED VIEW kafka_events AS
SELECT * FROM kafka.`broker1:9092/events`;"""],
e="""The `read_kafka` table-valued function reads Kafka from SQL. When it's wrapped in `STREAM` inside a streaming table, each refresh reads only new offsets.

`read_files` reads files from storage, and Kafka isn't a Lakehouse Federation source."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming query unions two streams before an aggregation:

```
a = stream_a.withWatermark("ts", "10 minutes")
b = stream_b.withWatermark("ts", "1 hour")
a.unionByName(b).groupBy(F.window("ts", "5 minutes")).count()
```

With default settings, which watermark decides when windows are finalized?""",
a=["The minimum of the two watermarks, so the slower stream (the one with the 1-hour delay) determines progress.",
   "The maximum of the two watermarks, so the faster stream (the one with the 10-minute delay) determines progress.",
   "The watermark of whichever stream appears first in the union.",
   "Neither. Streams with different watermarks can't be unioned."],
e="""When several inputs have watermarks, Spark tracks each one and by default uses the minimum as the global watermark (`spark.sql.streaming.multipleWatermarkPolicy = min`). This is safe because no data is dropped too early, at the cost of more latency.

Setting the policy to `max` advances faster but may drop data from the slower stream."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming aggregation uses the following window:

```
.groupBy(F.window("event_ts", "10 minutes", "5 minutes"))
```

Which windows does an event with `event_ts = 12:07` count toward?""",
a=["12:00–12:10 and 12:05–12:15",
   "Only 12:00–12:10",
   "Only 12:05–12:15",
   "12:00–12:05, 12:05–12:10, and 12:10–12:15"],
e="""A window with a slide shorter than its duration is a sliding window. Windows are 10 minutes long and start every 5 minutes, so each event falls into duration/slide = 2 overlapping windows. The two windows that contain 12:07 are [12:00, 12:10) and [12:05, 12:15)."""),

dict(d="Transformation, Cleansing & Quality", q="""Product analytics wants to group each user's clickstream events into sessions. A session ends after 30 minutes without activity, so sessions vary in length.

Which grouping expression should be used in the streaming aggregation?""",
a=["""`F.session_window("event_ts", "30 minutes")`""",
   """`F.window("event_ts", "30 minutes")`""",
   """`F.window("event_ts", "30 minutes", "5 minutes")`""",
   """`F.date_trunc("hour", "event_ts")`"""],
e="""Session windows have a dynamic length. A window starts with an event and is extended by each event that arrives within the gap, and it closes after the gap passes with no new events. Group by user and `session_window`.

Tumbling and sliding windows have fixed boundaries that don't follow user activity."""),
]
