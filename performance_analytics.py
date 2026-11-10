"""
================================================================================
ENTERPRISE HR PERFORMANCE & TALENT ANALYTICS ENGINE
================================================================================
Purpose:
    End-to-end analytical pipeline designed for Senior HR Performance & People
    Analytics. Evaluates pay-for-performance meritocracy, 9-box talent matrix,
    out-of-fold flight risk scoring, and financial costs of regrettable attrition.

Key Analytical Pillars:
    1. Pay-for-Performance & Compa-Ratio Audit (Market Equity & Meritocracy)
    2. Regrettable vs. Non-Regrettable Turnover & Financial Replacement Cost
    3. Multi-Factor Burnout & Career Stagnation Indexing
    4. Predictive Flight-Risk Modeling (Logistic Regression Baseline + Random Forest
       with 5-Fold Out-of-Fold Probability Scoring & Permutation Importance)
    5. 9-Box Talent Matrix (Performance vs. Retention Risk)
================================================================================
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, train_test_split, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score


def load_data(filepath: str) -> pd.DataFrame:
    """Load and perform initial data validation."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at {filepath}")
    df = pd.read_csv(filepath)
    print(f"[+] Loaded dataset: {df.shape[0]} records, {df.shape[1]} attributes.")
    return df


def engineer_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer domain-specific HR performance and talent metrics:
    - Compa-Ratio (salary relative to role + level median)
    - Career Velocity & Promotion Stagnation
    - Burnout Risk Index
    - Regrettable Turnover Flag & SHRM Replacement Cost
    """
    df = df.copy()

    # 1. Compa-Ratio: MonthlyIncome / Median(MonthlyIncome by JobRole & JobLevel)
    role_level_medians = (
        df.groupby(['JobRole', 'JobLevel'])['MonthlyIncome']
        .median()
        .reset_index()
        .rename(columns={'MonthlyIncome': 'RoleLevelMedianIncome'})
    )
    df = df.merge(role_level_medians, on=['JobRole', 'JobLevel'], how='left')
    df['CompaRatio'] = (df['MonthlyIncome'] / df['RoleLevelMedianIncome']).round(3)

    # Compa-Ratio Category (Standard HR Compensation benchmarking)
    # Below 0.85 = Underpaid vs peer band, 0.85-1.15 = Market competitive, > 1.15 = Premium
    df['CompensationBand'] = pd.cut(
        df['CompaRatio'],
        bins=[-np.inf, 0.85, 1.15, np.inf],
        labels=['Under-Market (<0.85)', 'Market-Competitive (0.85-1.15)', 'Above-Market (>1.15)']
    )

    # 2. Career Stagnation & Velocity
    # High risk: 3+ years since last promotion while staying in current role >= 3 years
    df['PromotionStagnant'] = (
        (df['YearsSinceLastPromotion'] >= 3) & (df['YearsInCurrentRole'] >= 3)
    ).astype(int)

    # Career Velocity: Job Level attained relative to Total Working Years
    df['CareerVelocity'] = (df['JobLevel'] / np.maximum(df['TotalWorkingYears'], 1)).round(3)

    # 3. Burnout Risk Index (0 - 100 Scale)
    # Composite indicator based on established I/O psychology factors:
    # OverTime (+30), Travel (+20/5), Poor WorkLifeBalance (+25), Long Commute (+15), Low Env Satisfaction (+10)
    burnout_score = np.zeros(len(df))
    burnout_score += np.where(df['OverTime'] == 'Yes', 30, 0)
    burnout_score += np.where(
        df['BusinessTravel'] == 'Travel_Frequently', 20,
        np.where(df['BusinessTravel'] == 'Travel_Rarely', 5, 0)
    )
    burnout_score += np.where(df['WorkLifeBalance'] <= 2, 25, 0)
    burnout_score += np.where(df['DistanceFromHome'] >= 15, 15, 0)
    burnout_score += np.where(df['EnvironmentSatisfaction'] <= 2, 10, 0)
    df['BurnoutIndex'] = burnout_score

    # 4. Regrettable vs. Standard Attrition
    df['AttritionNumeric'] = (df['Attrition'] == 'Yes').astype(int)

    def classify_attrition_type(row):
        if row['AttritionNumeric'] == 1:
            if row['PerformanceRating'] == 4:
                return 'Regrettable Attrition (Top Performer)'
            elif row['JobInvolvement'] >= 3 and row['JobLevel'] >= 2:
                return 'Regrettable Attrition (Core Talent)'
            else:
                return 'Non-Regrettable / Standard Attrition'
        return 'Active Employee'

    df['AttritionCategory'] = df.apply(classify_attrition_type, axis=1)

    # Financial Replacement Cost per employee (SHRM Standard: 75% to 125% of Annual Base)
    def calculate_replacement_cost(row):
        annual_salary = row['MonthlyIncome'] * 12
        if row['PerformanceRating'] == 4:
            multiplier = 1.25  # High-impact replacement & lost institutional knowledge
        elif row['JobLevel'] >= 3:
            multiplier = 1.00  # Senior/Managerial role replacement
        else:
            multiplier = 0.75  # Mid/Junior role replacement
        return round(annual_salary * multiplier, 2)

    df['EstimatedReplacementCost'] = df.apply(calculate_replacement_cost, axis=1)

    return df


def audit_pay_for_performance(df: pd.DataFrame) -> dict:
    """
    Audit whether compensation, merit raises, and equity reward high performance.
    """
    p4p_df = df.groupby('PerformanceRating').agg(
        Headcount=('EmployeeNumber', 'count'),
        ActiveHeadcount=('AttritionNumeric', lambda s: int((s == 0).sum())),
        DepartedHeadcount=('AttritionNumeric', 'sum'),
        AvgMonthlyIncome=('MonthlyIncome', lambda s: round(float(s.mean()), 2)),
        MedianMonthlyIncome=('MonthlyIncome', lambda s: round(float(s.median()), 2)),
        AvgSalaryHike=('PercentSalaryHike', lambda s: round(float(s.mean()), 2)),
        MedianSalaryHike=('PercentSalaryHike', lambda s: round(float(s.median()), 2)),
        AvgCompaRatio=('CompaRatio', lambda s: round(float(s.mean()), 2)),
        AvgStockOption=('StockOptionLevel', lambda s: round(float(s.mean()), 2)),
        AttritionRate=('AttritionNumeric', lambda s: round(float(s.mean()), 4)),
        AttritionRatePct=('AttritionNumeric', lambda s: round(float(s.mean() * 100), 2))
    )

    return {str(k): v for k, v in p4p_df.to_dict(orient='index').items()}


def train_flight_risk_model(df: pd.DataFrame):
    """
    Train predictive models (Logistic Regression baseline + Random Forest)
    and compute 5-fold out-of-fold Flight-Risk Probability (0.0 to 1.0)
    so no employee is scored by a model that trained on their own label.
    """
    # Avoid collinear double-counting: use composite BurnoutIndex rather than
    # duplicating its raw sub-components (OverTime, BusinessTravel, WorkLifeBalance,
    # DistanceFromHome, EnvironmentSatisfaction) alongside it.
    feature_cols = [
        'Age', 'CompaRatio', 'BurnoutIndex', 'JobInvolvement', 'JobLevel',
        'JobSatisfaction', 'MonthlyIncome', 'NumCompaniesWorked',
        'PercentSalaryHike', 'PerformanceRating', 'RelationshipSatisfaction',
        'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear',
        'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
        'YearsWithCurrManager', 'PromotionStagnant'
    ]
    categorical_cols = ['Department', 'JobRole', 'MaritalStatus']

    X_encoded = pd.get_dummies(df[feature_cols + categorical_cols], drop_first=True)
    y = df['AttritionNumeric']

    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.20, random_state=42, stratify=y
    )

    # 1. Baseline: L2-Regularized Logistic Regression with StandardScaler
    lr_pipeline = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    )
    lr_pipeline.fit(X_train, y_train)
    lr_roc_auc = roc_auc_score(y_test, lr_pipeline.predict_proba(X_test)[:, 1])

    # 2. Primary Model: Random Forest Classifier
    rf_model = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_roc_auc = roc_auc_score(y_test, rf_model.predict_proba(X_test)[:, 1])

    # 3. Out-of-Fold (5-Fold Stratified CV) probability scoring for full workforce
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_proba = cross_val_predict(
        RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42),
        X_encoded, y, cv=cv, method='predict_proba'
    )[:, 1]
    df['FlightRiskProbability'] = oof_proba.round(3)

    # Assign Risk Tier
    df['FlightRiskTier'] = pd.cut(
        df['FlightRiskProbability'],
        bins=[-np.inf, 0.20, 0.40, 0.65, np.inf],
        labels=['Low Risk', 'Moderate Risk', 'Elevated Risk', 'Critical Risk']
    )

    # 4. Held-out Permutation Feature Importance (unbiased towards high-cardinality continuous features)
    perm_imp = permutation_importance(
        rf_model, X_test, y_test, n_repeats=15, random_state=42, scoring='roc_auc'
    )
    raw_imp = np.maximum(perm_imp.importances_mean, 0)
    norm_imp = raw_imp / raw_imp.sum() if raw_imp.sum() > 0 else rf_model.feature_importances_

    feature_importance = pd.DataFrame({
        'Feature': X_encoded.columns,
        'Importance': norm_imp
    }).sort_values(by='Importance', ascending=False).head(10)

    return df, rf_model, rf_roc_auc, lr_roc_auc, feature_importance


def construct_talent_9box_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construct an enterprise 9-Box Talent & Retention Matrix:
    - Y-Axis: Performance Level (Rating 4: Outstanding, Rating 3: Solid/Core)
    - X-Axis: Retention Security / Risk (Low Risk, Moderate Risk, High/Critical Risk)
    """
    def categorize_9box(row):
        perf = "High (Rating 4)" if row['PerformanceRating'] == 4 else "Solid (Rating 3)"
        risk = row['FlightRiskTier']

        if perf == "High (Rating 4)":
            if risk in ['Elevated Risk', 'Critical Risk']:
                return "1. TOP TALENT AT CRITICAL RISK (Emergency Intervention)"
            elif risk == 'Moderate Risk':
                return "2. HIGH POTENTIAL - RETENTION WATCH (Career Growth)"
            else:
                return "3. FUTURE ENTERPRISE LEADERS (Secure Top Talent)"
        else:
            if risk in ['Elevated Risk', 'Critical Risk']:
                return "4. CORE CONTRIBUTOR BURNOUT RISK (Workload/Pay Review)"
            elif risk == 'Moderate Risk':
                return "5. STEADY WORKFORCE CONTRIBUTORS (Engagement Focus)"
            else:
                return "6. TRUSTED BEDROCK PERFORMERS (Stable Core)"

    df['TalentMatrixSegment'] = df.apply(categorize_9box, axis=1)
    return df


