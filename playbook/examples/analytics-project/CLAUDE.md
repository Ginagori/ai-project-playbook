# Sales Analytics Dashboard - Development Rules

**Generated:** 2025-01-18
**Last Updated:** 2025-01-18
**Project Type:** Data Analytics & Visualization

---

## 🎯 Project Overview

**Description:** Interactive dashboard for analyzing sales data with KPI tracking, trend analysis, and predictive insights.

**Mission:** Provide business stakeholders with real-time, actionable insights from sales data through intuitive visualizations and automated reporting.

**Target Users:**
- Business analysts (primary)
- Sales managers (secondary)
- C-level executives (reporting consumers)

---

## 1️⃣ Core Principles

### Non-Negotiable Rules

1. **DATA QUALITY IS NON-NEGOTIABLE**
   - All data MUST be validated on ingestion
   - Schema validation with Pandera on every pipeline run
   - No silent failures - fail loud with detailed error messages
   - Data lineage tracked for all transformations

2. **REPRODUCIBILITY FIRST**
   - All analysis code versioned in git
   - Data transformations fully documented
   - Environment fully specified (uv.lock)
   - Random seeds set for any stochastic operations

3. **TYPE SAFETY FOR DATA**
   - Pandas operations with type stubs (pandas-stubs)
   - Pydantic models for all data schemas
   - No `object` dtype without explicit justification
   - Polars preferred over Pandas for new pipelines (better type safety)

4. **PERFORMANCE MATTERS**
   - Query optimization for datasets >100MB
   - Use DuckDB for SQL analytics (faster than Pandas for aggregations)
   - Lazy evaluation where possible (Polars)
   - Cache expensive computations

5. **INSIGHTS OVER CODE**
   - Every visualization must answer a business question
   - No "because we can" charts
   - Clear titles, labels, and interpretations
   - Executive summaries for all reports

6. **FAIL FAST & LOUD**
   - Validate data schemas at pipeline entry points
   - Raise explicit errors with context (which file, which row, what failed)
   - Log all data quality issues
   - Alert on anomalies (unexpected nulls, outliers)

---

## 2️⃣ Tech Stack

### Data Processing
- **Python:** 3.13+
- **Package Manager:** UV (fast, reliable dependency management)
- **DataFrames:**
  - **Polars** 0.20+ (primary - fast, type-safe, lazy evaluation)
  - **Pandas** 2.1+ (legacy compatibility, ecosystem)
- **SQL Analytics:** DuckDB 0.9+ (in-process, blazing fast)
- **Data Validation:** Pandera 0.18+ (schema validation)
- **Type Checking:** Pydantic 2.5+ (data models)

### Visualization & Dashboards
- **Interactive Dashboards:** Streamlit 1.29+ (rapid prototyping, easy deployment)
- **Charts:** Plotly 5.18+ (interactive, professional)
- **Static Reports:** Matplotlib + Seaborn (publication-quality)
- **Tables:** Great Tables (beautiful data tables)

### Notebooks
- **Notebook Engine:** Marimo 0.1+ (reactive, reproducible notebooks)
- **Alternative:** Jupyter Lab 4.0+ (team familiarity)

### Data Sources
- **Database:** PostgreSQL 15+ (production data)
- **File Formats:**
  - Parquet (preferred - compressed, columnar)
  - CSV (legacy imports)
  - Excel (business user exports)

### Testing & Quality
- **Testing:** pytest 7.4+
- **Data Tests:** Great Expectations 0.18+ (data validation suites)
- **Coverage:** pytest-cov
- **Linting:** ruff (fast Python linter)
- **Formatting:** black + isort

### DevOps
- **Containerization:** Docker
- **Orchestration:** Prefect 2.14+ (data pipeline scheduling)
- **Version Control:** Git + DVC (data version control)
- **Deployment:**
  - Streamlit Cloud (dashboards)
  - Railway (backend APIs if needed)

