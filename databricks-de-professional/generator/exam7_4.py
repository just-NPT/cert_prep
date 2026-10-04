Q = [
dict(d="Data Governance", q="""The governance team wants all employees to be able to find tables in the `analytics` catalog through Catalog Explorer and search, and to see their metadata, so they can request access. They must not be able to read any data.

Which privilege should be granted?""",
a=["`BROWSE` on the `analytics` catalog",
   "`SELECT` on the `analytics` catalog",
   "`USE CATALOG` and `USE SCHEMA` on all schemas in `analytics`",
   "`MANAGE` on the `analytics` catalog"],
e="""`BROWSE` lets users see object metadata in Catalog Explorer, search, and lineage, and request access, without reading data.

`SELECT` grants read access to data. `MANAGE` lets users manage privileges on the object."""),

dict(d="Data Governance", q="""A production job running as the service principal `sp-etl` creates a new table with `CREATE TABLE`. Who owns the new table?""",
a=["The service principal `sp-etl`, since the principal that creates an object becomes its owner",
   "The metastore admin",
   "The user who created the job",
   "Nobody, until ownership is assigned explicitly"],
e="""In Unity Catalog, the principal that creates an object becomes its owner. Because the job runs as `sp-etl`, the service principal owns the table. You can transfer ownership later with `ALTER ... OWNER TO`, for example to a group."""),

dict(d="Data Governance", q="""Analysts get a permission error when they query `system.billing.usage`, even though the system schemas are enabled. What is needed?""",
a=["An admin (or another user with the right privileges) must grant `USE CATALOG` on `system`, `USE SCHEMA` on `system.billing`, and `SELECT` on the table (or schema) to the analysts.",
   "The analysts must use a cluster in dedicated access mode, because system tables can't be queried any other way.",
   "System tables can only be read by account admins, so nobody else can ever be given access.",
   "The analysts must enable Change Data Feed on `system.billing.usage`."],
e="""System tables live in the Unity Catalog `system` catalog and are governed like any other table. Admins grant access with the normal `USE CATALOG`, `USE SCHEMA`, and `SELECT` privileges, usually to specific groups because the data is sensitive."""),

dict(d="Data Governance", q="""How do governed tags differ from ordinary tags in Unity Catalog?""",
a=["Governed tags are defined at the account level with a policy for allowed values and for who can assign them, which keeps tagging consistent. Ordinary tags are free-form key/value pairs.",
   "Governed tags are stored in Delta file statistics, and ordinary tags are stored in the metastore.",
   "Only governed tags can be added to columns. Ordinary tags can only be added to catalogs.",
   "Governed tags mask data automatically without any policy or function."],
e="""Governed tags let admins define a tag key, its allowed values, and who may assign it. This makes tags reliable enough to drive ABAC policies and data classification. Masking or filtering still needs a policy that references the tag."""),

dict(d="Data Governance", q="""The view `sales.reporting.v_revenue` reads from the table `sales.core.orders`. An analyst has `USE CATALOG`, `USE SCHEMA` on `sales.reporting`, and `SELECT` on the view, but no privileges on `sales.core`. The view's owner can read `orders`.

What happens when the analyst queries the view?""",
a=["The query succeeds. The view's owner's privileges are used to read the underlying table, so the analyst doesn't need access to `orders`.",
   "The query fails, because the analyst also needs `SELECT` on `sales.core.orders`.",
   "The query returns only the rows the analyst inserted.",
   "The query succeeds only if the analyst has `MODIFY` on the view."],
e="""In Unity Catalog, a view is resolved with its owner's privileges on the objects it references. Consumers need `SELECT` on the view, plus `USE CATALOG` and `USE SCHEMA` on its parents, but no access to the underlying tables. That's why views work for exposing curated subsets of data."""),

dict(d="Debugging & Deploying", q="""Before deploying a Declarative Automation Bundle from CI, the team wants to catch configuration errors such as invalid YAML, unknown fields, or unresolved variables, without changing anything in the workspace.

Which command should they run?""",
a=["`databricks bundle validate -t prod`",
   "`databricks bundle deploy -t prod --dry-run-all`",
   "`databricks bundle run -t prod`",
   "`databricks bundle destroy -t prod`"],
e="""`bundle validate` checks the bundle configuration and resolves variables for the target, and reports errors and warnings without deploying anything. Running it as a CI step catches mistakes early.

`run` executes resources, and `destroy` deletes them."""),

dict(d="Debugging & Deploying", q="""A feature environment was deployed from a bundle to the `feature-x` target, and the feature has been abandoned. Which command removes everything that bundle deployed for that target?""",
a=["`databricks bundle destroy -t feature-x`",
   "`databricks bundle deploy -t feature-x --delete`",
   "`databricks jobs delete --all`",
   "`databricks workspace delete /Workspace --recursive`"],
e="""`bundle destroy` removes the jobs, pipelines, and other resources deployed for the target, along with the deployment's files and state. It asks for confirmation unless you pass `--auto-approve`.

The other commands either don't exist as written or would delete far more than intended."""),

dict(d="Debugging & Deploying", q="""A bundle deploys a job with a Python wheel task. The wheel should be built from the project source during `databricks bundle deploy` and uploaded with the deployment. How is this configured?""",
a=["Define the wheel in the bundle's `artifacts` mapping (type `whl`, with a build command or `pyproject.toml`), and reference the built wheel in the task's `libraries`.",
   "Build the wheel by hand, upload it to DBFS root, and hard-code the path in the job.",
   "Add `pip install .` to an init script on the job cluster.",
   "Put the wheel's source code in the `variables` section of `databricks.yml`."],
e="""The `artifacts` section tells the CLI to build the package, for example a Python wheel, during deployment and upload it to the workspace. Tasks then refer to it, for example as `./dist/*.whl` in `libraries`. This makes builds reproducible and versioned with the code."""),

dict(d="Debugging & Deploying", q="""A team already has a tested ingestion job. They are building an orchestration job that should run that ingestion job as one step, and then run reporting tasks after it.

Which task type should they use for the ingestion step?""",
a=["A Run Job task that triggers the existing ingestion job",
   "A notebook task that calls `dbutils.notebook.run()` on each ingestion notebook",
   "A For each task that loops over the ingestion job's tasks",
   "An If/else condition task that refers to the ingestion job's ID"],
e="""The Run Job task triggers another job as a step and waits for it to finish. You can pass job parameters to it, and its outcome drives downstream dependencies. This lets you reuse jobs without copying their tasks."""),

dict(d="Debugging & Deploying", q="""In a multi-task job, each of six sequential tasks starts its own new job cluster, and cluster startup accounts for almost half of the job's runtime. How can startup overhead be reduced while still using jobs compute?""",
a=["Configure one shared job cluster and assign all six tasks to it",
   "Change every task to use an all-purpose cluster that stays running",
   "Add a 5-minute retry delay to every task",
   "Split the job into six separate jobs"],
e="""Tasks in a job can share a job cluster defined at the job level, so the cluster starts once and serves several tasks, then terminates when the run ends. Serverless jobs compute removes startup delays too.

All-purpose clusters cost more per DBU and are meant for interactive work."""),

dict(d="Debugging & Deploying", q="""A data engineer edited the source code of a large SDP pipeline and wants to check for problems such as missing tables or invalid references, without updating any tables or processing data. What should they do?""",
a=["Run a validate update of the pipeline",
   "Run a full refresh of all tables",
   "Switch the pipeline to continuous mode",
   "Delete the pipeline's event log, then start a new update"],
e="""A validate update analyzes the pipeline's source code and checks the dataflow graph for errors, such as syntax and analysis problems or missing dependencies, without materializing data. It's a quick, safe check before a real update."""),

dict(d="Debugging & Deploying", q="""A job defines the job-level parameter `env = prod`. One of its notebook tasks also defines a task parameter `env = dev`. What value does `dbutils.widgets.get("env")` return in that task?""",
a=["`prod`, because job parameters are pushed down to all tasks and take precedence over task parameters with the same key",
   "`dev`, because task parameters always override job parameters",
   "An error, because keys can't be duplicated",
   "`prod,dev`, because the values are concatenated"],
e="""Job parameters apply to the whole job and are passed automatically to every task that accepts parameters. If a task parameter has the same key, the job parameter value wins. To control a value per task, give it a different key or use dynamic value references."""),

dict(d="Data Modeling", q="""Bronze order records contain a nested `line_items` array. The silver layer has to support analytics on both orders and line items. Which modeling approach is most common?""",
a=["Create an `orders` silver table, and an `order_line_items` silver table built by exploding the array, with `order_id` as the parent key",
   "Keep the array nested in the orders table, and make every consumer explode it in each query",
   "Turn the array into a comma-separated string column",
   "Create one silver table for each possible array position (`item_1`, `item_2`, and so on)"],
e="""Normalizing one-to-many nested data into a child table keyed by the parent ID gives clean grain for each entity. Joins and aggregations become simple, and line-item queries don't need to explode the array each time.

Fixed position columns and string concatenation don't scale and are hard to query."""),

dict(d="Data Modeling", q="""A retailer needs to analyze inventory on hand for each product and store at the end of each day, and trend it over months. Which type of fact table fits best?""",
a=["A periodic snapshot fact table with one row per product, store, and day",
   "A transactional fact table with one row per inventory movement only",
   "An SCD Type 2 dimension of products",
   "A factless fact table"],
e="""Periodic snapshot facts record the state of measures, such as inventory levels or balances, at regular intervals, which makes trend queries simple.

Transactional facts record individual events, and rebuilding daily levels from them means summing every movement. Factless facts record events that have no measures."""),
]