def generate_executive_insights(
    df: pd.DataFrame,
    p4p_stats: dict,
    rf_roc_auc: float,
    lr_roc_auc: float,
    feature_imp: pd.DataFrame
) -> dict:
    """
    Generate senior executive KPI summaries and dollar impact calculations.
    """
    total_headcount = len(df)
    total_attrition = int(df['AttritionNumeric'].sum())
    overall_attrition_rate = round((total_attrition / total_headcount) * 100, 2)

    # Financial Loss Calculations
    attrition_df = df[df['AttritionNumeric'] == 1]
    total_replacement_cost = float(attrition_df['EstimatedReplacementCost'].sum())

    regrettable_df = attrition_df[attrition_df['AttritionCategory'].str.startswith('Regrettable')]
    regrettable_cost = float(regrettable_df['EstimatedReplacementCost'].sum())
    non_regrettable_cost = round(total_replacement_cost - regrettable_cost, 2)
    regrettable_count = int(len(regrettable_df))
    non_regrettable_count = int(total_attrition - regrettable_count)
    regrettable_headcount_pct = round((regrettable_count / total_attrition) * 100, 2)
    regrettable_cost_pct = round((regrettable_cost / total_replacement_cost) * 100, 2)

    # Department Turnover Cost Breakdown
    dept_costs = {}
    for dept, grp in attrition_df.groupby('Department'):
        d_cost = round(float(grp['EstimatedReplacementCost'].sum()), 2)
        dept_costs[dept] = {
            "departed_count": int(len(grp)),
            "replacement_cost_usd": d_cost,
            "cost_share_pct": round((d_cost / total_replacement_cost) * 100, 2)
        }

    # Active Workforce Segmentation
    active_df = df[df['AttritionNumeric'] == 0]
    critical_active_top_performers = active_df[
        (active_df['PerformanceRating'] == 4) &
        (active_df['FlightRiskTier'].isin(['Elevated Risk', 'Critical Risk']))
    ]
    watchlist_active_top_performers = active_df[
        (active_df['PerformanceRating'] == 4) &
        (active_df['FlightRiskTier'] == 'Moderate Risk')
    ]
    stable_active_top_performers = active_df[
        (active_df['PerformanceRating'] == 4) &
        (active_df['FlightRiskTier'] == 'Low Risk')
    ]

    top_performer_exposure_cost = float(critical_active_top_performers['EstimatedReplacementCost'].sum())
    watchlist_exposure_cost = float(watchlist_active_top_performers['EstimatedReplacementCost'].sum())

    # Underpaid High Performers (Active, Rating 4, CompaRatio < 0.85)
    underpaid_top = active_df[
        (active_df['PerformanceRating'] == 4) & (active_df['CompaRatio'] < 0.85)
    ]
    underpaid_exposure = float(underpaid_top['EstimatedReplacementCost'].sum())
    recalibration_budget = float(
        ((underpaid_top['RoleLevelMedianIncome'] - underpaid_top['MonthlyIncome']) * 12).sum()
    )
    recalibration_roi = round(underpaid_exposure / recalibration_budget, 2) if recalibration_budget > 0 else 0.0

    # Active 9-Box Counts
    nine_box_counts = active_df['TalentMatrixSegment'].value_counts().to_dict()

    executive_metrics = {
        "workforce_summary": {
            "total_employees": int(total_headcount),
            "active_employees": int(len(active_df)),
            "departed_employees": int(total_attrition),
            "attrition_rate_pct": overall_attrition_rate
        },
        "financial_impact": {
            "total_turnover_replacement_cost_usd": total_replacement_cost,
            "regrettable_turnover_cost_usd": regrettable_cost,
            "non_regrettable_turnover_cost_usd": non_regrettable_cost,
            "regrettable_departures_count": regrettable_count,
            "non_regrettable_departures_count": non_regrettable_count,
            "regrettable_headcount_share_pct": regrettable_headcount_pct,
            "regrettable_cost_share_pct": regrettable_cost_pct,
            "immediate_flight_risk_exposure_usd": top_performer_exposure_cost,
            "watchlist_flight_risk_exposure_usd": watchlist_exposure_cost,
            "top_talent_combined_risk_exposure_usd": top_performer_exposure_cost + watchlist_exposure_cost,
            "department_turnover_cost_usd": dept_costs
        },
        "talent_matrix_status": {
            "critical_retention_targets_count": int(len(critical_active_top_performers)),
            "high_potential_watchlist_count": int(len(watchlist_active_top_performers)),
            "at_risk_top_talent_combined_count": int(len(critical_active_top_performers) + len(watchlist_active_top_performers)),
            "stable_future_leaders_count": int(len(stable_active_top_performers)),
            "underpaid_high_performers_count": int(len(underpaid_top)),
            "underpaid_avg_compa_ratio": round(float(underpaid_top['CompaRatio'].mean()), 3),
            "underpaid_replacement_exposure_usd": underpaid_exposure,
            "recalibration_budget_required_usd": round(recalibration_budget, 2),
            "recalibration_roi_multiple": recalibration_roi,
            "model_roc_auc": round(rf_roc_auc, 3),
            "logistic_regression_baseline_roc_auc": round(lr_roc_auc, 3),
            "nine_box_active_counts": nine_box_counts
        },
        "pay_for_performance_audit": p4p_stats,
        "top_attrition_drivers": feature_imp.to_dict(orient='records')
    }

    return executive_metrics


