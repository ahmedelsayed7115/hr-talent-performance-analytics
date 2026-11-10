# Enterprise HR Performance & Talent Intelligence Suite

[![Power BI](https://img.shields.io/badge/Power_BI-Desktop_2026-F2C811?logo=powerbi&logoColor=black)](HR_Executive_Dashboard.pbix)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](performance_analytics.py)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3%2B-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Executive_Ready-success)]()

An executive-grade **People Analytics, Compensation Equity & Predictive Retention Intelligence** system combining an automated Python machine learning pipeline with an interactive 3-page Power BI dashboard.

Designed to diagnose enterprise attrition drivers, audit pay-for-performance meritocracy, calculate the true financial drain of regrettable talent turnover using SHRM replacement modeling, and proactively triage flight risks before resignations occur.

---

## 📊 Core Deliverables & Repository Structure

```
├── HR_Executive_Dashboard.pbix       # Production Power BI Dashboard (3-page HD interactive app)
├── performance_analytics.py         # Complete Python ML & Analytics pipeline
├── enriched_hr_performance_data.csv # Enriched dataset (1,470 records with engineered features)
└── README.md                        # Portfolio documentation & executive summary
```

| Deliverable | Description |
| :--- | :--- |
| **Power BI Dashboard** (`HR_Executive_Dashboard.pbix`) | 3-page interactive `1920×1080` executive report with left-sidebar app rail (`01`, `02`, `03`), hover-glow KPI cards, burnout quadrant, and AI Decomposition Tree. |
| **Python ML Pipeline** (`performance_analytics.py`) | Feature engineering (`CompaRatio`, `BurnoutIndex`, SHRM replacement cost), 5-fold out-of-fold flight-risk scoring (`RandomForestClassifier` + `LogisticRegression` baseline), and 9-Box Talent Matrix. |
| **Enriched Dataset** (`enriched_hr_performance_data.csv`) | The clean enterprise dataset with all engineered features, risk scores, and compensation bands. |
| **Executive Documentation** (`README.md`) | Complete business findings, DAX measures overview, methodology, and instructions for reproducing. |

---

## 🎯 Headline Executive Findings

| Strategic Metric | Value | Diagnostic Assessment |
| :--- | :---: | :--- |
| **Total Workforce** | **1,470** (`1,233` Active) | 83.9% active retention across R&D, Sales, and HR |
| **Enterprise Turnover Rate** | **16.12%** (`237` exits) | Outpaces tech/life-sciences industry benchmarks (10%–12%) |
| **Total Replacement Cost Drain** | **\$12,327,384** | Cumulative SHRM-modeled replacement cost (\$52,014 average per exit) |
| **Regrettable Turnover Share** | **52.40%** (\$6.46M) | Over half of financial loss stems from the 36.71% (87 exits) of key/top talent |
| **Top-Performer Base Pay Lag** | **-\$188.50 / mo** | Rating 4 median (\$4,777) lags Rating 3 (\$4,966) due to earlier-tenure band entry |
| **Within-Band Compa-Ratio Parity** | **1.01** vs. **1.03** | **Zero Merit Premium:** Top performers sit at peer median despite +7.85% higher hikes |
| **Top Talent Retention Advantage** | **-0.29%** (`-0.3%`) | Rating 4 attrition (**16.37%**) is identical to/slightly exceeds Rating 3 (**16.08%**) |
| **Underpaid Top Talent (`<0.85` CR)**| **30 Personnel** | Paid **25.5% below role median** (`0.745` avg CR); **\$1,577,340** replacement risk |
| **Recalibration Budget Required** | **\$400,968 / yr** | **3.93× Direct ROI** in avoided turnover replacement exposure |
| **Active Rating 4 Flight Exposure** | **\$684,780** | 15 active top performers in Critical/Moderate flight-risk quadrants |
| **Predictive Model Discrimination** | **0.814 ROC-AUC** | 5-fold out-of-fold cross-validated Random Forest (0.837 Linear baseline) |

---

## 🖥️ Power BI Executive Dashboard Architecture

The dashboard ([`HR_Executive_Dashboard.pbix`](HR_Executive_Dashboard.pbix)) is built on a **1920×1080 Full HD canvas** with a custom **Left App-Bar Navigation Rail** (`01`, `02`, `03`), interactive hover-glow overlays, and responsive cross-filtering.

### Page 1: Executive KPI & Turnover Financial Exposure
* **KPI Row**: Total Turnover Cost (\$12.33M), Regrettable Turnover Loss (\$6.46M), Active Headcount (1,233).
* **Row 2**:
  * *Clustered Column Chart*: Turnover Cost by Job Role (Sales Executives at \$4.63M, Lab Technicians at \$1.89M, Research Scientists at \$1.37M).
  * *Donut Chart*: Regrettable (\$6.46M / 52.4%) vs. Standard Turnover (\$5.87M / 47.6%) financial split.
* **Row 3**:
  * *Clustered Bar Chart*: Attrition Rate by Department × OverTime (OverTime drives 30.5% turnover vs. 10.4% non-overtime).
  * *Area Chart (Retention Cliff)*: Longitudinal attrition rate across `YearsAtCompany`, highlighting the acute 0–24 month cliff (29.8% attrition, 43% of all exits).

### Page 2: Pay-for-Performance & Meritocracy Audit
* **KPI Row**: Base Payment Diff (-\$188.50/mo), Merit Hike Delta (+7.85%), Top Talent Retention Advantage (-0.3%), Recalibration Investment Required (\$400,968).
* **Row 2**:
  * *Clustered Bar Chart*: Median Base Pay by Job Role & Performance Rating (uncovers role-level base pay inversions).
  * *100% Stacked Bar Chart*: Compensation Band Distribution by Rating (Under-Market `<0.85`, Competitive `0.85–1.15`, Above-Market `>1.15`).
* **Row 3**:
  * *Horizontal Bar Chart*: Underpaid Top Performers by Job Role (pinpoints the 30 active Rating 4 employees with `<0.85` CR).
  * *Donut Chart*: Recalibration Budget Share by Department (R&D requires 63.7%, Sales 25.3%, HR 11.1%).

### Page 3: Talent Retention & Flight-Risk Intelligence
* **KPI Row (Talent Action Tiles)**:
  * *Critical Retention Targets* (1 employee — \$15.8K exposure, emergency stay bonus).
  * *High-Potential Watchlist* (14 employees — \$669.0K exposure, career pathing & compensation review).
  * *Stable Future Leaders* (174 employees — \$18.66M exposure, 92.1% of top talent).
* **Row 2**:
  * *Horizontal Bar Chart*: Top 10 ML Attrition Drivers (Burnout Index 11.4%, Monthly Income 9.2%, Total Working Years 8.7%).
  * *Scatter Quadrant*: The Burnout vs. Flight-Risk Quadrant (plots individual employees by Burnout Index vs. Flight-Risk %, bubble size = replacement cost).
* **Row 3**:
  * *Clustered Column Chart*: Top Talent Retention Exposure by Department (R&D \$461.1K, Sales \$223.6K).
  * *AI Decomposition Tree*: Root-cause drilldown of at-risk talent by Department $\rightarrow$ Job Role $\rightarrow$ Compensation Band $\rightarrow$ OverTime.

---

## 🧠 Machine Learning & Analytical Methodology

### 1. Domain Metric Engineering
* **Compa-Ratio**: Individual salary relative to the median salary of their exact `JobRole` and `JobLevel`:
  $$\text{CompaRatio} = \frac{\text{MonthlyIncome}}{\text{Median}(\text{MonthlyIncome}_{\text{Role, Level}})}$$
* **Composite Burnout Index (0–100 scale)**:
  $$\text{BurnoutIndex} = 30 \cdot \mathbb{I}_{\text{OverTime}} + 25 \cdot \mathbb{I}_{\text{WLB} \le 2} + 20 \cdot \mathbb{I}_{\text{FreqTravel}} + 15 \cdot \mathbb{I}_{\text{Commute} \ge 15} + 10 \cdot \mathbb{I}_{\text{EnvSat} \le 2}$$
* **SHRM Turnover Replacement Cost**:
  * Top Performers (`Rating = 4`): **1.25× Annual Base Salary**
  * Senior / Management (`Level 3–5`): **1.00× Annual Base Salary**
  * Junior / Mid-Level (`Level 1–2`): **0.75× Annual Base Salary**

### 2. Predictive Modeling & Evaluation
* **Models**: `RandomForestClassifier` (150 trees, max depth 6) alongside an L2-regularized `LogisticRegression` baseline.
* **Leak-Free Scoring**: 5-Fold Stratified Out-of-Fold Cross-Validation (`cross_val_predict`) ensures no employee's probability score is evaluated on training data.
* **ROC-AUC**: **0.814** (Random Forest) | **0.837** (Logistic Regression Baseline).
* **Feature Importance**: Held-out permutation importance on out-of-sample data, eliminating cardinality bias.

---

## 🛠️ How to Run & Reproduce

### Prerequisites
* Python 3.10+
* Packages: `pandas`, `numpy`, `scikit-learn`
* Microsoft Power BI Desktop (May 2024 or newer recommended)

### Quickstart
```bash
# Clone the repository
git clone https://github.com/ahmedelsayed7115/hr-talent-performance-analytics.git
cd hr-talent-performance-analytics

# Install Python dependencies
pip install -r requirements.txt # or: pip install pandas numpy scikit-learn openpyxl

# Run the complete data processing, ML, and metrics export pipeline
python performance_analytics.py
```

### Viewing the Dashboard
Open [`HR_Executive_Dashboard.pbix`](HR_Executive_Dashboard.pbix) in **Power BI Desktop**. Navigate between pages using the custom sidebar app rail (`01`, `02`, `03`).

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