---

## 3️⃣ Architecture

### Architecture Pattern
**Data Pipeline Architecture** (ETL/ELT)

```
┌─────────────────┐
│  Data Sources   │
│  (PostgreSQL,   │
│   CSV, Excel)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   EXTRACT       │  ← scripts/extract/
│  (Raw ingestion)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   TRANSFORM     │  ← scripts/transform/
│  (Clean, enrich)│     (Polars/DuckDB)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     LOAD        │  ← data/processed/
│  (Analytics DB) │     (Parquet files)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ANALYZE       │  ← notebooks/
│  (Notebooks,    │     dashboards/
│   Dashboards)   │
└─────────────────┘
```

### Directory Structure

```
analytics-project/
├── data/
│   ├── raw/              # Original, immutable data
│   │   ├── sales_2024.csv
│   │   └── customers.parquet
│   ├── interim/          # Intermediate transformations
│   │   └── cleaned_sales.parquet
│   └── processed/        # Final, analysis-ready data
│       └── sales_analytics.parquet
├── scripts/
│   ├── extract/          # Data extraction scripts
│   │   ├── extract_postgres.py
│   │   └── extract_csv.py
│   ├── transform/        # Data transformation pipelines
│   │   ├── clean_sales.py
│   │   ├── enrich_customers.py
│   │   └── aggregate_kpis.py
│   └── load/             # Load to analytics DB
│       └── load_duckdb.py
├── notebooks/
│   ├── exploratory/      # Ad-hoc analysis (Marimo)
│   │   └── sales_trends.py
│   └── reports/          # Polished reports for stakeholders
│       └── monthly_sales_report.py
├── dashboards/
│   ├── sales_dashboard.py     # Streamlit app
│   └── components/            # Reusable dashboard components
│       ├── kpi_cards.py
│       └── trend_charts.py
├── src/
│   ├── data/             # Data utilities
│   │   ├── loaders.py
│   │   ├── validators.py
│   │   └── schemas.py    # Pydantic models
│   ├── features/         # Feature engineering
│   │   └── sales_features.py
│   └── viz/              # Visualization utilities
│       └── plotly_themes.py
├── tests/
│   ├── unit/             # Unit tests for functions
│   ├── integration/      # Pipeline integration tests
│   └── data/             # Great Expectations suites
│       └── sales_expectations.py
├── config/
│   ├── database.yaml     # DB connection configs
│   ├── pipeline.yaml     # Pipeline parameters
│   └── viz_theme.yaml    # Chart styling
├── pyproject.toml        # Dependencies (uv)
├── .python-version       # Python version (3.13)
├── Dockerfile
└── README.md
```

---

## 4️⃣ Code Style

### File Naming
- Scripts: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Notebooks: `descriptive_name.py` (Marimo) or `.ipynb`

### Import Organization

```python
# Standard library
import os
from pathlib import Path
from datetime import datetime

# Third-party - data processing
import polars as pl
import duckdb
import pandera as pa

# Third-party - viz
import plotly.express as px
import streamlit as st

# Local
from src.data.loaders import load_sales_data
from src.data.schemas import SalesSchema
```

### Documentation Standards

**Functions:**
```python
def calculate_revenue_growth(
    df: pl.DataFrame,
    period: str = "monthly"
) -> pl.DataFrame:
    """Calculate revenue growth rate over time.

    Args:
        df: Polars DataFrame with columns: date, revenue
        period: Aggregation period ("daily", "weekly", "monthly", "yearly")

    Returns:
        DataFrame with growth_rate column added

    Raises:
        ValueError: If period is not supported
        pa.errors.SchemaError: If df doesn't match expected schema

    Example:
        >>> df = pl.DataFrame({
        ...     "date": ["2024-01-01", "2024-02-01"],
        ...     "revenue": [1000, 1200]
        ... })
        >>> result = calculate_revenue_growth(df, period="monthly")
        >>> assert "growth_rate" in result.columns
    """
    ...
```