def run_pipeline():
    """Main execution orchestrator."""
    data_path = "WA_Fn-UseC_-HR-Employee-Attrition.csv"
    print("=" * 80)
    print("STARTING HR PERFORMANCE & TALENT ANALYTICS PIPELINE")
    print("=" * 80)

    raw_df = load_data(data_path)
    df = engineer_performance_metrics(raw_df)
    p4p_stats = audit_pay_for_performance(df)
    df, model, rf_roc_auc, lr_roc_auc, feature_imp = train_flight_risk_model(df)
    df = construct_talent_9box_matrix(df)
    summary = generate_executive_insights(df, p4p_stats, rf_roc_auc, lr_roc_auc, feature_imp)

    output_csv = "enriched_hr_performance_data.csv"
    output_json = "hr_performance_executive_metrics.json"
    output_imp_csv = "Model_Feature_Importance.csv"

    df.to_csv(output_csv, index=False)
    feature_imp.to_csv(output_imp_csv, index=False)
    with open(output_json, 'w') as f:
        json.dump(summary, f, indent=4)

    print(f"\n[+] Pipeline execution completed successfully!")
    print(f"[+] Enriched dataset saved to: {output_csv}")
    print(f"[+] Feature importance saved to: {output_imp_csv}")
    print(f"[+] Executive metrics saved to: {output_json}")


if __name__ == '__main__':
    run_pipeline()
