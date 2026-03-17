📚 Gravity Books ETL Pipeline 📊
A robust ETL (Extract, Transform, Load) pipeline that transfers book sales data from an operational database (Gravity_Books) to a dimensional data warehouse (GravityBooks_DWH) following star schema principles. The pipeline automates the cleansing and loading of dimension tables and fact tables for business intelligence and analytics.

📌 Table of Contents
🔎 Project Overview

🚧 Current Technical & Budget Constraints

🚀 Final Goals

🏁 Competitors

❗Key Technical Challenges & Roadblocks

💡 Proposed Solutions

📈 System Architecture

🔧 Features

🧪 Pipeline Phases

🧬 Data Flow Diagram

🗂 Directory Structure

📦 Tech Stack

🗓 Roadmap

🧾 License

👨‍💻 Author

📬 Future Improvements

🙋‍♂️ Contributing

📞 Contact

🔎 Project Overview
Gravity Books ETL Pipeline is an automated data integration solution that extracts book sales data from a transactional database and loads it into a dimensional data warehouse optimized for analytical queries. The pipeline implements a classic star schema with dimension tables (books, customers, date) and a central fact table (sales).

This enables:

⚙️ Automated daily data warehouse refreshes

📊 Business intelligence and reporting capabilities

🔍 Historical sales analysis by book, customer, and time dimensions

🧮 Fast analytical queries on large datasets

📈 Data-driven decision making for inventory and sales strategies

🚧 Current Technical & Budget Constraints
This project processes book sales data from the Gravity_Books operational database, transforming it into an analytics-ready star schema in GravityBooks_DWH. The current implementation runs as a batch ETL process with the following constraints:

Single-threaded execution: The pipeline processes data sequentially without parallelization

No incremental loading: Currently performs full refresh (TRUNCATE/LOAD) instead of incremental updates

Limited error handling: Basic try-catch without granular retry logic for failed records

No data quality validation: Missing data quality checks before and after loading

No orchestration: Manual execution required, no scheduling capabilities

Local execution only: Not containerized or deployed to cloud environments

Budget constraints currently prevent investment in:

Enterprise ETL tools (Informatica, SSIS, Talend)

Cloud data warehousing solutions (Snowflake, Redshift, BigQuery)

Real-time streaming platforms

Commercial data quality and observability tools

🚀 Final Goals
✅ Automated pipeline: From source extraction to warehouse loading

✅ Star schema design: Properly modeled dimension and fact tables

✅ Data cleaning: Remove duplicates and handle missing values

✅ Date dimension population: Comprehensive date attributes for time-based analysis

✅ Fast execution: Optimized bulk insert operations

✅ Referential integrity: Maintain foreign key relationships between facts and dimensions

✅ Fully documented: Complete with schema diagrams, data lineage, and operational procedures

✅ CI/CD ready: Version-controlled with automated testing

🏁 Competitors
Several ETL and data integration tools and platforms offer similar data warehousing capabilities. Notable competitors include:

Microsoft SSIS : Enterprise-grade ETL tool with visual design interface but requires significant licensing costs and Windows infrastructure.

Talend Open Studio : Open-source ETL tool with extensive connector library but steeper learning curve and Java dependency.

Apache Airflow : Workflow orchestration platform with Python-based DAGs but requires more complex setup and infrastructure management.

dbt (data build tool) : Modern transformation tool focused on SQL-based modeling but doesn't handle extraction and loading natively.

Prefect : Modern workflow orchestration with Python-native approach similar to this project's future direction.

❗Key Technical Challenges & Roadblocks
This project faces several challenges that impact performance, reliability, and scalability:

Data Consistency: Source data may contain orphaned records or referential integrity violations that break fact table loading.

Performance Bottlenecks: The current single-threaded approach becomes slow with large volumes (millions of rows).

Type 1 Dimension Overwrites: Current implementation overwrites dimension attributes without maintaining history.

No SCD Handling: Slowly Changing Dimensions (Type 2) not implemented for tracking historical changes.

Limited Error Recovery: Failed executions require manual intervention and full restart.

No Data Validation: Missing pre-load validation for data quality and completeness.

Hardcoded Connections: Database connection parameters are hardcoded in the script, creating security and maintenance issues.

No Incremental Logic: Full refresh approach doesn't scale as data volumes grow over time.

Limited Date Dimension: Current date dimension lacks business-specific attributes (holidays, fiscal periods).

No Monitoring: Absence of logging and alerting mechanisms for production operations.

