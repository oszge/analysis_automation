# Sales Intelligence — Analysis Automation

A live business intelligence application for exploring sales performance, comparing periods, and reading validated AI-assisted reports. The dashboard is available online through Streamlit Community Cloud and reads published sales data and reports from an online **Neon PostgreSQL** database.

**[Open the live application](https://analysisautomation.streamlit.app/)**

Use the hosted app directly in your browser without installing Python or configuring database credentials. You can also clone the project and run your own copy locally, including an offline dashboard using CSV data.

The project combines **Streamlit**, **Plotly**, **pandas**, **Neon PostgreSQL**, and an **OpenAI-powered reporting pipeline**. A separate Windows/Node-RED workflow can schedule report generation.

## Choose how to use it

| Mode | Data source | What you need |
| --- | --- | --- |
| Online app | Published sales snapshot and reports in Neon PostgreSQL | A browser and an internet connection |
| Local offline dashboard | Bundled CSV or your own compatible CSV, plus any saved AI output | Python and installed dependencies; select **CSV** in the sidebar |
| Local dashboard with cloud data | Your configured Neon PostgreSQL database | Python, an internet connection, and your own database credentials |

The offline dashboard runs on your computer and opens in your browser. After downloading the repository and installing dependencies, its CSV charts, filters, comparisons, and exports work without a database connection or an OpenAI API key. Generating fresh AI reports requires internet access and an OpenAI API key; the cloud reporting pipeline also requires a database connection.

## What it does

- Explore revenue, units sold, and transaction counts.
- Filter sales by date, country, and category.
- Inspect revenue trends and rankings by category, country, and product.
- Compare the last seven days with the preceding seven days, or month-to-date with the complete previous month.
- Export filtered records as CSV.
- Read an AI executive summary, key insights, risks, and recommendations.
- Publish a matching sales snapshot, validated AI analysis, and Markdown report together in PostgreSQL.

All monetary values are **EUR**. No currency conversion is performed. Transaction counts represent dataset rows.

## Architecture

```text
sales_v2 in PostgreSQL
        |
        v
Python KPI and comparison calculations
        |
        v
AI analysis -> validation -> Markdown report
        |
        v
Atomic dashboard_publication snapshot in Neon
        |
        v
Read-only Streamlit dashboard
```

The dashboard does not call the AI API or import sales into the database. In Neon mode it reads the last successful publication, keeping charts and AI commentary tied to the same data snapshot. Dashboard filters change the charts and tables, but do not generate new AI commentary.

CSV mode is a separate local preview using the bundled `sales_data_v2` file and previously saved AI output. The saved AI output is not guaranteed to describe that CSV or the current filters.

## Run your own copy locally

Use a Python environment compatible with the versions in `requirements-dashboard.txt`.

```bash
git clone https://github.com/oszge/analysis_automation.git
cd analysis_automation
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies while connected to the internet, then start the app:

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open the local address printed by Streamlit, normally `http://localhost:8501`.

**To explore without a database or AI credentials:** select **CSV** in the sidebar. The initial default is Neon PostgreSQL; an unconfigured database may show an error until CSV is selected. The CSV file has no `.csv` extension, but contains CSV data.

For subsequent offline sessions, activate the same environment and run `python -m streamlit run streamlit_app.py`, then select **CSV** again. Keep the local Streamlit process running while you use the dashboard.

To explore your own data, replace the contents of `sales_data_v2` in your local copy with a CSV using the columns listed below. Keep the filename unchanged. Dates must be parseable, quantities must be whole numbers, and quantities and revenue must be finite numeric values with no missing required fields. Revenue is displayed as EUR. Previously saved AI commentary is not regenerated when you change the CSV.

## Dashboard views

| View | Contents |
| --- | --- |
| Overview | Filters, KPIs, daily/weekly/monthly revenue, segment rankings, transactions, CSV export |
| Comparison | Weekly or monthly comparisons, absolute changes, and percentage changes where the baseline is nonzero |
| AI assessment | Previously generated analysis and Markdown report |

Comparisons use the selected end date as their anchor; the start-date filter does not define the comparison windows. A partial current month is compared with the full previous month and is identified in the interface. Percentage changes are undefined when the previous-period value is zero.

Neon publications are checked every 60 seconds while the dashboard session is open. CSV data uses a five-minute cache. **Refresh data** clears the data caches; it does not start a report or AI request.

## Connect your own database (optional)

The public online app already has its cloud database configured. The following settings are only needed when connecting your own local or hosted copy to a database; CSV mode does not require them.

For local use, create an untracked `.env` file in the project directory:

```dotenv
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require
```

For Streamlit Community Cloud, set the root-level secret in the app settings:

```toml
DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
```

The reporting pipeline reads `sales_v2`, whose schema is defined in [`sales.sql`](sales.sql). Load the sales data before running analysis. Required columns are:

| Column | Meaning |
| --- | --- |
| `sale_date` | Sale date |
| `product` | Product name |
| `category` | Product category |
| `country` | Sales country |
| `quantity` | Units sold |
| `revenue` | Revenue in EUR |

The publisher creates/updates `dashboard_publication`; its database role needs the corresponding schema/table permissions. A separate dashboard role can be restricted to reading the published table.

The existing `database.import_sales()` helper contains an author-specific Windows file path and appends records. Adapt it before use and avoid re-importing the same records unintentionally. The dashboard and scheduled report do not perform this import automatically.

## Run the reporting pipeline

The dashboard dependency file does not include the AI client packages. In the same environment, install:

```bash
python -m pip install openai pydantic
```

Add `OPENAI_API_KEY` to your local `.env`, alongside `DATABASE_URL`. The current AI module initializes the client when imported, so a key is needed even when reusing a saved response. The model is configured in `ai_analysis.py`; verify that it is available to your API account before running. AI requests can incur API charges.

Run from the **parent directory** of the `analysis_automation` checkout, because the pipeline uses package-qualified imports:

```bash
cd ..
python -m analysis_automation.data_processing
```

`REFRESH_AI_RESPONSE` in `data_processing.py` controls execution:

- **`True` (current source default):** requests a new AI response, validates it, generates a report, and publishes the matching snapshot to Neon. Local JSON/Markdown outputs are also written.
- **`False`:** reuses `ai_response.json` and validates it against current analysis inputs. It does not publish a new cloud snapshot. A stale response can fail validation.

Validation failures stop the pipeline. A failed database publication does not replace the previous successful publication. Validation is a consistency check, not a guarantee that every AI interpretation is correct; review reports before making business decisions.

## Scheduled execution with Node-RED

The repository includes a Windows-oriented automation setup in [`node_red/`](node_red/). Its intended schedule is daily at **10:00 Europe/Budapest**.

`run_pipeline.py` provides an overlap lock, a 600-second timeout, and JSON run logs in `run_logs/`. It uses the Windows-only `msvcrt` module.

The schedule requires the machine to be awake and the configured Node-RED process to be running. Cloning the repository does not install Node-RED, import the flow, or create a startup shortcut. Review the launch scripts and adapt machine-specific paths before configuring automation. Missed runs are not automatically replayed.

The root README describes the current implementation. Some older notes in `node_red/README.md` refer to earlier defaults; check the current `REFRESH_AI_RESPONSE` flag and the publication behaviour described above.

## Deploy your own online version

The existing application is available at **[analysisautomation.streamlit.app](https://analysisautomation.streamlit.app/)**. To host your own copy, use the configuration below.

For an existing Streamlit Community Cloud account, select this repository, the `main` branch, and `streamlit_app.py` as the entry point. `requirements.txt` includes the dashboard dependencies. Add `DATABASE_URL` in the app's secrets settings to use Neon.

The hosted dashboard requires a successful publication to exist in Neon mode. Hosting the dashboard does not host the Windows scheduler or generate reports; those run separately. The dashboard itself does not need an OpenAI API key.

## Project structure

| File | Purpose |
| --- | --- |
| `streamlit_app.py` | Dashboard interface and publication refresh |
| `dashboard_data.py` | Data loading, preparation, and comparisons |
| `dashboard_style.py` | Styling and Plotly charts |
| `data_processing.py` | KPI calculations and report orchestration |
| `ai_analysis.py` | Structured AI response schema and API request |
| `validation.py` | AI output consistency checks |
| `report_generator.py` | Markdown report generation |
| `published_report.py` | Atomic database publication and read access |
| `database.py` / `sales.sql` | Database access and sales schema |
| `run_pipeline.py` / `node_red/` | Windows automation wrapper and supporting setup |
| `sales_data_v2` | Bundled CSV preview data |

## Credentials and data

Keep `.env`, API keys, database passwords, and populated secrets files out of version control. Use a read-only database role for the public dashboard where possible. Publish only sales data and reports that are intended to be visible to visitors.

Built by [Ősz Gergő](https://github.com/oszge).
