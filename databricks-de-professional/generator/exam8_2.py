Q = [
dict(d="Transformation, Cleansing & Quality", q="""A streaming query reads the Delta table `silver.orders`. Someone adds a new column to `silver.orders` with `ALTER TABLE ... ADD COLUMN`. How does the streaming query behave?""",
a=["It stops with an error when it detects the schema change. After a restart, it continues with the new schema (with schema evolution enabled on the sink if the column should be written).",
   "It ignores the new column forever, even after restarts.",
   "It adds the new column to its output automatically, without stopping.",
   "It reprocesses the whole table from version 0 with the new schema."],
e="""A Delta streaming source fixes its schema when the query starts. When it sees a schema change in the log, the query fails so the change can be handled safely. In production, configure job retries so the query restarts and picks up additive changes. Non-additive changes, such as renames or drops with column mapping, need extra options."""),

dict(d="Transformation, Cleansing & Quality", q="""A data engineer runs this statement on a large Delta table:

```
ALTER TABLE customers ALTER COLUMN email SET NOT NULL;
```

Some existing rows have a NULL `email`. What happens?""",
a=["The command fails, because existing data breaks the constraint, and the table is left unchanged.",
   "The constraint is added, and the existing NULL rows are deleted automatically.",
   "The constraint is added, and it only applies to rows written from now on.",
   "The NULL values are replaced with empty strings automatically."],
e="""Delta checks existing data before it adds a NOT NULL or CHECK constraint, and the command fails if any row violates it. Clean up or backfill the data first, then add the constraint. After that, writes that break it fail."""),

dict(d="Transformation, Cleansing & Quality", q="""In a `foreachBatch` function, each micro-batch DataFrame is transformed and then written to two different Delta tables. The engineer notices that the source is read and the transformations are computed twice per batch.

What should they do?""",
a=["Persist the batch DataFrame (`batch_df.persist()`) before the two writes, and call `unpersist()` after them.",
   "Write to both tables with one `saveAsTable` call that takes a list of table names.",
   "Use `outputMode(\"complete\")` so the batch is only computed once.",
   "Set `spark.sql.shuffle.partitions` to 1."],
e="""Each write is a separate action, so the batch's lineage is computed again for each one. Persisting the DataFrame computes it once and reuses it for both writes. Unpersisting frees the memory before the next batch.

`saveAsTable` takes a single table name, and the output mode doesn't affect how many times the batch is recomputed."""),

dict(d="Transformation, Cleansing & Quality", q="""An SDP streaming table should use liquid clustering on `customer_id`. How is this defined in SQL?""",
a=["""CREATE OR REFRESH STREAMING TABLE orders_silver
CLUSTER BY (customer_id)
AS SELECT * FROM STREAM(orders_bronze)""",
   """CREATE OR REFRESH STREAMING TABLE orders_silver
PARTITIONED BY (customer_id) ZORDER BY (customer_id)
AS SELECT * FROM STREAM(orders_bronze)""",
   """CREATE OR REFRESH STREAMING TABLE orders_silver
AS SELECT * FROM STREAM(orders_bronze)
ORDER BY customer_id""",
   """CREATE OR REFRESH STREAMING TABLE orders_silver
TBLPROPERTIES ('cluster' = 'customer_id')
AS SELECT * FROM STREAM(orders_bronze)"""],
e="""Pipeline tables accept a `CLUSTER BY` clause in SQL, or `cluster_by` in Python decorators, to enable liquid clustering. Partitioning can't be combined with Z-ordering in a table definition, and `ORDER BY` in a streaming query doesn't set the layout."""),

dict(d="Transformation, Cleansing & Quality", q="""Auto Loader runs with an explicit schema in which `quantity` is INT, and with the default rescued data column. A file arrives with `"quantity": "twelve"`. What happens to this value?""",
a=["`quantity` is set to NULL for that record, and the original value is kept in the `_rescued_data` column as JSON, along with the source file path.",
   "The stream fails because of a type mismatch.",
   "The whole record is dropped without a trace.",
   "The table's `quantity` column is changed to STRING automatically."],
e="""The rescued data column catches values that don't fit the schema, whether because of a type mismatch, a case mismatch, or an unexpected field. The affected column is NULL, and `_rescued_data` holds the original value so it can be reprocessed or quarantined."""),

dict(d="Transformation, Cleansing & Quality", q="""A buggy job wrote corrupted data into the Delta table `gold.revenue` as version 57. Version 56 was correct. What is the fastest way to bring the table back to its correct state?""",
a=["`RESTORE TABLE gold.revenue TO VERSION AS OF 56;`",
   "`DELETE FROM gold.revenue WHERE _commit_version = 57;`",
   "`VACUUM gold.revenue RETAIN 0 HOURS;`",
   "`DROP TABLE gold.revenue;` followed by `UNDROP TABLE gold.revenue;`"],
e="""`RESTORE` returns a Delta table to an earlier version or timestamp by recording a new commit, so history is kept and the restore itself can be undone. The files of the target version must still exist, meaning they haven't been vacuumed.

Tables have no `_commit_version` column (that only exists in CDF output). VACUUM removes the files you would need."""),

dict(d="Transformation, Cleansing & Quality", q="""In a silver transformation, rows with a NULL `customer_id` or a NULL `order_id` must be removed, but rows with NULLs in other columns must be kept. Which code does this?""",
a=["""df.dropna(subset=["customer_id", "order_id"])""",
   """df.dropna()""",
   """df.dropna(how="all")""",
   """df.fillna(0, subset=["customer_id", "order_id"])"""],
e="""`dropna(subset=...)` checks only the listed columns, and with the default `how="any"` it drops a row when any of them is NULL.

- Plain `dropna()` checks every column.
- `how="all"` drops a row only when all columns are NULL.
- `fillna` replaces the NULLs instead of removing the rows."""),

dict(d="Data Sharing & Federation", q="""A provider wants to share every table in the schema `sales.public`, including tables added to the schema later, without updating the share each time. What should they do?""",
a=["`ALTER SHARE partner_share ADD SCHEMA sales.public;`",
   "Add each table individually, and run a nightly job that adds new tables to the share",
   "`GRANT SELECT ON SCHEMA sales.public TO RECIPIENT partner;`",
   "Create a view that unions every table in the schema, and share the view"],
e="""You can add a whole schema to a share. Its current and future tables (and other supported objects) are then shared automatically.

Recipients receive access through `GRANT ... ON SHARE`, not schema grants. A union view doesn't work for tables with different schemas."""),

dict(d="Data Sharing & Federation", q="""The table `sales.global_orders` is partitioned by `country`. A provider shares it with many recipients, and each recipient may only see its own country's partition. They want to use a single share.

What should they do?""",
a=["Set a `country` property on each recipient, and add the table to the share with `PARTITION (country = CURRENT_RECIPIENT('country'))`",
   "Create one share per country, each with a static partition filter",
   "Add a row filter to the table that uses `current_user()`",
   "Share the whole table, and ask each recipient to filter on their own country"],
e="""Recipient properties combined with `CURRENT_RECIPIENT()` in a share's partition specification filter the data dynamically for each recipient, so one share serves many recipients.

Creating a share per country works, but it doesn't scale. Trusting recipients to filter the data themselves exposes everything."""),

dict(d="Data Sharing & Federation", q="""A partnership has ended, and the provider must stop recipient `acme` from reading `sales_share` right away, while keeping the share for other recipients. Which command should they run?""",
a=["`REVOKE SELECT ON SHARE sales_share FROM RECIPIENT acme;`",
   "`DROP SHARE sales_share;`",
   "`ALTER SHARE sales_share REMOVE TABLE sales.orders;`",
   "`VACUUM sales.orders;`"],
e="""Recipients are granted access with `GRANT SELECT ON SHARE ... TO RECIPIENT`, and access is removed by revoking that grant. You can also drop the recipient entirely.

Dropping the share or removing tables from it would affect every recipient."""),

dict(d="Data Sharing & Federation", q="""An admin has created the Lakehouse Federation connection `pg_conn`. A data engineer needs to create a foreign catalog with this connection. Which privilege must the engineer have on the connection, in addition to `CREATE CATALOG` on the metastore?""",
a=["`CREATE FOREIGN CATALOG` on the connection",
   "`SELECT` on the connection",
   "`USE SCHEMA` on the connection",
   "`MODIFY` on the connection"],
e="""Connections are securable objects in Unity Catalog. Creating a foreign catalog from a connection requires `CREATE FOREIGN CATALOG` on that connection (or ownership of it), plus `CREATE CATALOG` on the metastore. Users who query the foreign catalog then need the usual `USE CATALOG`, `USE SCHEMA`, and `SELECT` privileges on its objects."""),

dict(d="Data Sharing & Federation", q="""A pipeline needs to look up a small, frequently changing `exchange_rates` table that lives in an operational MySQL database. It must always use the current values, and the table has only a few thousand rows.

Which approach is most appropriate?""",
a=["Query the table live through a Lakehouse Federation foreign catalog",
   "Build a nightly bulk export to CSV and load it with Auto Loader",
   "Ask the MySQL team to share the table with Delta Sharing",
   "Copy the table once with a deep clone"],
e="""For small, current lookups, querying through federation gives up-to-date values with no ingestion pipeline to maintain, and the load on the source is minimal.

A nightly export goes stale, MySQL can't share data through Delta Sharing, and deep clone only works on Delta tables."""),

dict(d="Monitoring & Alerting", q="""A team uses data profiling (Lakehouse Monitoring) on the table `orders`. They also want to track a business-specific metric over time: the percentage of orders with a negative discount.

What should they do?""",
a=["Add a custom metric to the monitor, defined as a SQL expression, so it is computed with the built-in metrics and stored in the metric tables",
   "Add a CHECK constraint that rejects negative discounts",
   "Create a new monitor that uses the InferenceLog profile type",
   "Query the drift metrics table. Every possible business metric is computed automatically."],
e="""Monitors support custom aggregate, derived, and drift metrics defined with SQL expressions. They are calculated on each refresh, stored in the profile and drift metrics tables, and can be used in dashboards and alerts.

Constraints reject data and don't measure it."""),
]
