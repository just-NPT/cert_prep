Q = [
dict(d="Data Ingestion", q="""A data engineer configures an Auto Loader stream with the following option:

```
.option("cloudFiles.schemaEvolutionMode", "rescue")
```

A few days later, the incoming JSON files start containing a new field named `coupon_code`.

How does the stream behave?""",
a=["The stream keeps running without failing. The schema is not evolved, and the values of `coupon_code` are captured in the `_rescued_data` column.",
   "The stream fails, adds `coupon_code` to the schema stored in the schema location, and processes the new column after it is restarted.",
   "The stream fails and stays failed until the schema location is manually updated or the files are removed.",
   "The stream keeps running, and `coupon_code` is silently ignored without being stored anywhere."],
e="""Auto Loader supports several schema evolution modes:

- `addNewColumns` (default): the stream fails, adds the new columns to the schema, and picks them up after a restart.
- `rescue`: the schema never evolves and the stream does not fail. Unexpected fields go to the `_rescued_data` column.
- `failOnNewColumns`: the stream fails and does not restart until the schema is updated or the offending files are removed.
- `none`: the schema does not evolve, new columns are ignored, and no data is rescued unless the `rescuedDataColumn` option is set."""),

dict(d="Data Ingestion", q="""A data engineer reads a Kafka topic with Structured Streaming:

```
df = (spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", brokers)
        .option("subscribe", "orders")
        .load())
```

Each message value is a JSON document matching a StructType named `schema`. Which transformation correctly turns the payload into top-level columns?""",
a=["""df.select(from_json(col("value").cast("string"), schema).alias("v")).select("v.*")""",
   """df.select(from_json(col("value"), schema).alias("v")).select("v.*")""",
   """df.select(col("value").cast(schema).alias("v")).select("v.*")""",
   """df.select(schema_of_json(col("value")).alias("v")).select("v.*")"""],
e="""The Kafka source exposes `key` and `value` as BINARY columns. Cast `value` to STRING before `from_json` can parse it with the schema you provide. Then expand the resulting struct with `v.*`.

`schema_of_json` only infers a DDL schema string from a sample JSON literal. It does not parse data."""),

dict(d="Transformation, Cleansing & Quality", q="""Producers of an `events` stream sometimes re-send the same event, up to 30 minutes after the original. A re-sent event has the same `event_id`, but its `event_ts` can differ by a few seconds because the producer stamps it again.

The data engineer needs to remove these duplicates while keeping the streaming state bounded. Which approach should they use?""",
a=["""events.withWatermark("event_ts", "30 minutes").dropDuplicatesWithinWatermark(["event_id"])""",
   """events.dropDuplicates(["event_id"])""",
   """events.withWatermark("event_ts", "30 minutes").dropDuplicates(["event_id", "event_ts"])""",
   """events.withWatermark("event_ts", "30 minutes").distinct()"""],
e="""`dropDuplicatesWithinWatermark` (Spark 3.5+ / DBR 13.3+) removes records with the same key if they arrive within the watermark delay, even when their event-time values differ. The state is dropped once the watermark passes, so it stays bounded.

- `dropDuplicates(["event_id"])` without a watermark keeps state forever.
- Adding `event_ts` to the key misses duplicates whose timestamps differ.
- `distinct()` compares every column, so re-sent events with a new timestamp are not removed."""),

dict(d="Transformation, Cleansing & Quality", q="""A streaming query uses `foreachBatch` to write each micro-batch to two Delta tables, `silver_orders` and `audit_orders`. If the query fails after writing to `silver_orders` but before writing to `audit_orders`, the micro-batch is reprocessed on restart and `silver_orders` gets duplicate rows.

Which change makes both writes idempotent?""",
a=["Set the `txnAppId` and `txnVersion` (the micro-batch `batchId`) options on each Delta write inside the function.",
   "Give each write inside the function its own `checkpointLocation` option.",
   "Change the query's output mode from append to complete.",
   "Set the `delta.appendOnly` table property on both target tables."],
e="""Inside `foreachBatch`, Delta can't tell on its own that a write is a replay. When you pass a stable application ID (`txnAppId`) and a monotonically increasing version (`txnVersion`, usually the `batchId`), Delta skips a write it has already committed for that pair. That makes the reprocessed batch idempotent.

A checkpoint only applies to the outer streaming query. Output modes and `appendOnly` don't prevent duplicates."""),

dict(d="Transformation, Cleansing & Quality", q="""A nightly job upserts a staging table into `dim_customers`:

```
MERGE INTO dim_customers t
USING staging_customers s
ON t.customer_id = s.customer_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

The job fails with an error saying that multiple source rows matched and tried to modify the same target row. What is the right fix?""",
a=["Deduplicate the source so it contains one row per `customer_id` (for example, keep the latest record using `row_number()` over a window) before the MERGE.",
   "Add a `WHEN NOT MATCHED BY SOURCE THEN DELETE` clause to the MERGE statement.",
   "Enable deletion vectors on `dim_customers` so concurrent row modifications are allowed.",
   "Run `OPTIMIZE dim_customers` before the MERGE so each customer lives in a single file."],
e="""MERGE requires that each target row is matched by at most one source row. Otherwise the update is ambiguous. Reduce the source to one row per merge key first, usually by keeping the most recent change with a window function such as `row_number()` ordered by a timestamp.

The other options don't change how many source rows match a target row."""),

dict(d="Transformation, Cleansing & Quality", q="""A Lakeflow Spark Declarative Pipelines (SDP) pipeline defines this table:

```
CREATE OR REFRESH STREAMING TABLE silver_payments (
  CONSTRAINT positive_amount EXPECT (amount > 0),
  CONSTRAINT has_currency EXPECT (currency IS NOT NULL) ON VIOLATION DROP ROW
)
AS SELECT * FROM STREAM(bronze_payments)
```

A record arrives with `amount = -5` and `currency = 'USD'`. What happens to it?""",
a=["It is written to `silver_payments`, and the `positive_amount` violation is recorded in the pipeline's data quality metrics.",
   "It is dropped from `silver_payments`, because any failed expectation drops the row.",
   "The pipeline update fails, and the transaction for `silver_payments` is rolled back.",
   "It is automatically redirected to a quarantine table created by the pipeline."],
e="""An expectation with no `ON VIOLATION` clause is a warn expectation. The invalid record is kept, and the violation count is reported in the event log. Only `positive_amount` fails here, and it has no action, so the row is written.

`ON VIOLATION DROP ROW` drops invalid rows, and `ON VIOLATION FAIL UPDATE` stops the update. SDP never creates a quarantine table automatically; you have to build one yourself."""),

dict(d="Monitoring & Alerting", q="""A platform team wants a dashboard of the estimated list-price cost of each Databricks job over the last 30 days. Which approach gives this information?""",
a=["Join `system.billing.usage` with `system.billing.list_prices` on the SKU and the price's effective time window, then aggregate `usage_quantity × price` by `usage_metadata.job_id`.",
   "Count the events in `system.access.audit` for each job ID and multiply by the DBU rate of the workspace.",
   "Sum the run durations from `system.lakeflow.job_run_timeline` and treat each hour as one DBU.",
   "Query `system.compute.clusters` and sum the `num_workers` column for each job cluster."],
e="""`system.billing.usage` records DBU consumption with attribution metadata such as `usage_metadata.job_id`. `system.billing.list_prices` holds the list price of each SKU over time. Joining the two on SKU and validity period gives the estimated cost, which you can then group by job.

The other tables describe activity or configuration, not billed usage."""),

dict(d="Cost & Performance Optimization", q="""A Unity Catalog managed table `events` uses liquid clustering on `event_date`. Query patterns changed, so the team ran:

```
ALTER TABLE events CLUSTER BY (customer_id, event_date);
```

They now want every existing record, not just newly written data, reorganized by the new clustering keys. Which command should they run?""",
a=["`OPTIMIZE events FULL`",
   "`OPTIMIZE events ZORDER BY (customer_id, event_date)`",
   "`REORG TABLE events APPLY (PURGE)`",
   "`VACUUM events RETAIN 0 HOURS`"],
e="""Changing the clustering keys doesn't rewrite existing data. A normal `OPTIMIZE` only clusters data incrementally. `OPTIMIZE ... FULL` reclusters every record in the table using the current keys, which is the usual step right after changing them.

You can't combine Z-ordering with liquid clustering. `REORG ... APPLY (PURGE)` rewrites files to remove soft-deleted data. VACUUM removes unreferenced files."""),

dict(d="Cost & Performance Optimization", q="""In the Spark UI, a stage that runs a join has these summary metrics across its 200 tasks:

- Duration: median 18 s, max 26 min
- Shuffle Read Size: median 140 MB, max 13 GB

Which action is most likely to shorten this stage?""",
a=["Enable Adaptive Query Execution skew-join handling (or salt the join key) so the oversized partition is split into smaller tasks.",
   "Add more worker nodes to the cluster without changing the query.",
   "Cache both input DataFrames before the join.",
   "Lower `spark.sql.shuffle.partitions` from 200 to 50."],
e="""A max far above the median for both duration and shuffle read size means data skew: one key holds most of the rows, so one task does most of the work. AQE's skew join optimization (`spark.sql.adaptive.skewJoin.enabled`) splits skewed partitions automatically. Salting the key works too.

More nodes don't help a single straggler task. Caching doesn't change the partition sizes. Fewer shuffle partitions make each partition larger."""),

dict(d="Cost & Performance Optimization", q="""A data engineer compares the plans of a join query in the Spark UI. The initial physical plan shows a `SortMergeJoin`, but the final plan executed shows a `BroadcastHashJoin`.

What explains the change?""",
a=["Adaptive Query Execution re-optimized the plan at runtime after shuffle statistics showed one side was smaller than the broadcast threshold.",
   "Dynamic file pruning rewrote the join after skipping files in the larger table.",
   "Statistics from a previous `ANALYZE TABLE` run made the optimizer swap strategies after the query finished.",
   "Photon always replaces sort-merge joins with broadcast joins, whatever the table size."],
e="""AQE reoptimizes queries at stage boundaries using statistics gathered at runtime. If a join side turns out to be small after filtering, AQE can switch a sort-merge join to a broadcast hash join. The initial and final plans then differ.

Statistics from `ANALYZE TABLE` are used when the query is planned, not after it runs."""),

dict(d="Security & Compliance", q="""The `hr.core.employees` table has an `ssn` column. Everyone outside the `hr_admins` group should see only the last four digits. Which implementation meets this requirement?""",
a=["""CREATE FUNCTION hr.core.mask_ssn(ssn STRING)
RETURN CASE WHEN is_account_group_member('hr_admins') THEN ssn
            ELSE concat('***-**-', right(ssn, 4)) END;

ALTER TABLE hr.core.employees ALTER COLUMN ssn SET MASK hr.core.mask_ssn;""",
   """CREATE FUNCTION hr.core.mask_ssn(ssn STRING)
RETURN is_account_group_member('hr_admins');

ALTER TABLE hr.core.employees SET ROW FILTER hr.core.mask_ssn ON (ssn);""",
   """ALTER TABLE hr.core.employees ALTER COLUMN ssn
SET TAGS ('mask' = 'last4');""",
   """REVOKE SELECT (ssn) ON TABLE hr.core.employees FROM `account users`;
GRANT SELECT (ssn) ON TABLE hr.core.employees TO `hr_admins`;"""],
e="""A column mask is a SQL UDF. Its first parameter receives the column value, and it returns the value to display. Attach it with `ALTER TABLE ... ALTER COLUMN ... SET MASK`. The `is_account_group_member()` check lets `hr_admins` see the full value.

A row filter hides whole rows, not values. A tag alone enforces nothing unless an ABAC policy uses it. Unity Catalog has no column-level GRANT/REVOKE on SELECT."""),

dict(d="Security & Compliance", q="""The `customers` Delta table has deletion vectors enabled. To honor a right-to-be-forgotten request, a data engineer runs:

```
DELETE FROM customers WHERE customer_id = 4821;
```

Compliance requires that the customer's data is physically removed from storage. What should the engineer do next?""",
a=["Run `REORG TABLE customers APPLY (PURGE)` to rewrite the affected files, then run `VACUUM` once the old files are past the retention period.",
   "Run `VACUUM customers` right after the DELETE. With deletion vectors, it immediately removes the deleted rows from the data files.",
   "Run `FSCK REPAIR TABLE customers` to physically remove the rows marked as deleted.",
   "Disable deletion vectors with `ALTER TABLE ... SET TBLPROPERTIES`. This rewrites all existing files without the deleted rows."],
e="""With deletion vectors, DELETE only marks rows as removed. The rows stay in data files that the table still references. `REORG TABLE ... APPLY (PURGE)` rewrites those files without the deleted rows. A later `VACUUM` then removes the old files from storage once they are past the retention threshold.

`FSCK REPAIR TABLE` only removes log entries for files that are missing from storage. Turning off deletion vectors doesn't rewrite existing files."""),

dict(d="Data Governance", q="""An analyst was granted `SELECT` on the table `sales.reporting.daily_revenue`, but their query still fails with an insufficient privileges error. No other grants exist for the analyst.

What is the minimum additional access they need?""",
a=["`USE CATALOG` on `sales` and `USE SCHEMA` on `sales.reporting`",
   "`BROWSE` on the `sales` catalog",
   "`MODIFY` on `sales.reporting.daily_revenue`",
   "`ALL PRIVILEGES` on the `sales.reporting` schema"],
e="""To read a table in Unity Catalog, a user needs `SELECT` on the table, `USE SCHEMA` on its schema, and `USE CATALOG` on its catalog.

`BROWSE` only lets the user see metadata. `MODIFY` and `ALL PRIVILEGES` grant much more than the task needs."""),

dict(d="Debugging & Deploying", q="""A Databricks job has three parallel ingestion tasks, followed by a `cleanup` task that releases temporary resources. `cleanup` must run once all three upstream tasks have finished, whether they succeeded or failed.

Which "Run if" condition should `cleanup` use?""",
a=["All done", "All succeeded", "At least one failed", "None failed"],
e="""The "Run if" condition controls when a task runs based on the outcome of its dependencies:

- **All done** runs once all dependencies have completed, whatever their outcome. This fits a cleanup task.
- **All succeeded** (the default) runs only if every dependency succeeded.
- **At least one failed** runs only if something failed.
- **None failed** runs if no dependency failed (skipped is allowed)."""),

dict(d="Data Modeling", q="""A data engineer builds a customer dimension using AUTO CDC in Lakeflow Spark Declarative Pipelines:

```
CREATE FLOW customers_flow AS AUTO CDC INTO dim_customers
FROM STREAM(customers_cdc)
KEYS (customer_id)
SEQUENCE BY update_ts
COLUMNS * EXCEPT (operation)
STORED AS SCD TYPE 2;
```

Which columns does the pipeline add to `dim_customers` to track the validity period of each version?""",
a=["`__START_AT` and `__END_AT`",
   "`_commit_version` and `_commit_timestamp`",
   "`valid_from` and `valid_to`",
   "`_change_type` and `_sequence_num`"],
e="""With SCD Type 2, AUTO CDC keeps a history of every version of a record. It adds `__START_AT` and `__END_AT`, which take the values of the `SEQUENCE BY` column. `__END_AT` is NULL for the current version.

`_commit_version`, `_commit_timestamp`, and `_change_type` are metadata columns of the Delta Change Data Feed."""),
]
