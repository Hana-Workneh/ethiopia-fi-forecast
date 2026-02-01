# Forecasting Financial Inclusion in Ethiopia 🇪🇹

This project builds a forecasting system to track Ethiopia’s digital financial transformation using time-series modeling and event-based interventions.

The system focuses on the two core Global Findex dimensions of financial inclusion:

- **Access** → Account Ownership Rate  
- **Usage** → Digital Payment Adoption Rate  

The work is developed as part of the Selam Analytics Financial Inclusion Forecasting Challenge.

---

## Project Objectives

The consortium (development finance institutions, mobile money operators, and the National Bank of Ethiopia) seeks to understand:

- What drives financial inclusion in Ethiopia?
- How do events (policy reforms, product launches, infrastructure investments) affect inclusion outcomes?
- How will inclusion evolve in **2025–2027**?

---

## Repository Structure

```bash
ethiopia-fi-forecast/
│
├── data/
│   ├── raw/                # Starter datasets
│   └── processed/          # Enriched analysis-ready datasets
│
├── notebooks/
│   ├── 01_task1_data_exploration.ipynb
│   └── 02_task2_eda.ipynb
│
├── reports/
│   └── data_enrichment_log.md
│
├── dashboard/              # Streamlit dashboard (Task 5)
├── models/                 # Forecasting models (Task 4)
└── README.md
```
## How to Run
## Setup environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

## Run notebooks
jupyter notebook

## Data Sources

World Bank Global Findex Database

National Bank of Ethiopia publications

Operator reports (Telebirr, M-Pesa)

Infrastructure proxies (internet penetration, electricity access)

## Next Steps

Upcoming tasks include:

Event impact modeling (Task 3)

Forecasting inclusion outcomes for 2025–2027 (Task 4)

Interactive dashboard development (Task 5)