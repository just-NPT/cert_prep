Q = [
dict(d="Developing Code (Python & SQL)", q="""Two DataFrames hold monthly extracts. The March extract has an extra column, `promo_code`, that the February extract doesn't have. The engineer needs to combine them by column name, with `promo_code` set to NULL for February rows.

Which code does this?""",
a=["""feb.unionByName(mar, allowMissingColumns=True)""",
   """feb.union(mar)""",
   """feb.unionByName(mar)""",
   """feb.join(mar, on="order_id", how="outer")"""],
e="""`unionByName` matches columns by name rather than position. With `allowMissingColumns=True`, columns missing from either side are filled with NULL.

- `union` matches by position and fails when the column counts differ.
- `unionByName` without the flag fails when columns are missing.
- A join combines columns, not rows."""),

dict(d="Developing Code (Python & SQL)", q="""For each customer, the engineer needs a `status_changed` flag that is true when a row's `status` differs from the customer's previous status, ordered by `updated_at`. Which expression produces it?""",
a=["""w = Window.partitionBy("customer_id").orderBy("updated_at")
df.withColumn("status_changed", F.col("status") != F.lag("status").over(w))""",
   """w = Window.partitionBy("customer_id").orderBy("updated_at")
df.withColumn("status_changed", F.col("status") != F.lead("status").over(w))""",
   """w = Window.partitionBy("status").orderBy("updated_at")
df.withColumn("status_changed", F.col("status") != F.lag("status").over(w))""",
   """df.withColumn("status_changed", F.col("status") != F.first("status"))"""],
e="""`lag` returns the value from the previous row within the window partition, here the customer's prior status in time order. `lead` looks at the next row instead. Partitioning by status compares rows that already share the same status.

The first row of each customer gets NULL, which you can handle with `coalesce` if needed."""),

dict(d="Developing Code (Python & SQL)", q="""The `orders` table has an `items` array of structs, each with a `qty` field. Which query returns only the orders that contain at least one item with `qty > 10`, without exploding the array?""",
a=["""SELECT * FROM orders WHERE exists(items, x -> x.qty > 10)""",
   """SELECT * FROM orders WHERE array_contains(items, qty > 10)""",
   """SELECT * FROM orders WHERE items.qty > 10""",
   """SELECT * FROM orders WHERE size(filter(items, x -> x.qty > 10)) < 0"""],
e="""`exists(array, predicate)` returns true if any element meets the lambda condition. Writing `size(filter(...)) > 0` would also work, but the version given compares with `< 0`, which is never true.

`array_contains` checks for a literal value, not a condition. `items.qty` is an array, so it can't be compared with a number."""),

dict(d="Developing Code (Python & SQL)", q="""A Python notebook needs to read a small JSON config file stored in the Unity Catalog volume `main.config.files`, using the standard Python `json` module. Which code works?""",
a=["""with open("/Volumes/main/config/files/settings.json") as f:
    cfg = json.load(f)""",
   """with open("dbfs:/Volumes/main/config/files/settings.json") as f:
    cfg = json.load(f)""",
   """with open("main.config.files/settings.json") as f:
    cfg = json.load(f)""",
   """cfg = json.load(spark.table("main.config.files"))"""],
e="""Unity Catalog volumes are available at POSIX-style paths, `/Volumes/<catalog>/<schema>/<volume>/...`, so standard Python file APIs, `dbutils.fs`, and Spark can all use them, subject to `READ VOLUME` permission.

Python's `open()` doesn't understand URI schemes like `dbfs:/`. A volume isn't a table, so `spark.table` can't read it."""),

dict(d="Developing Code (Python & SQL)", q="""A data scientist has a large pandas codebase that fails on a dataset that no longer fits in driver memory. They want to scale it on Spark with as few code changes as possible.

Which approach fits best?""",
a=["Use the pandas API on Spark (`import pyspark.pandas as ps`), which provides a pandas-compatible API that runs distributed",
   "Increase the driver memory until the full dataset fits",
   "Rewrite all the logic as RDD transformations",
   "Run the pandas code inside a single Python UDF"],
e="""The pandas API on Spark implements most of the pandas API on top of Spark DataFrames, so existing code can scale out with only small changes, such as swapping the import and adjusting unsupported calls.

Adding driver memory only postpones the problem, and an RDD rewrite is costly."""),

dict(d="Developing Code (Python & SQL)", q="""A data engineer needs the median `order_value` per region from a very large table, and a close approximation is acceptable. Which expression should be used?""",
a=["`percentile_approx(order_value, 0.5)`", "`avg(order_value)`", "`max(order_value) / 2`", "`approx_count_distinct(order_value) / 2`"],
e="""`percentile_approx` (also called `approx_percentile`) computes approximate percentiles, including the median at 0.5, using bounded memory. It scales well.

`avg` is the mean, not the median. The other expressions don't compute percentiles."""),

dict(d="Data Ingestion", q="""An upstream system sometimes overwrites a file in the landing directory with corrected content but keeps the same file name. Auto Loader is running with default options. What happens to the corrected file?""",
a=["It isn't processed again, because by default Auto Loader treats a file path it has already processed as done. Setting `cloudFiles.allowOverwrites` to `true` makes it pick up changed files.",
   "It is processed again automatically, and the old rows in the target are replaced.",
   "The stream fails with a FileAlreadyExists error.",
   "Auto Loader deletes the earlier rows from the target and inserts the new ones."],
e="""Auto Loader processes each file once by default. With `cloudFiles.allowOverwrites = true`, modified files can be reprocessed. Even then, the rows are appended, so the downstream logic must handle duplicates or corrections, for example with MERGE."""),

dict(d="Data Ingestion", q="""Two separate streaming queries read the same landing directory with Auto Loader, each with its own checkpoint location. One writes to `bronze_a`, the other to `bronze_b`.

How are the files processed?""",
a=["Each query tracks files on its own in its checkpoint, so every file is processed by both queries.",
   "The two queries share the files, so each file goes to only one of them.",
   "The second query fails, because a directory can only have one Auto Loader stream.",
   "Only the query that started first processes files. The other stays idle."],
e="""File discovery state is stored in each query's own checkpoint, and queries don't coordinate with each other. Independent consumers each see all the files. This is useful for fan-out, but if you meant to split the work, it causes double processing."""),

dict(d="Data Ingestion", q="""To save time, a data engineer copies an existing notebook and starts a second streaming query that writes to a different table, but with the same `checkpointLocation` as the first query. What is the most likely result?""",
a=["The queries clash over the same checkpoint state. This can cause failures, skipped data, or corrupted progress. Every streaming query needs its own checkpoint location.",
   "Spark automatically creates a subfolder for each query, so sharing the location is safe.",
   "The second query reuses the first one's progress and processes only new data, which is the recommended pattern.",
   "Both queries run normally, but the checkpoint takes up twice as much storage."],
e="""A checkpoint stores one query's offsets, commits, and state. Two queries writing to it overwrite each other's progress. Always use a unique checkpoint location for each streaming query, usually next to its target table."""),

dict(d="Data Ingestion", q="""A batch job reads a 500-million-row table from PostgreSQL over JDBC. The read runs as a single task. Which options make the read parallel?""",
a=["""`partitionColumn`, `lowerBound`, `upperBound`, and `numPartitions` (for example, partitioning on a numeric `id` column)""",
   """`fetchsize` only""",
   """`maxOffsetsPerTrigger` and `numPartitions`""",
   """`spark.sql.shuffle.partitions` set to 200"""],
e="""Spark's JDBC source reads with one connection unless you give it a partition column and bounds. With these, it splits the range into `numPartitions` parallel queries.

`fetchsize` only sets how many rows each round trip returns. Shuffle partitions apply after the read."""),

dict(d="Data Ingestion", q="""Some CSV fields contain line breaks inside quoted values, such as free-text comments. With the default reader options, these records are split across several malformed rows.

Which option fixes this?""",
a=["""`.option("multiLine", "true")`""",
   """`.option("header", "false")`""",
   """`.option("inferSchema", "true")`""",
   """`.option("mode", "DROPMALFORMED")`"""],
e="""By default, the CSV reader treats every line break as the end of a record. `multiLine` lets quoted fields span several lines, and `quote` and `escape` can be adjusted if the file uses non-standard characters.

`DROPMALFORMED` would throw these records away instead of parsing them."""),

dict(d="Data Ingestion", q="""New files land throughout the day, but the business only needs the bronze table refreshed four times a day. The team wants exactly-once file tracking at the lowest compute cost.

Which approach should they use?""",
a=["Run Auto Loader with `trigger(availableNow=True)` in a job scheduled four times a day",
   "Run Auto Loader continuously with a processing-time trigger of 6 hours",
   "Run a batch `spark.read` of the whole directory four times a day and overwrite the table",
   "Run `COPY INTO` with `force = true` four times a day"],
e="""An `availableNow` trigger turns the stream into an incremental batch. It processes all new files since the last run, keeps exactly-once tracking in the checkpoint, and stops, so compute only runs when scheduled.

A continuous query keeps the cluster running between triggers. Full re-reads and `force` reprocess old data."""),

dict(d="Transformation, Cleansing & Quality", q="""Each night, a source system delivers a complete snapshot of the active products. The target Delta table must match the snapshot exactly: new products inserted, changed products updated, and products missing from the snapshot removed.

Which MERGE does this?""",
a=["""MERGE INTO products t USING snapshot s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE""",
   """MERGE INTO products t USING snapshot s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO products t USING snapshot s ON t.id = s.id
WHEN MATCHED THEN DELETE
WHEN NOT MATCHED THEN INSERT *""",
   """MERGE INTO products t USING snapshot s ON t.id = s.id
WHEN NOT MATCHED BY TARGET THEN DELETE"""],
e="""`WHEN NOT MATCHED BY SOURCE` handles target rows that have no matching source row, here products missing from the snapshot, and can delete or update them. Together with the matched and not-matched clauses, one MERGE syncs the table with the snapshot.

`NOT MATCHED BY TARGET` is the same as `NOT MATCHED`, which covers source rows to insert, so it can't delete."""),

dict(d="Transformation, Cleansing & Quality", q="""A data engineer joins two DataFrames on `region_code`. Both sides have rows where `region_code` is NULL, and those rows should match each other. With `a.region_code == b.region_code`, they are dropped.

Which join condition fixes this?""",
a=["""`a.region_code.eqNullSafe(b.region_code)` (the `<=>` operator in SQL)""",
   """`a.region_code == b.region_code` with `how="outer"`""",
   """`F.coalesce(a.region_code, F.lit(0)) == b.region_code`""",
   """`a.region_code.isNull() & b.region_code.isNull()`"""],
e="""In SQL, `NULL = NULL` evaluates to NULL, not true, so NULL keys never match. The null-safe equality operator `<=>` (`eqNullSafe` in PySpark) treats two NULLs as equal.

An outer join keeps the rows, but they still won't match each other. Coalescing only one side doesn't help. The last condition matches only NULL rows."""),

dict(d="Transformation, Cleansing & Quality", q="""An SDP table is defined with the following expectation:

```
CONSTRAINT valid_amount EXPECT (amount >= 0) ON VIOLATION FAIL UPDATE
```

A micro-batch contains one record with `amount = -10`. What happens?""",
a=["The update fails, the write to this table is rolled back, and someone has to fix the data or the rule before the next update.",
   "The invalid record is dropped, and the rest of the batch is written.",
   "The record is written, and a warning is recorded in the event log.",
   "The record is written to an automatically created `valid_amount_errors` table."],
e="""`FAIL UPDATE` stops the update as soon as a violation is found. The transaction is rolled back atomically, so the table isn't partially updated. Use it for critical rules where bad data must never be written.

`DROP ROW` drops records. With no action, the expectation only warns."""),
]