💡 Proposed Solutions
Implement Incremental Loading: Add change data capture (CDC) logic using timestamps or audit columns to load only new/changed records.

Parallel Processing: Use Python's multiprocessing or async capabilities for parallel data extraction and loading.

Add SCD Type 2 Support: Track historical changes in dimension attributes with effective dates and current flag.

Enhance Error Handling: Implement granular retry logic and dead letter queues for failed records.

Add Data Quality Framework: Implement pre-load validation checks and post-load reconciliation.

Externalize Configuration: Move connection strings and parameters to environment variables or config files.

Enrich Date Dimension: Add fiscal periods, holidays, and business-specific date attributes.

Implement Logging: Add structured logging with log levels and optional log aggregation.

Containerize Application: Package ETL process in Docker for consistent execution environments.

Orchestrate with Prefect: Replace manual execution with scheduled, monitored workflows.

📈 System Architecture
text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Source DB     │────▶│   ETL Pipeline  │────▶│  Target DW      │
│  Gravity_Books  │     │   (Python)      │     │ GravityBooks_DWH│
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌──────────┐
              │Dim_Books │ │Dim_Custom│ │Dim_Date  │
              └──────────┘ └──────────┘ └──────────┘
                    │            │            │
                    └────────────┼────────────┘
                                 ▼
                         ┌──────────────┐
                         │  Fact_Sales  │
                         └──────────────┘
🔧 Features
✅ Automated dimension table population (Books, Customers)

✅ Comprehensive date dimension with 30+ years of data

✅ Fact table loading with referential integrity

✅ Bulk insert optimization with fast_executemany

✅ Data cleaning and transformation

✅ Transaction management with commit/rollback

✅ Source-to-target data lineage

✅ Primary key-foreign key relationship maintenance

✅ Configurable via environment variables

✅ Error handling and basic logging

🧪 Pipeline Phases
<details> <summary>✅ Phase 1: Database Connections</summary>
🔁 Inputs:

Source database connection string

Destination database connection string

ODBC driver configuration

⚙️ Inside:

Establish connections to both databases

Configure fast_executemany for performance

Set up cursor for destination operations

🎯 Purpose:
Create secure, performant connections to source and target databases.

🔁 Used again in:
All subsequent phases

📤 Outputs:
Active database connections and cursors

</details><details> <summary>✅ Phase 2: Data Cleanup</summary>
🔁 Inputs:

Destination database connection

Table names (Fact_Sales, Dim_Books, Dim_Customers)

⚙️ Inside:

Execute DELETE statements in correct order (facts first, then dimensions)

Commit transaction after successful deletion

Handle foreign key constraints by maintaining deletion order

🎯 Purpose:
Clean existing data to prevent duplicates and maintain referential integrity before fresh load.

🔁 Used again in:
Phase 3, 4, 5 (load operations)

📤 Outputs:
Empty dimension and fact tables ready for loading

</details><details> <summary>✅ Phase 3: Dim_Books Population</summary>
🔁 Inputs:

Source database connection

SQL query joining book, language, and publisher tables

⚙️ Inside:

Execute query and load results into pandas DataFrame

Transform data as needed

Bulk insert using executemany with fast_executemany

🎯 Purpose:
Populate book dimension with denormalized attributes (title, language, publisher).

🔁 Used again in:
Phase 5 (Fact_Sales loading for BookKey lookup)

📤 Outputs:
/logs/dim_books_load_summary.txt

</details><details> <summary>✅ Phase 4: Dim_Customers Population</summary>
🔁 Inputs:

Source database connection

SQL query extracting customer data

Default values for City and Country

⚙️ Inside:

Extract customer data with full name concatenation

Add default values for missing attributes (City, Country)

Bulk insert transformed customer records

🎯 Purpose:
Create customer dimension with consistent formatting and default values for missing data.

🔁 Used again in:
Phase 5 (Fact_Sales loading for CustomerKey lookup)

📤 Outputs:
/logs/dim_customers_load_summary.txt

</details><details> <summary>✅ Phase 5: Dim_Date Population</summary>
🔁 Inputs:

Start date (2000-01-01)

End date (2030-12-31)

pandas date_range function

⚙️ Inside:

Generate continuous date range

Create DateKey (YYYYMMDD integer format)

Extract year, month, day components

Check if table already populated (avoid duplicates)

Bulk insert if empty

🎯 Purpose:
Populate date dimension for time-based analysis with consistent date keys.

🔁 Used again in:
Phase 6 (Fact_Sales loading for OrderDateKey lookup)

📤 Outputs:
Complete date dimension with 30+ years of dates