**Notebooks:**
Every notebook MUST have:
```python
"""
# Monthly Sales Analysis

**Purpose:** Analyze sales trends for January 2024

**Data Sources:**
- data/raw/sales_jan_2024.csv

**Outputs:**
- Trend charts
- KPI summary table
- Anomaly detection results

**Last Updated:** 2024-01-18
**Author:** [Your name]
"""
```

---

## 5️⃣ Testing

### Testing Philosophy
- **Test data transformations, not just code**
- **Validate schemas at pipeline boundaries**
- **Use real data samples for tests** (anonymized if needed)

### Test Structure

**Unit Tests (pytest):**
```python
# tests/unit/test_transformations.py
import polars as pl
import pytest
from src.transform.clean_sales import remove_duplicates

class TestCleanSales:
    """Tests for sales data cleaning."""

    def test_remove_duplicates(self):
        """Should remove duplicate rows based on sale_id."""
        # Arrange
        df = pl.DataFrame({
            "sale_id": [1, 2, 2, 3],
            "amount": [100, 200, 200, 300]
        })

        # Act
        result = remove_duplicates(df)

        # Assert
        assert result.height == 3  # One duplicate removed
        assert result["sale_id"].to_list() == [1, 2, 3]
```

**Data Validation Tests (Great Expectations):**
```python
# tests/data/sales_expectations.py
import great_expectations as gx

def create_sales_expectations():
    """Define expectations for sales data."""
    suite = gx.core.ExpectationSuite(name="sales_data")

    # Schema validations
    suite.add_expectation(
        gx.expectations.ExpectColumnToExist(column="sale_id")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column="sale_id")
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeUnique(column="sale_id")
    )

    # Business rule validations
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column="amount",
            min_value=0,
            max_value=1_000_000  # Max sale amount
        )
    )
    suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeInSet(
            column="status",
            value_set=["completed", "pending", "cancelled"]
        )
    )

    return suite
```

**Integration Tests (pipeline end-to-end):**
```python
# tests/integration/test_sales_pipeline.py
import pytest
from scripts.transform.clean_sales import run_cleaning_pipeline

@pytest.mark.integration
def test_full_sales_pipeline(tmp_path):
    """Should run full pipeline from raw to processed."""
    # Arrange - create sample raw data
    raw_data = pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "amount": [100, 200]
    })
    raw_path = tmp_path / "raw_sales.csv"
    raw_data.write_csv(raw_path)

    # Act - run pipeline
    output_path = tmp_path / "processed_sales.parquet"
    run_cleaning_pipeline(
        input_path=raw_path,
        output_path=output_path
    )

    # Assert - validate output
    result = pl.read_parquet(output_path)
    assert result.height == 2
    assert "growth_rate" in result.columns  # Added by pipeline
```

### Test Markers

```toml
# pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (full pipelines)",
    "slow: Tests that take >5s",
    "requires_db: Tests requiring database connection",
]
```

**Running tests:**
```bash
# All tests
pytest

# Only fast unit tests
pytest -m unit

# Integration tests (with DB)
pytest -m integration

# With coverage
pytest --cov=src --cov-report=html
```

### Coverage Requirements
- **Minimum:** 75% overall
- **Data transformations:** 90% (critical path)
- **Visualization code:** Exempt (hard to test, low risk)

---

## 6️⃣ Common Patterns

### Data Loading Pattern

```python
# src/data/loaders.py
import polars as pl
from pathlib import Path
from src.data.schemas import SalesSchema

def load_sales_data(file_path: Path, validate: bool = True) -> pl.DataFrame:
    """Load and optionally validate sales data.

    Args:
        file_path: Path to CSV/Parquet file
        validate: If True, validate against SalesSchema

    Returns:
        Polars DataFrame with sales data

    Raises:
        FileNotFoundError: If file doesn't exist
        pa.errors.SchemaError: If validation fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    # Load based on extension
    if file_path.suffix == ".parquet":
        df = pl.read_parquet(file_path)
    elif file_path.suffix == ".csv":
        df = pl.read_csv(file_path, try_parse_dates=True)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

    # Validate schema
    if validate:
        SalesSchema.validate(df)

    return df
```

