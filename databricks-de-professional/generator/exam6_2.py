Q = [
dict(d="Security & Compliance", q="""A table stores customer national ID numbers. Most users must never see the plain-text values, but a small compliance group must be able to recover the original values when needed. The encryption key is stored in the secret scope `kms`.

Which approach meets both requirements?""",
a=["Store `aes_encrypt(national_id, secret('kms', 'pii_key'))`, and let only the compliance group read the key so they can use `aes_decrypt` when needed.",
   "Store `sha2(national_id, 256)` and remove the original column. Compliance can reverse the hash when needed.",
   "Store `base64(national_id)`, since base64 values can't be read without the secret.",
   "Apply a column mask that returns `'****'` to everyone, and remove the original values from the table."],
e="""`aes_encrypt` and `aes_decrypt` give reversible encryption. If the key comes from a secret with the `secret()` function, only principals with READ access to that secret scope can decrypt.

- SHA-2 is a one-way hash and can't be reversed.
- Base64 is an encoding, not protection.
- A mask over deleted data leaves nothing to recover."""),

dict(d="Security & Compliance", q="""Several analysts need to share one interactive cluster to query Unity Catalog tables. Each user's code must be isolated from the others, and their individual Unity Catalog permissions must be enforced.

Which access mode should the cluster use?""",
a=["Standard (formerly shared) access mode",
   "No isolation shared access mode",
   "Dedicated (formerly single user) access mode assigned to one analyst",
   "Any access mode, since Unity Catalog permissions are enforced the same way in all of them"],
e="""Standard access mode lets several users share compute safely. It isolates users from each other and enforces each user's Unity Catalog permissions.

- Dedicated access mode is for one user (or one group).
- No isolation shared is a legacy mode that doesn't support Unity Catalog."""),

dict(d="Data Governance", q="""A data engineering team needs to upload raw files into the Unity Catalog volume `main.raw.landing` and read them back. They already have `USE CATALOG` and `USE SCHEMA`.

Which additional privileges should they be granted?""",
a=["`READ VOLUME` and `WRITE VOLUME` on `main.raw.landing`",
   "`SELECT` and `MODIFY` on `main.raw.landing`",
   "`CREATE TABLE` on the `main.raw` schema",
   "`READ FILES` and `WRITE FILES` on the metastore"],
e="""Volumes have their own privileges: `READ VOLUME` lets you list and read files, and `WRITE VOLUME` lets you add, change, and delete files. Both also require `USE CATALOG` and `USE SCHEMA`.

`SELECT` and `MODIFY` apply to tables. `READ FILES` and `WRITE FILES` apply to external locations, not volumes."""),

dict(d="Data Governance", q="""A team needs to create Unity Catalog external tables over data in an S3 bucket that Databricks can't access yet. In what order should the objects be set up?""",
a=["Create a storage credential for the cloud IAM role, create an external location that uses it for the bucket path, then grant `CREATE EXTERNAL TABLE` on the external location to the team.",
   "Create the external tables with `LOCATION 's3://...'`, then create a storage credential for them.",
   "Create a Lakehouse Federation connection to S3, then a foreign catalog for the bucket.",
   "Mount the bucket to DBFS with an access key, then register the mount point as a catalog."],
e="""A storage credential holds the cloud identity, such as an IAM role. An external location pairs a storage path with a credential and is governed by Unity Catalog. Users need privileges on the external location, such as `CREATE EXTERNAL TABLE` or `READ FILES`, to use the path.

DBFS mounts are a legacy approach and are not governed by Unity Catalog."""),

dict(d="Data Governance", q="""An engineer accidentally dropped the Unity Catalog managed table `prod.sales.orders` two days ago. What is the quickest way to get the table back with its data and history?""",
a=["`UNDROP TABLE prod.sales.orders;`",
   "`RESTORE TABLE prod.sales.orders TO VERSION AS OF 0;`",
   "`SELECT * FROM prod.sales.orders TIMESTAMP AS OF date_sub(current_date(), 3);`",
   "`CREATE TABLE prod.sales.orders LOCATION '<managed storage path>';`"],
e="""Unity Catalog keeps dropped managed tables for a retention period (7 days), and `UNDROP TABLE` recovers them. Use `SHOW TABLES DROPPED` to see the tables that can be recovered.

`RESTORE` and time travel need the table to exist. Managed storage paths are not meant to be registered by hand."""),

dict(d="Data Governance", q="""The company has `dev`, `staging`, and `prod` workspaces attached to the same Unity Catalog metastore. The `prod_data` catalog must only be usable from the `prod` workspace, even by users who have privileges on it.

What should the admin configure?""",
a=["Workspace-catalog binding: set `prod_data` so it is not open to all workspaces, and bind it only to the `prod` workspace.",
   "Revoke `USE CATALOG` on `prod_data` from every user, and grant it again only while they work in the `prod` workspace.",
   "Create a separate metastore for each workspace, and copy `prod_data` with deep clones.",
   "Add a row filter to every table in `prod_data` that checks the current workspace ID."],
e="""Workspace-catalog binding limits which workspaces can access a catalog. From a workspace that isn't bound, users can't use the catalog, whatever their privileges. This is the standard way to isolate environments that share a metastore.

There should normally be one metastore per region, not one per workspace."""),

dict(d="Debugging & Deploying", q="""An hourly job sometimes runs longer than an hour. When that happens, the team wants the next scheduled run to wait and start after the current one finishes, rather than being skipped or running at the same time.

How should the job be configured?""",
a=["Keep the maximum concurrent runs at 1 and enable queueing for the job.",
   "Increase the maximum concurrent runs to 2 so the runs can overlap.",
   "Set the job timeout to 60 minutes so that runs never overlap.",
   "Add task retries with a delay of 60 minutes."],
e="""With queueing enabled, runs that can't start because of the concurrency limit wait in a queue instead of being skipped. With max concurrent runs set to 1, they start one after another.

Allowing two concurrent runs causes overlap. A timeout cancels work. Retries only apply to failures."""),

dict(d="Debugging & Deploying", q="""A downstream job should start whenever new data is committed to the Unity Catalog table `silver.orders`, instead of running on a fixed schedule. Which trigger type should it use?""",
a=["A table update trigger on `silver.orders`",
   "A file arrival trigger on the storage path of `silver.orders`",
   "A continuous trigger",
   "A cron schedule that runs every minute"],
e="""A table update trigger starts a job when the monitored tables are updated, which suits event-driven pipelines between tables.

- File arrival triggers watch volumes or external locations for new files, not Delta commits.
- A continuous trigger runs the job all the time.
- Polling every minute wastes resources."""),

dict(d="Debugging & Deploying", q="""A notebook task in a job runs on serverless compute and needs the PyPI package `great-expectations`. How should the dependency be provided?""",
a=["Add the package to the task's serverless environment (its dependencies list), or install it with `%pip install` in the notebook.",
   "Add a cluster-scoped init script that runs `pip install great-expectations`.",
   "Install the package as a cluster library on an all-purpose cluster, and keep the task on serverless.",
   "Put the wheel file in DBFS root, which serverless compute loads automatically on startup."],
e="""Serverless compute doesn't support init scripts or cluster libraries. Dependencies go in the environment spec (the environment version plus a dependencies list) or are installed in the notebook with `%pip`.

A library on a different cluster doesn't affect serverless tasks."""),

dict(d="Debugging & Deploying", q="""What is the difference between `%run ./helpers` and `dbutils.notebook.run("./helpers", 600, {"env": "prod"})`?""",
a=["`%run` runs the notebook in the caller's context, so its functions and variables become available to the caller. `dbutils.notebook.run` runs it as a separate run with parameters and returns the value passed to `dbutils.notebook.exit()`.",
   "Both run the notebook in the caller's context. `dbutils.notebook.run` additionally sets a timeout.",
   "`%run` starts a new job cluster for the notebook, while `dbutils.notebook.run` reuses the caller's Spark session.",
   "`%run` accepts widget parameters and returns a value, while `dbutils.notebook.run` can only run notebooks in the same folder."],
e="""`%run` effectively includes the other notebook, which is useful for shared function definitions. `dbutils.notebook.run` starts a separate notebook run. You pass parameters as widget values and get back a string from `dbutils.notebook.exit()`. Definitions in the called notebook are not shared with the caller."""),

dict(d="Debugging & Deploying", q="""In the Spark UI Executors tab, several executors show GC time at about 40% of task time, and tasks are slower than usual. What is the most likely cause, and how should it be addressed?""",
a=["The executors are under memory pressure. Use memory-optimized instances or make partitions smaller, and avoid caching data that isn't needed.",
   "The cluster has too much memory. Use smaller instance types to reduce garbage collection.",
   "Disk I/O is the bottleneck. Turn off the disk cache to free CPU for garbage collection.",
   "The driver is overloaded. Increase driver memory to reduce executor garbage collection."],
e="""High JVM garbage-collection time means executors are short of heap memory, for example from large partitions, too much caching, or wide rows.

Giving executors more memory per core, increasing the partition count so each partition is smaller, or unpersisting unused cached data all reduce GC overhead."""),

dict(d="Debugging & Deploying", q="""A job runs on job clusters. When a run fails overnight, the driver and executor logs are no longer available the next morning because the cluster has been terminated.

How can the team keep these logs for troubleshooting?""",
a=["Configure cluster log delivery in the job cluster's settings, with a destination such as a Unity Catalog volume or a cloud storage path.",
   "Switch the job to an all-purpose cluster that never terminates.",
   "Add `print()` statements to the notebook so the logs show up in the notebook output.",
   "Turn on Change Data Feed on the job's output tables."],
e="""Cluster log delivery periodically copies driver and executor logs and event logs to a destination you choose, so they are kept after the cluster terminates.

Keeping clusters running forever is expensive. Print statements only capture what you add yourself."""),

dict(d="Developing Code (Python & SQL)", q="""A data engineer needs to upsert the DataFrame `updates_df` into the Delta table `silver.customers` with the Python API, matching on `customer_id`. Which code does this?""",
a=["""from delta.tables import DeltaTable
(DeltaTable.forName(spark, "silver.customers").alias("t")
   .merge(updates_df.alias("s"), "t.customer_id = s.customer_id")
   .whenMatchedUpdateAll()
   .whenNotMatchedInsertAll()
   .execute())""",
   """from delta.tables import DeltaTable
(DeltaTable.forName(spark, "silver.customers").alias("t")
   .merge(updates_df.alias("s"), "t.customer_id = s.customer_id")
   .whenMatchedUpdateAll()
   .whenNotMatchedInsertAll())""",
   """(spark.table("silver.customers").alias("t")
   .merge(updates_df.alias("s"), "t.customer_id = s.customer_id")
   .whenMatchedUpdateAll()
   .execute())""",
   """updates_df.write.mode("merge") \\
   .option("mergeKey", "customer_id") \\
   .saveAsTable("silver.customers")"""],
e="""The `DeltaTable` builder sets up a MERGE with `merge()` plus `whenMatched...` and `whenNotMatched...` clauses, and nothing runs until `.execute()` is called.

A plain DataFrame has no `merge` method, and `DataFrameWriter` has no `"merge"` mode."""),

dict(d="Developing Code (Python & SQL)", q="""The bronze table `raw_events` has a STRING column `raw` that holds JSON documents. An analyst needs the nested value `customer.address.city` as a string, without defining a schema.

Which query returns it?""",
a=["""SELECT raw:customer.address.city::string AS city FROM raw_events""",
   """SELECT raw.customer.address.city AS city FROM raw_events""",
   """SELECT json_tuple(raw, 'customer.address.city') AS city FROM raw_events""",
   """SELECT from_json(raw).customer.address.city AS city FROM raw_events"""],
e="""Databricks SQL can extract fields from JSON strings (and VARIANT columns) using the `:` path syntax, with `::` to cast the result.

- Dot notation only works on STRUCT columns.
- `json_tuple` only reads top-level keys.
- `from_json` needs a schema."""),

dict(d="Developing Code (Python & SQL)", q="""A team ingests semi-structured event payloads whose fields change often. They are deciding whether to store each payload as a JSON STRING or as a VARIANT column.

What is the main advantage of VARIANT?""",
a=["VARIANT stores the data parsed in an efficient binary format, so extracting fields is much faster than parsing JSON strings at query time, and no fixed schema is needed.",
   "VARIANT enforces a strict schema, so payloads with unexpected fields are rejected when written.",
   "VARIANT flattens every nested field into its own top-level column when the data is written.",
   "VARIANT columns are excluded from Delta file statistics, which makes writes faster."],
e="""The VARIANT type (`parse_json()` to create values, and `:` paths or `variant_get` to read them) keeps the flexibility of JSON while storing values in an encoded binary form. Reads are much faster than repeatedly parsing strings, and the schema can still change freely."""),
]
