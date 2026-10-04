Q = [
dict(d="Security & Compliance", q="""A library installed on a classic cluster reads a database password from the environment variable `DB_PASSWORD`. The password is stored in the secret scope `prod-scope` under the key `db-password`.

How should the data engineer provide this variable without exposing the password in plain text?""",
a=["Set the environment variable in the cluster configuration to `DB_PASSWORD={{secrets/prod-scope/db-password}}`.",
   "Write the password into an init script that exports `DB_PASSWORD` when the cluster starts.",
   "Pass the password as a job parameter and read it with `dbutils.widgets.get`.",
   "Store the password in a Delta table restricted to admins, and read it into `os.environ` at the start of each notebook."],
e="""Cluster Spark configuration properties and environment variables can reference a secret with `{{secrets/<scope>/<key>}}`. The value is resolved when the cluster starts and never appears in plain text in the configuration.

Init scripts, job parameters, and tables would all store or show the password in clear text."""),

dict(d="Security & Compliance", q="""The `sales` table has a `region` column. The mapping table `sec.region_access(user_email, region)` lists which regions each user may see. Each user should see only the rows for their regions, whichever tool they query from.

Which implementation meets this requirement?""",
a=["""CREATE FUNCTION sec.region_filter(r STRING)
RETURN EXISTS (SELECT 1 FROM sec.region_access a
               WHERE a.user_email = current_user() AND a.region = r);

ALTER TABLE sales SET ROW FILTER sec.region_filter ON (region);""",
   """CREATE FUNCTION sec.region_filter(r STRING)
RETURN EXISTS (SELECT 1 FROM sec.region_access a
               WHERE a.user_email = current_user() AND a.region = r);

ALTER TABLE sales ALTER COLUMN region SET MASK sec.region_filter;""",
   """GRANT SELECT ON TABLE sales
WHERE region IN (SELECT region FROM sec.region_access) TO `account users`;""",
   """CREATE VIEW sales_vw AS SELECT * FROM sales
WHERE is_account_group_member(region);"""],
e="""A row filter is a boolean SQL UDF attached with `SET ROW FILTER ... ON (columns)`. It runs for every row, so it can check the current user against a mapping table. This scales better than writing one rule per group.

- A column mask changes the values in a column but doesn't remove rows.
- `GRANT ... WHERE` is not valid syntax.
- The view would need a group named after each region, and the base table could still be queried directly."""),

dict(d="Security & Compliance", q="""A company has hundreds of tables across several schemas. Every column holding an email address is labeled with the governed tag `pii : email`. The security team wants one central rule that masks all of these columns for non-privileged users, and it must also cover tables created later.

Which approach fits best?""",
a=["Create an attribute-based access control (ABAC) policy at the catalog level that applies a masking UDF to columns whose governed tag matches `pii : email`.",
   "Create a separate column mask on every email column, and add a CI check that new tables also get one.",
   "Create a dynamic view over every table and revoke direct access to the base tables.",
   "Use Delta Sharing to share masked copies of the tables with non-privileged users."],
e="""ABAC policies in Unity Catalog combine governed tags with UDFs. A single policy defined on a catalog or schema applies to every matching column, including in tables added later, so you don't manage masks table by table.

Per-table masks and dynamic views work, but they don't scale and can drift out of sync. Delta Sharing is not a tool for internal access control."""),

dict(d="Data Governance", q="""A senior engineer who owns several production tables in Unity Catalog is leaving the company. What is the recommended way to handle ownership of these tables?""",
a=["Transfer ownership to a group or service principal, for example: `ALTER TABLE prod.sales.orders OWNER TO data_platform_admins`.",
   "Grant `ALL PRIVILEGES` on each table to the engineer's replacement, and keep the original owner.",
   "Deep clone each table into a schema owned by the replacement, then drop the originals.",
   "Leave ownership as is. Unity Catalog moves ownership of tables to the metastore admin when a user is deactivated."],
e="""The owner of an object has full control over it, including the right to grant privileges. It's best practice to have groups or service principals own production objects rather than individuals, so access doesn't depend on any one person.

`ALL PRIVILEGES` doesn't change ownership. Cloning creates new objects and loses history and grants. Ownership is not moved automatically."""),

dict(d="Data Governance", q="""A data engineer wants to query, programmatically, every downstream table that was written using data from `prod.bronze.orders` in the last 90 days. Which source provides this information?""",
a=["The `system.access.table_lineage` system table, filtered on `source_table_full_name = 'prod.bronze.orders'`",
   "The output of `DESCRIBE HISTORY prod.bronze.orders`",
   "The view `prod.information_schema.tables`, filtered on `table_name = 'orders'`",
   "The `system.billing.usage` table, filtered on the table name"],
e="""Unity Catalog captures lineage automatically for queries run on Databricks and exposes it in the system tables `system.access.table_lineage` and `system.access.column_lineage`. Filtering on the source table lists the target tables written from it, with event times.

`DESCRIBE HISTORY` only shows operations that wrote to the table itself."""),

dict(d="Data Governance", q="""A governance team needs a list of every column in the `prod` catalog that has the tag `pii`, including schema and table names. Which query returns this?""",
a=["""SELECT schema_name, table_name, column_name, tag_value
FROM prod.information_schema.column_tags
WHERE tag_name = 'pii';""",
   """SHOW TAGS IN CATALOG prod WHERE tag_name = 'pii';""",
   """DESCRIBE DETAIL prod.* WHERE tag_name = 'pii';""",
   """SELECT * FROM system.access.audit WHERE action_name = 'pii';"""],
e="""Unity Catalog exposes tag assignments through `information_schema` views, such as `catalog_tags`, `schema_tags`, `table_tags`, and `column_tags`. Querying `column_tags` with a filter on `tag_name` lists the tagged columns.

The other statements are invalid or return unrelated data."""),

dict(d="Debugging & Deploying", q="""In a job, the notebook task `ingest` counts the rows it loaded. The next task, `validate`, must read that count. Which approach is correct?""",
a=["""In `ingest`: `dbutils.jobs.taskValues.set(key="row_count", value=n)`
In `validate`: `dbutils.jobs.taskValues.get(taskKey="ingest", key="row_count")`""",
   """In `ingest`: `dbutils.widgets.text("row_count", str(n))`
In `validate`: `dbutils.widgets.get("row_count")`""",
   """In `ingest`: `spark.conf.set("row_count", n)`
In `validate`: `spark.conf.get("row_count")`""",
   """In `ingest`: `dbutils.notebook.exit(n)`
In `validate`: `dbutils.notebook.run("ingest", 60)`"""],
e="""Task values let tasks in the same job run pass small values to each other. Set a value with `dbutils.jobs.taskValues.set`, and read it in a downstream task with `taskValues.get` or the dynamic reference `{{tasks.ingest.values.row_count}}`.

- Widgets are local to one notebook.
- Spark confs don't carry over between tasks, which may run on different compute.
- `dbutils.notebook.run` would run the ingest notebook again."""),

dict(d="Debugging & Deploying", q="""A daily job must run the `full_refresh` task only on Sundays, and the `incremental_load` task on every other day. Which configuration does this in a single job?""",
a=["Add an If/else condition task that checks whether `{{job.start_time.iso_weekday}}` equals `7`. `full_refresh` depends on its true branch and `incremental_load` on its false branch.",
   "Add a For each task that loops over the days of the week and runs `full_refresh` once per iteration.",
   "Set the \"Run if\" condition of `full_refresh` to \"At least one succeeded\" and of `incremental_load` to \"All failed\".",
   "Package both tasks in one Python wheel task that reads the system clock and calls `sys.exit()` on the wrong day."],
e="""The If/else condition task compares two values. These can be dynamic value references such as the run's start weekday (`iso_weekday`, where Monday = 1 and Sunday = 7). Downstream tasks depend on the true or false outcome, so only one branch runs.

For each tasks repeat a nested task over a list of inputs. "Run if" conditions only look at whether upstream tasks succeeded or failed."""),

dict(d="Debugging & Deploying", q="""A Declarative Automation Bundle (formerly Databricks Asset Bundle) defines this target:

```
targets:
  dev:
    mode: development
    default: true
```

A developer runs `databricks bundle deploy -t dev`. Which statement describes the deployed resources?""",
a=["Resource names get the prefix `[dev <username>]`, and job schedules and triggers are paused, so each developer gets an isolated copy that doesn't run automatically.",
   "Resources are deployed under the production service principal, with schedules active, and overwrite the jobs used by the production target.",
   "The bundle is checked but not deployed. Development mode only runs `bundle validate`.",
   "All jobs in the bundle start running as soon as the deployment finishes."],
e="""`mode: development` sets defaults suited to personal development:

- Deployed resources get the prefix `[dev ${workspace.current_user.short_name}]`.
- Schedules and triggers are paused.
- Concurrent runs are allowed.
- Resources deploy to a per-user location.

Production mode adds checks instead, such as requiring an explicit `run_as` identity and workspace paths that are not user-specific."""),

dict(d="Debugging & Deploying", q="""In a Declarative Automation Bundle, the variable `catalog` defaults to `dev_catalog`. In a CI pipeline, the team wants to deploy the bundle to the `prod` target and set `catalog` to `prod_catalog` for this deployment only.

Which command should they use?""",
a=["`databricks bundle deploy -t prod --var=\"catalog=prod_catalog\"`",
   "`databricks bundle run -t prod --catalog prod_catalog`",
   "`databricks jobs create --json @databricks.yml --target prod`",
   "`databricks workspace import databricks.yml --var catalog=prod_catalog`"],
e="""`databricks bundle deploy` deploys a bundle's resources to the chosen target (`-t`). You can override a variable with `--var="name=value"` or with an environment variable `BUNDLE_VAR_<name>`.

`bundle run` starts a resource that is already deployed. The jobs and workspace commands don't understand bundle configuration."""),

dict(d="Debugging & Deploying", q="""With the Jobs REST API, a data engineer needs to change only `max_concurrent_runs` on an existing job. All other settings, such as tasks, schedules, and permissions, must stay the same.

Which call should they use?""",
a=["`POST /api/2.2/jobs/update` with `job_id` and a `new_settings` object that contains only `max_concurrent_runs`",
   "`POST /api/2.2/jobs/reset` with `job_id` and a `new_settings` object that contains only `max_concurrent_runs`",
   "`POST /api/2.2/jobs/create` with the same job name and the new `max_concurrent_runs` value",
   "`POST /api/2.2/jobs/runs/submit` with `max_concurrent_runs` in the request body"],
e="""`jobs/update` partially updates a job: only the fields in `new_settings` change. `jobs/reset` replaces the job's entire settings, so sending only one field would remove the tasks and every other setting.

`create` makes a new job, and `runs/submit` starts a one-time run."""),

dict(d="Debugging & Deploying", q="""A notebook that used to run fine started failing with a driver out-of-memory error after this line was added:

```
pdf = spark.table("prod.silver.transactions").toPandas()
```

The table holds about 900 million rows. What is the best fix?""",
a=["Keep the processing distributed with Spark DataFrame operations, or aggregate or filter in Spark first so that only a small result is collected to the driver.",
   "Add more worker nodes so the `toPandas()` call has more memory to work with.",
   "Increase `spark.sql.shuffle.partitions` so the collected data is split into smaller pieces.",
   "Enable Photon on the cluster so `toPandas()` uses vectorized execution."],
e="""`toPandas()` and `collect()` move the whole dataset into the driver's memory. Workers don't help, because the result has to fit on the driver.

Run transformations in Spark (or use the pandas API on Spark), and collect only small, reduced results."""),

dict(d="Data Modeling", q="""A team is considering an identity column as the surrogate key of a new dimension table:

```
customer_sk BIGINT GENERATED ALWAYS AS IDENTITY
```

Which consideration is correct?""",
a=["Identity values are unique but may have gaps, and declaring an identity column turns off concurrent write transactions on the table.",
   "Identity values are always consecutive, with no gaps, even when several jobs write at the same time.",
   "Values in a `GENERATED ALWAYS` identity column can be changed later with an `UPDATE` statement.",
   "An identity column can be added to an existing populated table with `ALTER TABLE ADD COLUMN`, and the existing rows are backfilled."],
e="""Delta Lake identity columns generate unique values, but they are not guaranteed to be consecutive. Declaring an identity column also disables concurrent transactions on the table, so use one only when concurrent writes are not needed.

You can't update `GENERATED ALWAYS` values, and you can't add an identity column to an existing table."""),

dict(d="Data Modeling", q="""A data engineer adds this constraint to a dimension table:

```
ALTER TABLE gold.dim_customer
ADD CONSTRAINT dim_customer_pk PRIMARY KEY (customer_id) RELY;
```

What effect does this have?""",
a=["The constraint is informational and not enforced. `RELY` tells the optimizer it can trust the key for rewrites, such as removing unneeded joins or aggregations, so the team must make sure the key really is unique.",
   "Delta Lake enforces uniqueness, and any write that would insert a duplicate `customer_id` fails.",
   "Delta Lake creates an index on `customer_id` that is used to skip files on point lookups.",
   "Rows in fact tables that reference a deleted `customer_id` are deleted automatically (cascade)."],
e="""Primary and foreign key constraints in Unity Catalog are informational and not enforced, unlike NOT NULL and CHECK constraints. With `RELY`, the optimizer can use the constraint for query optimizations. If the data breaks the constraint, query results can be wrong.

No index is created, and nothing cascades."""),

dict(d="Data Modeling", q="""Finance must report revenue by the sales territory each customer belonged to on the date of each order. Customers sometimes move between territories, and reports must not change when a customer moves later.

How should the customer dimension be modeled?""",
a=["As an SCD Type 2 table with effective start and end dates, joined to orders where the order date falls between them.",
   "As an SCD Type 1 table that overwrites the territory whenever it changes.",
   "As an SCD Type 0 table that keeps each customer's original territory forever.",
   "As an SCD Type 1 table, using Delta time travel to read the version as of each order date."],
e="""SCD Type 2 keeps a new row for each change, with a validity period, so every fact can be matched to the attribute value that was current when it happened.

- Type 1 loses history.
- Type 0 never reflects changes.
- Time travel is limited by retention and VACUUM, and doing it per order date is impractical."""),
]