### Data Transformation Pattern

```python
# scripts/transform/clean_sales.py
import polars as pl
from src.data.loaders import load_sales_data
from src.data.validators import SalesSchema

def clean_sales_data(input_path: Path, output_path: Path) -> None:
    """Clean sales data pipeline.

    Steps:
    1. Load raw data
    2. Remove duplicates
    3. Handle missing values
    4. Validate business rules
    5. Save to parquet

    Args:
        input_path: Path to raw CSV
        output_path: Path to save cleaned parquet
    """
    # 1. Load
    df = load_sales_data(input_path, validate=False)  # Validate after cleaning

    # 2. Clean
    df = (
        df
        # Remove exact duplicates
        .unique()
        # Remove rows with null sale_id
        .filter(pl.col("sale_id").is_not_null())
        # Fill missing amounts with 0
        .with_columns(pl.col("amount").fill_null(0))
        # Filter invalid dates
        .filter(pl.col("date") >= pl.date(2020, 1, 1))
    )

    # 3. Validate business rules
    SalesSchema.validate(df)

    # 4. Save
    df.write_parquet(output_path, compression="snappy")

    # 5. Log summary
    print(f"✅ Cleaned {df.height} sales records")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Total revenue: ${df['amount'].sum():,.2f}")
```

### Schema Validation Pattern

```python
# src/data/schemas.py
import pandera.polars as pa
import polars as pl

class SalesSchema(pa.DataFrameModel):
    """Schema for sales data."""

    sale_id: int = pa.Field(unique=True, nullable=False)
    date: pl.Date = pa.Field(nullable=False)
    customer_id: int = pa.Field(ge=1, nullable=False)
    amount: float = pa.Field(ge=0, le=1_000_000, nullable=False)
    status: str = pa.Field(isin=["completed", "pending", "cancelled"])
    product_category: str = pa.Field(nullable=True)  # Optional

    class Config:
        strict = True  # Reject extra columns
        coerce = True  # Attempt type coercion

# Usage
df = pl.read_csv("sales.csv")
SalesSchema.validate(df)  # Raises error if invalid
```

### Visualization Pattern (Plotly)

```python
# src/viz/sales_charts.py
import plotly.express as px
import polars as pl

def plot_revenue_trend(df: pl.DataFrame) -> px.Figure:
    """Create interactive revenue trend chart.

    Args:
        df: DataFrame with columns: date, revenue

    Returns:
        Plotly figure
    """
    # Aggregate by month
    monthly = (
        df
        .with_columns(pl.col("date").dt.truncate("1mo").alias("month"))
        .group_by("month")
        .agg(pl.col("revenue").sum())
        .sort("month")
    )

    # Create chart
    fig = px.line(
        monthly.to_pandas(),  # Plotly needs pandas
        x="month",
        y="revenue",
        title="Monthly Revenue Trend",
        labels={"revenue": "Revenue ($)", "month": "Month"},
    )

    # Styling
    fig.update_traces(line_color="#3b82f6", line_width=3)
    fig.update_layout(
        hovermode="x unified",
        font_family="Inter",
        title_font_size=20,
    )

    return fig
```

### Dashboard Pattern (Streamlit)