</details><details> <summary>✅ Phase 6: Fact_Sales Population</summary>
🔁 Inputs:

Source database (cust_order, order_line tables)

Dimension tables (Dim_Books, Dim_Customers)

Date formatting logic

⚙️ Inside:

Join source order data with dimension tables

Convert order_date to DateKey integer format

Insert fact records with foreign keys to all dimensions

Commit transaction on success

🎯 Purpose:
Populate fact table with measurable sales data linked to all dimensions.

🔁 Used again in:
Reporting and analytics tools

📤 Outputs:
/logs/fact_sales_load_summary.txt

</details>
🧬 Data Flow Diagram
text
┌─────────────────────────────────────────────────────────────────┐
│                        SOURCE DATABASE                           │
│                        Gravity_Books                             │
├───────────────┬──────────────────┬─────────────────────────────┤
│    book       │    customer      │    cust_order                │
│  book_id      │  customer_id     │  order_id                    │
│  title        │  first_name      │  customer_id                 │
│  language_id  │  last_name       │  order_date                  │
│  publisher_id │                  │                              │
├───────────────┼──────────────────┼─────────────────────────────┤
│ book_language │    publisher      │    order_line                │
│ language_id   │  publisher_id     │  order_id                    │
│ language_name │  publisher_name   │  book_id                     │
│               │                   │  price                       │
└───────────────┴──────────────────┴─────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ETL PIPELINE                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Extract     │─▶│ Transform   │─▶│ Load                    │ │
│  │ pandas      │  │ Date format │  │ fast_executemany        │ │
│  │ read_sql    │  │ Name concat │  │ Bulk insert             │ │
│  └─────────────┘  │ Defaults    │  └─────────────────────────┘ │
│                   └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA WAREHOUSE                              │
│                      GravityBooks_DWH                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  FACT TABLE                              │   │
│  │              Fact_Sales                                  │   │
│  │  SalesKey (PK) │ BookKey (FK) │ CustomerKey (FK)        │   │
│  │  OrderDateKey (FK) │ Price                               │   │
│  └───────────────┬────────────────┬────────────────────────┘   │
│                  │                │                             │
│                  ▼                ▼                             │
│  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │   Dim_Books          │  │   Dim_Customers      │            │
│  │   BookKey (PK)       │  │   CustomerKey (PK)   │            │
│  │   BookID             │  │   CustomerID         │            │
│  │   Title              │  │   Full_Name          │            │
│  │   Language_Name      │  │   City               │            │
│  │   Publisher_Name     │  │   Country            │            │
│  └──────────────────────┘  └──────────────────────┘            │
│                  ▲                                              │
│                  │                                              │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                 Dim_Date                              │      │
│  │                 DateKey (PK)                          │      │
│  │                 FullDate │ Year │ Month │ Day         │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
🗂 Directory Structure
text
gravity_books_etl/
├── .github/                          # GitHub configuration
│   └── workflows/
│       └── etl_pipeline.yml          # Scheduled ETL workflow

├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Container configuration
├── docker-compose.yml                  # Multi-service orchestration
├── .env                               # Environment variables
├── .gitignore                          # Git ignore rules

├── etl_pipeline.py                     # Main ETL script
├── config/
│   ├── __init__.py
│   ├── settings.py                     # Central configuration
│   └── database.py                      # Connection management

├── scripts/
│   ├── run_etl_local.py                 # Local execution script
│   ├── validate_data.py                  # Data validation utilities
│   └── generate_date_dimension.py        # Standalone date generator

├── logs/
│   └── etl_YYYYMMDD.log                  # Execution logs

├── notebooks/
│   ├── data_profiling.ipynb              # Source data analysis
│   ├── dim_design_validation.ipynb       # Dimension validation
│   └── sample_queries.ipynb               # Example analytical queries

├── sql/
│   ├── schema/
│   │   ├── create_dim_books.sql
│   │   ├── create_dim_customers.sql
│   │   ├── create_dim_date.sql
│   │   └── create_fact_sales.sql
│   ├── queries/
│   │   ├── source_extract.sql
│   │   ├── sample_reports.sql
│   │   └── data_validation.sql
│   └── indexes/
│       └── create_indexes.sql

├── python_scripts/
│   ├── __init__.py
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── books_extractor.py
│   │   ├── customers_extractor.py
│   │   └── sales_extractor.py
│   ├── transformer/
│   │   ├── __init__.py
│   │   ├── date_transformer.py
│   │   ├── name_transformer.py
│   │   └── data_cleaner.py
│   └── loader/
│       ├── __init__.py
│       ├── dim_loader.py
│       ├── fact_loader.py
│       └── bulk_inserter.py

