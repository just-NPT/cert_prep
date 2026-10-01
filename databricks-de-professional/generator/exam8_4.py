Q = [
dict(d="Security & Compliance", q="""For a regulatory investigation, the security team must be able to see the exact commands users run in notebooks. What should be enabled?""",
a=["Verbose audit logs, which record notebook and SQL command execution events in the audit logs",
   "Change Data Feed on every table",
   "Cluster log delivery for every cluster",
   "Query result caching on SQL warehouses"],
e="""Verbose audit logs add events for commands run in notebooks and other interactive sessions to the standard audit logs, which you can query in `system.access.audit`.

Cluster logs hold driver and executor output, not a structured audit trail. CDF records changes to data."""),

dict(d="Security & Compliance", q="""Regulations require that EU customer data is stored and processed only in the EU. Analysts in the US must use aggregated, non-personal results only. Which architecture meets this?""",
a=["Keep the personal data in an EU-region workspace with an EU metastore and EU storage, and share only aggregated tables (for example, through Delta Sharing) with the US region",
   "Store the EU data in a US metastore and mask its columns for US users",
   "Copy the raw EU data to the US every night with deep clone, and restrict who can access it",
   "Use Lakehouse Federation from the US workspace to query the raw EU tables directly"],
e="""Unity Catalog metastores, workspaces, and storage belong to a region. Data residency requires that personal data stays on EU resources, and only non-personal, aggregated outputs cross borders. Sharing aggregated tables does that.

Cloning or querying the raw data from the US moves or processes personal data outside the EU."""),

dict(d="Data Governance", q="""An auditor asks for the current privileges on the table `finance.core.ledger`, including the principal and privilege for each grant. Which command lists them?""",
a=["`SHOW GRANTS ON TABLE finance.core.ledger;`",
   "`DESCRIBE HISTORY finance.core.ledger;`",
   "`DESCRIBE DETAIL finance.core.ledger;`",
   "`SHOW TBLPROPERTIES finance.core.ledger;`"],
e="""`SHOW GRANTS ON <securable>` lists the privileges granted on an object. You can also add `TO <principal>` to see a single principal's grants. The `information_schema` privilege views give the same information in SQL tables.

The other commands show write history, file details, or table properties."""),

dict(d="Data Governance", q="""Which statement about Unity Catalog data lineage is correct?""",
a=["Lineage is captured automatically at the table and column level for queries run on Databricks, and Catalog Explorer shows the upstream and downstream tables along with the notebooks, jobs, pipelines, and dashboards involved.",
   "Lineage has to be declared by hand with `ALTER TABLE ... SET LINEAGE` for each table.",
   "Lineage is only captured for SDP pipelines, not for notebooks or jobs.",
   "Lineage is stored in each table's `_delta_log` and can only be read with `DESCRIBE HISTORY`."],
e="""Unity Catalog records lineage at runtime, down to column level, across languages and compute types. It is shown in Catalog Explorer and exposed in `system.access.table_lineage` and `system.access.column_lineage`, including which notebooks, jobs, and dashboards read or wrote each table. No manual declaration is needed."""),

dict(d="Data Governance", k=2, q="""A team is choosing between Unity Catalog managed tables and external tables for new data. Which two benefits apply to managed tables? Choose 2 answers:""",
a=["They are eligible for predictive optimization, which handles maintenance such as `OPTIMIZE`, `VACUUM`, and statistics automatically",
   "Unity Catalog manages the storage location and the data's lifecycle, including recovering dropped tables with `UNDROP` during the retention period",
   "Other engines can write directly to their storage path without going through Unity Catalog",
   "Dropping a managed table never deletes the underlying data files",
   "They can only be stored in DBFS root"],
e="""Managed tables give Unity Catalog full control over storage and lifecycle. That enables features like predictive optimization and automatic liquid clustering, and dropped tables can be recovered within the retention window.

Direct writes by other engines and data that survives a drop are properties of external tables. Managed storage lives in cloud storage configured at the metastore, catalog, or schema level, not DBFS root."""),

dict(d="Data Governance", q="""A group was granted `SELECT` on the schema `sales.core`. An admin wants this group to lose access to one table in that schema and runs:

```
REVOKE SELECT ON TABLE sales.core.payroll FROM `analysts`;
```

The analysts can still read `payroll`. Why?""",
a=["The privilege is inherited from the schema-level grant. Revoking at table level only removes direct grants, and Unity Catalog has no DENY, so the schema grant must be narrowed or the table moved.",
   "`REVOKE` takes effect only after the metastore restarts.",
   "Revoked privileges only apply to new sessions started after 24 hours.",
   "The analysts own the table."],
e="""Unity Catalog privileges are inherited downward: a `SELECT` on a schema covers every current and future table in it. There's no explicit DENY. To exclude one table, grant at table level instead of schema level, or move the sensitive table to a schema the group can't access."""),

dict(d="Data Governance", q="""A business unit's managed tables must be stored in its own dedicated cloud storage bucket, separate from the metastore's default storage, for chargeback and isolation. What should the admin configure?""",
a=["A managed storage location on the business unit's catalog, for example `CREATE CATALOG bu_finance MANAGED LOCATION 's3://bu-finance-bucket/managed'`, backed by an external location",
   "An external table `LOCATION` on every table, set by hand",
   "A separate metastore for each business unit in the same region",
   "A DBFS mount for the business unit's bucket"],
e="""You can set managed storage at the catalog or schema level, which overrides the metastore default. Every managed table created in that catalog is then stored in the dedicated bucket while still being a managed table. The location must be covered by an external location.

Only one metastore is allowed per region."""),

dict(d="Debugging & Deploying", q="""Interactive and job clusters take several minutes to start, mostly because of cloud instance provisioning. Classic compute must still be used. Which feature reduces startup time?""",
a=["Instance pools, which keep idle, ready-to-use instances that clusters can take when they start",
   "Cluster policies that limit the maximum number of workers",
   "Init scripts that pre-install libraries",
   "Turning off autoscaling"],
e="""Pools keep a set of idle instances, optionally with a preloaded Databricks Runtime, so clusters that use the pool skip most of the provisioning time. Idle pool instances don't incur DBU charges, only cloud costs.

Serverless compute avoids the wait altogether."""),

dict(d="Debugging & Deploying", q="""After `databricks bundle deploy -t staging`, the CI pipeline must trigger the bundle's job `nightly_etl` in staging and wait for the result. Which command should it run?""",
a=["`databricks bundle run -t staging nightly_etl`",
   "`databricks bundle deploy -t staging --run nightly_etl`",
   "`databricks jobs create nightly_etl -t staging`",
   "`databricks bundle validate -t staging nightly_etl`"],
e="""`bundle run <resource-key>` triggers a deployed job or pipeline in the chosen target, using the bundle's resource key instead of a numeric ID. By default it waits for the run to finish and reports the result, which suits CI integration tests."""),

dict(d="Debugging & Deploying", q="""A bundle's `databricks.yml` has grown to thousands of lines. The team wants each job and pipeline defined in its own YAML file under `resources/`. How is this supported?""",
a=["Add an `include` mapping to `databricks.yml` (for example, `include: [\"resources/*.yml\"]`) so the files are merged into the bundle configuration",
   "Run `databricks bundle deploy` once for each YAML file",
   "Name the files `databricks1.yml`, `databricks2.yml`, and so on, which are picked up automatically",
   "Put each file's contents into a separate target"],
e="""The top-level `include` key takes paths or globs to more configuration files. They are merged with `databricks.yml` into one bundle, which keeps large projects modular. The `bundle init` templates use this layout by default."""),

dict(d="Debugging & Deploying", q="""In a bundle, the `prod` target must deploy jobs that run as the service principal `sp-prod-etl`, while development deployments run as the developer. How should this be configured?""",
a=["""targets:
  prod:
    mode: production
    run_as:
      service_principal_name: "sp-prod-etl\"""",
   """targets:
  prod:
    mode: development
    owner: "sp-prod-etl\"""",
   """variables:
  run_as: "sp-prod-etl\"""",
   """resources:
  jobs:
    etl:
      user: "sp-prod-etl\""""],
e="""The `run_as` mapping, set at the top level or per target, decides which identity deployed jobs and pipelines run as. Setting it on the production target keeps production runs under a service principal, while development targets default to the deploying user. Production mode also checks that deployments are set up safely."""),

dict(d="Debugging & Deploying", q="""Two jobs run MERGE statements at the same time on the same Delta table, each for a different region. One of them sometimes fails with `ConcurrentAppendException`. What is a recommended fix?""",
a=["Make each MERGE's condition explicitly limited to its own region (for example, `ON t.id = s.id AND t.region = 'EU'`) so the operations touch disjoint data, and/or use row-level concurrency with deletion vectors and liquid clustering",
   "Run `VACUUM` between the two jobs",
   "Turn off the Delta transaction log on the table",
   "Increase the cluster size of both jobs"],
e="""Delta uses optimistic concurrency. A conflict happens when a transaction might have read data that another transaction changed at the same time. Explicit predicates that limit each operation to disjoint partitions or clusters, plus row-level concurrency (available with deletion vectors and liquid clustering), reduce conflicts.

Bigger clusters and VACUUM don't change how conflicts are detected."""),

dict(d="Data Modeling", q="""A team needs surrogate keys for a dimension built by several independent pipelines. The same business key must always get the same surrogate key, without a central sequence. Which approach fits?""",
a=["Derive the key deterministically from the business key, for example `xxhash64(source_system, customer_id)` or a `sha2` hash",
   "Use `monotonically_increasing_id()` in each pipeline",
   "Use an identity column, written to by all pipelines at the same time",
   "Use `uuid()` for each row"],
e="""A hash-based key is deterministic: the same input always gives the same key, in any pipeline, with no coordination. Use a wide enough hash to keep collisions unlikely.

`monotonically_increasing_id()` and `uuid()` give different values on each run, and identity columns don't support concurrent writers."""),

dict(d="Data Modeling", q="""A retailer is designing a sales fact table. Analysts need to analyze discounts at the level of individual products, and also report totals per order and per day. What grain should the fact table have?""",
a=["One row per order line item (product within an order), the lowest level of detail, from which order and daily totals can be aggregated",
   "One row per day per store",
   "One row per order, with product details stored in an array",
   "One row per customer per month"],
e="""A fact table's grain should be the most atomic level the business needs. Detailed facts can always be rolled up to orders, days, or stores, but aggregated facts can't be broken back down to products. Aggregated gold tables or materialized views can sit on top for performance."""),
]