```python
# dashboards/sales_dashboard.py
import streamlit as st
import polars as pl
from src.data.loaders import load_sales_data
from src.viz.sales_charts import plot_revenue_trend

# Page config
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# Sidebar filters
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Date Range", [])

# Load data
@st.cache_data
def load_data():
    return load_sales_data(Path("data/processed/sales_analytics.parquet"))

df = load_data()

# Apply filters
if date_range:
    df = df.filter(pl.col("date").is_between(*date_range))

# KPI Cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${df['revenue'].sum():,.0f}")
with col2:
    st.metric("Total Orders", f"{df.height:,}")
with col3:
    avg_order = df["revenue"].sum() / df.height
    st.metric("Avg Order Value", f"${avg_order:.2f}")

# Charts
st.plotly_chart(plot_revenue_trend(df), use_container_width=True)
```

---

## 7️⃣ Development Commands

### Data Pipeline
```bash
# Extract data from PostgreSQL
uv run scripts/extract/extract_postgres.py --table sales --output data/raw/

# Transform (clean + enrich)
uv run scripts/transform/clean_sales.py --input data/raw/sales.csv --output data/processed/sales.parquet

# Run full pipeline (with Prefect)
uv run prefect deployment run sales-pipeline/daily
```

### Analysis
```bash
# Launch Marimo notebook
marimo edit notebooks/exploratory/sales_trends.py

# Run Streamlit dashboard
streamlit run dashboards/sales_dashboard.py

# Generate static report
uv run notebooks/reports/monthly_sales_report.py
```

### Testing & Quality
```bash
# Linting
ruff check src/ scripts/

# Formatting
black src/ scripts/ tests/

# Type checking
mypy src/

# Unit tests
pytest -m unit

# Integration tests
pytest -m integration

# Data validation (Great Expectations)
great_expectations checkpoint run sales_data_checkpoint

# Full validation pipeline
pytest --cov=src --cov-report=html && ruff check . && mypy src/
```

### Environment
```bash
# Install dependencies
uv sync

# Update dependencies
uv lock --upgrade

# Add new dependency
uv add polars plotly streamlit

# Activate environment (if needed)
source .venv/bin/activate
```

---

## 8️⃣ AI Assistant Instructions

### When Implementing Features

1. **ALWAYS validate data schemas** before and after transformations
2. **Use Polars for new code** (Pandas only for legacy/compatibility)
3. **Write tests BEFORE marking feature as complete**
4. **Optimize for readability over cleverness** (data code is read 10x more than written)
5. **Document business logic** (why this transformation, not just what)

### When Planning Analysis

1. **Start with the question** - What business question are we answering?
2. **Identify data sources** - What tables/files do we need?
3. **Define success criteria** - What output validates the analysis?
4. **Consider edge cases** - Missing data, outliers, date ranges

### When Reviewing Code

1. **Check data validation** - Are schemas enforced?
2. **Verify performance** - Will this work with 10x more data?
3. **Ensure reproducibility** - Can another analyst run this?
4. **Validate business logic** - Do calculations match requirements?

---

## 9️⃣ Project-Specific Notes

### Known Issues / Tech Debt
- Legacy sales data (pre-2020) has inconsistent date formats → manual cleaning required
- Customer table lacks unique constraint on email → duplicates exist
- Excel exports from ERP system sometimes have hidden rows → use `skip_blank_rows=True`

### Data Sources
- **Production DB:** PostgreSQL at `postgres://prod-db:5432/sales`
- **Legacy CSVs:** Stored in `data/raw/legacy/` (2018-2019)
- **External APIs:**
  - Stripe for payment data (API key in .env)
  - HubSpot for customer data (OAuth token in .env)

### Deployment Notes
- Dashboard deployed to Streamlit Cloud: https://sales-dashboard.streamlit.app
- Data pipelines run daily at 6 AM UTC via Prefect Cloud
- PostgreSQL backups stored in S3 bucket: `s3://company-data-backups/sales/`

### Performance Considerations
- Sales table has 5M+ rows → use DuckDB for aggregations (100x faster than Pandas)
- Dashboard queries cached for 1 hour to reduce DB load
- Parquet files compressed with Snappy (good balance of speed/size)

---

**Last Updated:** 2025-01-18
**Maintained By:** Analytics Team