├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_extractors.py
│   │   ├── test_transformers.py
│   │   └── test_loaders.py
│   ├── integration/
│   │   └── test_end_to_end.py
│   └── test_data/
│       ├── sample_books.csv
│       ├── sample_customers.csv
│       └── expected_results.json

├── extra_scripts/
│   ├── data_migration_validator.py
│   ├── index_rebuild.py
│   └── statistics_update.py

└── docs/
    ├── architecture_diagram.png
    ├── data_lineage.md
    ├── etl_process_flow.md
    ├── star_schema_design.md
    ├── deployment_guide.md
    └── sample_analytics_queries.md
📦 Tech Stack
Category	Tool / Library
Database	Microsoft SQL Server
ODBC Driver	ODBC Driver 17 for SQL Server
ETL Framework	Python 3.10+
Data Manipulation	pandas
Database Connectivity	pyodbc
Bulk Insert	fast_executemany
Workflow Orchestration	Prefect (Future)
Containerization	Docker
CI/CD	GitHub Actions
Testing	pytest
Version Control	Git
Documentation	Markdown, Mermaid
🗓 Roadmap
Phase	Description	Start Date	End Date	Status
✅ 1	Database Connections & Schema Setup	2025-08-01	2025-08-02	✅ Done
✅ 2	Dim_Books ETL Implementation	2025-08-03	2025-08-04	✅ Done
✅ 3	Dim_Customers ETL Implementation	2025-08-04	2025-08-05	✅ Done
✅ 4	Dim_Date Population	2025-08-05	2025-08-05	✅ Done
✅ 5	Fact_Sales ETL Implementation	2025-08-06	2025-08-07	✅ Done
🔄 6	Incremental Loading Logic	2025-08-15	TBD	🔄 Planned
🔄 7	SCD Type 2 Implementation	TBD	TBD	🔄 Planned
🔄 8	Error Handling & Logging Enhancement	TBD	TBD	🔄 Planned
🔄 9	Data Quality Framework	TBD	TBD	🔄 Planned
🔄 10	Prefect Orchestration	TBD	TBD	🔄 Planned
🔄 11	Docker Containerization	TBD	TBD	🔄 Planned
🔄 12	CI/CD with GitHub Actions	TBD	TBD	🔄 Planned
🔄 13	Monitoring & Alerting	TBD	TBD	🔄 Planned
🔄 14	Performance Optimization	TBD	TBD	🔄 Planned
🔄 15	Documentation Completion	2025-08-07	Ongoing	🔄 In Progress
🧾 License
No license has been selected for this project yet.
All rights reserved — you may not use, copy, modify, or distribute this code without explicit permission from the author.

👨‍💻 Author
Omar Erfan
Data Engineer • ETL Specialist • SQL Server Expert • BI Enthusiast

🌐 GitHub | LinkedIn

📬 Future Improvements
Incremental ETL Implementation

Add watermark tables for change data capture

Implement merge statements for upsert operations

Reduce load times by 70% for large datasets

SCD Type 2 Support

Track historical changes in customer and book attributes

Add effective date and current flag columns

Enable point-in-time historical analysis

Data Quality Framework

Pre-load validation rules for source data

Post-load reconciliation counts

Automated data quality dashboard

Orchestration & Scheduling

Implement Prefect workflows with retry logic

Add Slack/email notifications

Create dependency management between tasks

Performance Optimization

Implement parallel processing for large tables

Add indexing strategies post-load

Optimize batch sizes for bulk operations

Monitoring & Observability

Real-time ETL dashboard with Grafana

Prometheus metrics for job duration and row counts

Automated anomaly detection

Security Enhancements

Move connection strings to Azure Key Vault

Implement row-level security for multi-tenant support

Add audit logging for data access

Cloud Deployment

Migrate to Azure SQL Database

Implement Azure Data Factory for managed orchestration

Add disaster recovery with geo-replication

🙋‍♂️ Contributing
Contributions are welcome! Please open an issue first to discuss any proposed changes.
Areas where help is especially needed:

Performance optimization techniques

Additional date dimension attributes

Data validation rules

Documentation improvements

Test coverage expansion

📞 Contact
For questions, support, or collaboration opportunities, please reach out to:

Omar Erfan
📧 Email: omarerfan871@gmail.com
🐙 GitHub: omarerfan21
💼 LinkedIn: Omar Erfan