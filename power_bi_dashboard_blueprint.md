# Enterprise HR Performance & Talent Analytics — Power BI Dashboard Blueprint

This blueprint provides the complete end-to-end design, data model, and copy-paste DAX formulas to build and maintain the executive-grade **Power BI report** ([`HR_Executive_Dashboard_v4.pbix`](file:///d:/ME/port/hr/HR_Executive_Dashboard_v4.pbix)).

---

## 1. Data Source & Modeling Architecture

### 1.1 Data Sources
* **Primary Fact Table**: `Fact_EmployeePerformance` (`1,470` records: `1,233` Active, `237` Departed) imported from [`HR_Performance_Analytics_PowerBI.xlsx`](file:///d:/ME/port/hr/HR_Performance_Analytics_PowerBI.xlsx) (or [`enriched_hr_performance_data.csv`](file:///d:/ME/port/hr/enriched_hr_performance_data.csv)).
* **ML Feature Importance Table**: `Model_FeatureImportance` (`10` ranked features) imported from [`Model_Feature_Importance.xlsx`](file:///d:/ME/port/hr/Model_Feature_Importance.xlsx) (or [`Model_Feature_Importance.csv`](file:///d:/ME/port/hr/Model_Feature_Importance.csv)) to power the Page 3 Top Attrition Drivers chart.

### 1.2 Dedicated Measures Table
In Power BI Desktop:
1. Click **Enter Data** in the Home tab.
2. Name the table `_Measures` and click **Load**.
3. Create all DAX measures below inside this dedicated table for clean, professional governance.

---

## 2. Complete Production DAX Measures Library

Organize your DAX measures into 4 folders inside `_Measures`:

### Folder 1: Workforce & Turnover KPIs

```dax
// 1. Total Headcount (1,470)
Total Employees = COUNTROWS(Fact_EmployeePerformance)

// 2. Active Workforce (1,233)
Active Employees = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "No"
)

// 3. Departed Headcount (237)
Departed Employees = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "Yes"
)

// 4. Overall Attrition Rate % (16.12%)
Attrition Rate = 
DIVIDE([Departed Employees], [Total Employees], 0)

// 5. Regrettable Departures (87 exits: 37 Top Performers + 50 Core Talent)
Regrettable Departures = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "Yes",
    Fact_EmployeePerformance[AttritionCategory] IN {
        "Regrettable Attrition (Top Performer)",
        "Regrettable Attrition (Core Talent)"
    }
)

// 6. Regrettable Headcount Share % (36.71% of exits)
Regrettable Attrition Share = 
DIVIDE([Regrettable Departures], [Departed Employees], 0)

// 6b. Regrettable Cost Share % (52.40% of financial loss)
Regrettable Cost Share = 
DIVIDE([Regrettable Turnover Cost], [Total Turnover Cost], 0)
```

---

### Folder 2: Financial Impact & Turnover Costs

```dax
// 7. Total Turnover Replacement Cost ($12,327,384)
Total Turnover Cost = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "Yes"
)

// 8. Regrettable Turnover Financial Loss ($6,458,949)
Regrettable Turnover Cost = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "Yes",
    Fact_EmployeePerformance[AttritionCategory] IN {
        "Regrettable Attrition (Top Performer)",
        "Regrettable Attrition (Core Talent)"
    }
)

// 8b. Non-Regrettable Turnover Cost ($5,868,435)
Non-Regrettable Turnover Cost = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "Yes",
    Fact_EmployeePerformance[AttritionCategory] = "Non-Regrettable / Standard Attrition"
)

// 9. Average Replacement Cost Per Departed Employee ($52,014)
Avg Replacement Cost = 
DIVIDE([Total Turnover Cost], [Departed Employees], 0)

// 10. Immediate Critical Flight-Risk Exposure ($15,780 — 1 Active Rating 4 in Critical/Elevated Risk)
Flight Risk Exposure Cost = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] IN {"Elevated Risk", "Critical Risk"}
)

// 10b. Watchlist Flight-Risk Exposure ($669,000 — 14 Active Rating 4 in Moderate Risk)
Watchlist Exposure Cost = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] = "Moderate Risk"
)

// 10c. Combined At-Risk Top Talent Exposure ($684,780 — 15 Active Rating 4 in Moderate/Elevated/Critical Risk)
Top Talent Risk Exposure = 
CALCULATE(
    SUM(Fact_EmployeePerformance[EstimatedReplacementCost]),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] IN {"Moderate Risk", "Elevated Risk", "Critical Risk"}
)
```

---

### Folder 3: Pay-for-Performance & Equity Metrics

```dax
// 11. Median Monthly Income (Rating 3: $4,965.50)
Median Income Rating 3 = 
CALCULATE(
    MEDIAN(Fact_EmployeePerformance[MonthlyIncome]),
    Fact_EmployeePerformance[PerformanceRating] = 3
)

// 12. Median Monthly Income (Rating 4: $4,777.00)
Median Income Rating 4 = 
CALCULATE(
    MEDIAN(Fact_EmployeePerformance[MonthlyIncome]),
    Fact_EmployeePerformance[PerformanceRating] = 4
)

// 13. Pay-for-Performance Base Inversion Delta (-$188.50/mo)
Base Pay Inversion Delta = [Median Income Rating 4] - [Median Income Rating 3]

// 14. Average Compa-Ratio (1.03 Rating 3 vs 1.01 Rating 4)
Avg Compa-Ratio = AVERAGE(Fact_EmployeePerformance[CompaRatio])

// 15. Average Salary Hike % (14.00% Rating 3 vs 21.85% Rating 4)
Avg Salary Hike Pct = AVERAGE(Fact_EmployeePerformance[PercentSalaryHike]) / 100

// 16. Underpaid High-Performers Count (30 Active Top Performers with Compa-Ratio < 0.85)
Underpaid High Performers = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[CompaRatio] < 0.85
)

// 17. Annual Budget Required to Recalibrate Underpaid High-Performers to 1.00 Market Parity ($400,968)
Recalibration Budget Required = 
CALCULATE(
    SUMX(
        FILTER(
            Fact_EmployeePerformance,
            Fact_EmployeePerformance[Attrition] = "No" &&
            Fact_EmployeePerformance[PerformanceRating] = 4 &&
            Fact_EmployeePerformance[CompaRatio] < 0.85
        ),
        (Fact_EmployeePerformance[RoleLevelMedianIncome] - Fact_EmployeePerformance[MonthlyIncome]) * 12
    )
)
```

---

### Folder 4: Talent Matrix Counts & Dynamic Card Subtitles

```dax
// 18. Average Burnout Index
Avg Burnout Index = AVERAGE(Fact_EmployeePerformance[BurnoutIndex])

// 19. Critical Retention Targets Count (1 Employee)
Critical Retention Targets = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] IN {"Elevated Risk", "Critical Risk"}
)

// 20. High-Potential Watchlist Count (14 Employees)
High Potential Watchlist = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] = "Moderate Risk"
)

// 21. Stable Future Leaders Count (174 Employees)
Stable Future Leaders = 
CALCULATE(
    COUNTROWS(Fact_EmployeePerformance),
    Fact_EmployeePerformance[Attrition] = "No",
    Fact_EmployeePerformance[PerformanceRating] = 4,
    Fact_EmployeePerformance[FlightRiskTier] = "Low Risk"
)

// 22. % of Active Rating 4 Leaders in Stable Low-Risk Tier (92.1%)
Pct Stable Leaders = 
DIVIDE(
    [Stable Future Leaders],
    CALCULATE([Active Employees], Fact_EmployeePerformance[PerformanceRating] = 4),
    0
)

// 23. Dynamic Card Subtitle for Underpaid Talent
Underpaid Talent Subtitle = 
FORMAT([Underpaid High Performers], "#,##0") & " Top Performers paid <85% peer median (" & 
FORMAT([Recalibration Budget Required], "$#,##0") & " recalibration pool required)"

// 24. Early Tenure (First-2-Years) Attrition Rate (34.3%)
Early Tenure Attrition Rate = 
CALCULATE(
    [Attrition Rate],
    Fact_EmployeePerformance[YearsAtCompany] <= 2
)
```

---

## 3. Page-by-Page Visual Layout & Architecture

The report uses a modern **1920×1080 Full HD canvas** with a **Dark Left App-Bar Navigation Rail (`x = 0, width = 63.3px`, Fill `#112D4E`)** containing interactive page-switching buttons (`01`, `02`, `03`) with active highlights and hover-glow animations, plus 2 hidden Drillthrough rosters.

```
Dashboard Structure:
├── Left Sidebar App-Rail: Interactive Page Navigation Buttons (01, 02, 03)
├── Page 1: Executive KPI & Turnover Financial Exposure
├── Page 2: Pay-for-Performance & Meritocracy Audit
├── Page 3: Talent Retention & Flight-Risk Intelligence
├── [Hidden] Drillthrough A: Compensation Equity Roster
└── [Hidden] Drillthrough B: Flight-Risk Action Roster
```

---

### Page 1: Executive KPI & Turnover Financial Exposure

#### Header & Global Slicers (Top Bar)
* **Title**: `WORKFORCE & TALENT FINANCIAL INTELLIGENCE`
* **Subtitle**: `Enterprise Attrition Economics, Replacement Cost Exposure & Lifecycle Retention Diagnostics`
* **Slicers (Horizontal dropdowns)**: `Department`, `JobRole`, `OverTime`

#### Row 1: KPI Cards (with Dynamic Subtitles & Hover-Glow Overlays)
1. **Total Turnover Cost**: `[Total Turnover Cost]` (**$12.33M**) | Sub: *"237 exits | 16.1% attrition rate"*
2. **Regrettable Turnover Cost**: `[Regrettable Turnover Cost]` (**$6.46M**) | Sub: *"87 key exits | 52.4% of total cost"*
3. **Active Workforce**: `[Active Employees]` (**1,233**) | Sub: *"83.9% retention | 1,470 total headcount"*

#### Row 2: Two Charts (55% / 45% Split)

* **Visual 1 (Left 55%): Clustered Column Chart — Turnover Cost by Job Role**
  * **X-Axis**: `JobRole` | **Y-Axis**: `[Total Turnover Cost]`
  * **Color**: Primary Navy `#1E3A8A` | **Data Labels**: On
  * *Story*: Identifies Sales Executives ($4.57M) and Research Scientists ($1.90M) as the primary turnover cost centers.

* **Visual 2 (Right 45%): Donut Chart — Regrettable vs. Standard Turnover Split**
  * **Legend**: `AttritionCategory` | **Values**: `[Total Turnover Cost]`
  * **Colors**: Regrettable (Top Performer) `#1E3A8A`, Regrettable (Core Talent) `#0D9488`, Standard Turnover `#94A3B8`.
  * *Story*: Shows that **52.40%** ($6.46M) of total replacement cost comes from the **36.71%** (87 exits) classified as regrettable departures.

#### Row 3: Two Charts (50% / 50% Balanced Split)

* **Visual 1 (Left 50%): Clustered Bar Chart — Attrition Rate by Department & OverTime**
  * **Y-Axis**: `Department` | **X-Axis**: `[Attrition Rate]` | **Legend**: `OverTime` (`Yes` = `#EF4444`, `No` = `#0D9488`)
  * *Story*: OverTime employees leave at **30.53%** vs. **10.44%** for non-OverTime peers.

* **Visual 2 (Right 50%): Area Chart — The "Retention Cliff" Curve: Attrition Rate Across Tenure**
  * **X-Axis**: `YearsAtCompany` (Continuous 0 to 40) | **Y-Axis**: `[Attrition Rate]`
  * *Story*: Highlights the acute onboarding retention cliff during years 0–2 (where attrition exceeds **34%**).

---

### Page 2: Pay-for-Performance & Meritocracy Audit

#### Header & Slicers
* **Title**: `PAY-FOR-PERFORMANCE & MERITOCRACY AUDIT`
* **Subtitle**: `Salary Compression Diagnostics, Compa-Ratio Parity & Recalibration Budget Modeling`
* **Slicers (Horizontal dropdowns)**: `Department`, `JobRole`, `JobLevel`

#### Row 1: KPI Cards
1. **Base Payment Diff**: `[Base Pay Inversion Delta]` (**-$188.50/mo**) | Sub: *"Rating 4 ($4,777) vs Rating 3 ($4,966) median"*
2. **Merit Hike Differentiation**: **+7.85% Hike** | Sub: *"Rating 4 (21.85%) vs Rating 3 (14.00%) avg"*
3. **Top Talent Retention Advantage**: `[Retention Premium]` (**-0.3%**) | Sub: *"Rating 4: (16.4%) vs. Rating 3: (16.1%) Attrition"*
4. **Recalibration Investment Required**: `[Recalibration Budget Required]` (**$400,968**) | Sub: *"30 underpaid top performers (<0.85 Compa-Ratio)"*

#### Row 2: Two Charts (50% / 50% Split)

* **Visual 1 (Left 50%): Clustered Bar Chart — Median Base Pay by Job Role & Rating**
  * **Y-Axis**: `JobRole` | **X-Axis**: `MonthlyIncome` (Median) | **Legend**: `PerformanceRating`
* **Visual 2 (Right 50%): Scatter Chart — Compensation Parity & Market Compa-Ratio Matrix**
  * **Category (Detail)**: `EmployeeNumber` (plots individual employees rather than a single aggregate bubble)
  * **X-Axis**: `CompaRatio` | **Y-Axis**: `MonthlyIncome` | **Legend**: `PerformanceRating` | **Size**: `EstimatedReplacementCost`
  * **Reference Lines**: Vertical lines at `X = 1.00` (Market Parity) and `X = 0.85` (Under-Market Danger Threshold).

#### Row 3: Two Charts (50% / 50% Split)

* **Visual 1 (Left 50%): Horizontal Bar Chart — Underpaid Top Performers by Job Role**
  * **Y-Axis**: `JobRole` | **X-Axis**: `[Underpaid High Performers]`
  * *Story*: Pinpoints where the 30 underpaid top performers sit (`Avg Compa-Ratio = 0.745`, `$1,577,340` replacement exposure). Right-click any bar to **Drillthrough** to **Drillthrough A**.

* **Visual 2 (Right 50%): Waterfall Chart — Market Parity Recalibration Investment Bridge by Role**
  * **Category**: `JobRole` | **Y-Axis**: `[Recalibration Budget Required]` (**$400,968** total pool to bring all 30 underpaid top performers to `1.00` Compa-Ratio, delivering a **3.93× ROI** against **$1,577,340** in replacement risk).

---

### Page 3: Talent Retention & Flight-Risk Intelligence

#### Header & Slicers
* **Title**: `PREDICTIVE FLIGHT-RISK & RETENTION INTELLIGENCE`
* **Subtitle**: `Machine Learning Attrition Drivers, Burnout Exposure Matrix & Priority Intervention Targets`
* **Slicers (Horizontal dropdowns)**: `Department`, `JobRole`, `PerformanceRating`

#### Row 1: Three Priority Talent Segment Tiles (Active Rating 4 Workforce: 189 Employees)

1. **Critical Retention Targets** (Red Accent `#EF4444`):
   * **Measure**: `[Critical Retention Targets]` (**1 employee** — Rating 4 + Elevated/Critical Risk)
   * **Subtitle**: *"$15.8K exposure | Immediate stay intervention"*
2. **High-Potential Watchlist** (Amber Accent `#F59E0B`):
   * **Measure**: `[High Potential Watchlist]` (**14 employees** — Rating 4 + Moderate Risk)
   * **Subtitle**: *"$669.0K exposure | Career growth & comp review"*
3. **Stable Future Leaders** (Teal Accent `#0D9488`):
   * **Measure**: `[Stable Future Leaders]` (**174 employees** — Rating 4 + Low Risk)
   * **Subtitle**: *"92.1% of top talent | Leadership pipeline"*

#### Row 2: Two Charts (45% / 55% Split)

* **Visual 1 (Left 45%): Horizontal Bar Chart — Top Attrition Drivers (Feature Importance)**
  * **Table**: `Model_FeatureImportance`
  * **Y-Axis**: `Feature` | **X-Axis**: `Importance` (`BurnoutIndex` 11.4%, `MonthlyIncome` 9.2%, `TotalWorkingYears` 8.7%, `Age` 7.4%, `YearsAtCompany` 5.3%).

* **Visual 2 (Right 55%): Scatter Chart — The Burnout vs. Flight-Risk Quadrant Matrix**
  * **Visual Filter**: `Attrition = "No"` (Active employees only: `1,233` personnel)
  * **Category (Detail)**: `EmployeeNumber`
  * **X-Axis**: `BurnoutIndex` (0 to 100) | **Y-Axis**: `FlightRiskProbability` (0% to 100%)
  * **Size**: `EstimatedReplacementCost` | **Legend**: `FlightRiskTier`

#### Row 3: Two Charts (50% / 50% Split)

* **Visual 1 (Left 50%): Clustered Column Chart — At-Risk Top Talent Exposure by Department**
  * **X-Axis**: `Department` | **Y-Axis**: `[Top Talent Risk Exposure]` (**$684,780** combined across 15 Moderate/Elevated/Critical Rating 4 employees: **$461,145** in R&D and **$223,635** in Sales).

* **Visual 2 (Right 50%): Decomposition Tree (AI Visual) — Root Cause Breakdown of Top Talent Risk Exposure**
  * **Visual Filter**: `Attrition = "No"` (Active workforce)
  * **Analyze**: `[Top Talent Risk Exposure]` ($684,780)
  * **Explain By**: `Department`, `JobRole`, `OverTime`, `CompensationBand`, `BurnoutIndex`

---

### Drillthrough A: Compensation Equity Roster (Hidden Page)

* **Access**: Right-click any bar on Page 2 Row 3 (Underpaid Top Performers) → Drillthrough.
* **Drillthrough Field**: `JobRole`
* **Default Filter**: `Attrition = "No"`, `CompaRatio < 0.85`, AND `PerformanceRating = 4` (30 active employees).

### Drillthrough B: Flight-Risk Action Roster (Hidden Page)

* **Access**: Right-click any bar/tile on Page 3 → Drillthrough.
* **Drillthrough Field**: `Department`
* **Default Filter**: Active Employees (`Attrition = "No"`), sorted by `FlightRiskProbability` descending.
