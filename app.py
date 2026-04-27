# ================================================================
# IMPORT LIBRARIES
# ================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# ================================================================
# PAGE CONFIG
# ================================================================

st.set_page_config(page_title="AI BI Assistant", layout="wide")
st.title("🚀 AI Business Intelligence Assistant")

# ================================================================
# INDUSTRIES & SUBCATEGORIES
# ================================================================

INDUSTRIES = ["Retail", "SaaS", "FinTech", "Enterprise"]

SUBCATEGORIES = {
    "Retail": [
        "Executive Overview", "Sales Trend Analysis", "Regional Analysis",
        "Product Performance", "Customer Insights",
        "Inventory & Supply Analysis", "Forecast & AI insights"
    ],
    "SaaS": [
        "Executive Overview", "Customers Growth", "Revenue Analysis",
        "Churn Analysis", "Product Analysis", "Business Forecast"
    ],
    "FinTech": [
        "Executive Overview", "Transaction Analysis", "Fraud Detection",
        "Customer Insights", "Forecast & AI insights"
    ],
    "Enterprise": [
        "Financial Overview", "Customer Analytics", "Sales Analytics",
        "Operations Analytics", "HR Insights", "Forecast"
    ]
}

# ================================================================
# POWER BI LINKS
# ================================================================

POWERBI_LINKS = { 

    "Retail": {
        "base_url": "https://app.powerbi.com/reportEmbed?reportId=dce2a924-9892-4a79-b319-17f5718f8127&autoAuth=true&ctid=a01ef85e-a667-4caf-905e-72703b6785b9",
        "pages": {
            "Executive Overview": "ReportSection",
            "Sales Trend Analysis": "57d5d8ce13493a9e5759",
            "Regional Analysis": "bf5c8b4b705f5c918021",
            "Product Performance": "55ae3452c013679b4b67",
            "Customer Insights": "725d1ec40ec7fcdb4bb4",
            "Inventory & Supply Analysis": "a327537831d553d5320c",
            "Forecast & AI insights": "edb77ef7c195214a472a"
        }
    },

    "SaaS": {
        "base_url": "https://app.powerbi.com/reportEmbed?reportId=b3a89965-26d1-42d7-9799-e53a0ab5cbad&autoAuth=true&ctid=a01ef85e-a667-4caf-905e-72703b6785b9",
        "pages": {
            "Executive Overview": "ReportSection532efbd106e706d305ad",
            "Customers Growth": "f1d00a8de42ec1aebd13",
            "Revenue Analysis": "35e74586e1cce2c0035d",
            "Churn Analysis": "5f6dfd36f20952b86b16",
            "Product Analysis": "5965e6af8afffd5866e2",
            "Business Forecast": "3f21404c0475e334d58e"
        }
    },

    "FinTech": {
        "base_url": "https://app.powerbi.com/reportEmbed?reportId=0d073e55-c9d6-4160-a5cd-b8530aa46624&autoAuth=true&ctid=a01ef85e-a667-4caf-905e-72703b6785b9",
        "pages": {
            "Executive Overview": "60f56dba3d6296034305",
            "Transaction Analysis": "ed95125577886cb68055",
            "Fraud Detection": "b769ccf72cd799f9e0cc",
            "Customer Insights": "3aff73a693cdb85ca8f3",
            "Forecast & AI insights": "5f0ea21163b0ade45c14"
        }
    },

    "Enterprise": {
        "base_url": "https://app.powerbi.com/reportEmbed?reportId=8b7a6d9a-d1b8-461d-a3b5-749d31c65504&autoAuth=true&ctid=a01ef85e-a667-4caf-905e-72703b6785b9",
        "pages": {
            "Financial Overview": "8a94efe344e8466e7ab8",
            "Customer Analytics": "91ba5f4a7b0673880584",
            "Sales Analytics": "26ce174068d5fd280e71",
            "Operations Analytics": "9e2486ca36fcbf1e367e",
            "HR Insights": "4b5e42c1e08757991113",
            "Forecast": "6c71333cc7b534340975"
        }
    }

}
# ================================================================
# REQUIRED SCHEMA
# ================================================================

REQUIRED_COLUMNS = {
    "retail": ["date","revenue","profit","cost","order_quantity","country","state","product_category","sub_category","customer_age","customer_gender","unit_cost","unit_price"],
    "saas": ["date","mrr","arr","customer_name","customer_id","monthly_revenue","expansion_revenue","churn_status","churn_date","churned","churn_risk_score","plan_type","plan_tier","feature_usage","usage_count"],
    "fintech": ["date","transaction_amount","transaction_status","payment_mode","payment_channel","fraud_flag","risk_score","customer_name","customer_segment","region"],
    "enterprise": ["date","revenue","cost","profit","profit_margin","client_name","customer_segment","customer_satisfaction","units_sold","sales_channel","employee_productivity","system_downtime","employee_name","department","job_role","budget"]
}

# ================================================================
# FUNCTIONS
# ================================================================

def clean_dataset(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    df = df.drop_duplicates()
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)  # or None
    return df

def remove_duplicate_columns(df):
    return df.loc[:, ~df.columns.duplicated()]


def smart_column_mapping(df):
    mapping = {
        "transaction_amount": ["txn_amt","amount","transactionvalue"],
        "customer_name": ["customer","cust_name","name"],
        "customer_id": ["cust_id","id"],
        "payment_mode": ["paymentmethod","mode"],
        "payment_channel": ["channel"],
        "fraud_flag": ["fraud","is_fraud"],
        "revenue": ["sales","income"],
        "mrr": ["monthly_revenue"],
        "arr": ["annual_revenue"],
        "date": ["transaction_date","order_date"],
        "region": ["location","area"]
    }

    for std, variants in mapping.items():
        if std not in df.columns:
            for col in df.columns:
                if col in variants:
                    df.rename(columns={col: std}, inplace=True)
                    break
    return df
def convert_datetime_columns(df):

    date_cols = ["date", "churn_date"]

    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

            # Convert to Power BI format
            df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

    return df

def detect_industry(cols):
    text = " ".join(cols)
    if "product" in text:
        return "Retail"
    if "subscription" in text:
        return "SaaS"
    if "transaction" in text:
        return "FinTech"
    if "department" in text:
        return "Enterprise"
    return "Retail"

def align_columns(df, industry):
    required = REQUIRED_COLUMNS[industry.lower()]
    for col in required:
        if col not in df.columns:
            df[col] = None
    return df[required]

def data_quality_score(df):
    total = df.size
    missing = df.isna().sum().sum()
    completeness = (1 - missing / total) * 100
    duplicates = df.duplicated().sum()
    uniqueness = (1 - duplicates / len(df)) * 100
    return round((completeness + uniqueness) / 2, 2)

def fix_json_issues(df):
    # Replace NaN with None (valid JSON)
    df = df.replace({np.nan: None})

    # Also handle infinity values safely
    df = df.replace([np.inf, -np.inf], None)

    return df

def generate_ai_insights(df):
    insights = []
    if "revenue" in df.columns:
        insights.append(f"💰 Total Revenue: {df['revenue'].sum():,.2f}")
    if "transaction_amount" in df.columns:
        insights.append(f"💳 Total Transactions: {df['transaction_amount'].sum():,.2f}")
    if "churned" in df.columns:
        insights.append(f"⚠️ Churn Rate: {df['churned'].mean()*100:.2f}%")
    if "fraud_flag" in df.columns:
        insights.append(f"🚨 Fraud Rate: {df['fraud_flag'].mean()*100:.2f}%")
    return insights

# ✅ FIXED FUNCTION
def push_data(df, industry):

    url_map = {
        "Retail": "https://api.powerbi.com/beta/a01ef85e-a667-4caf-905e-72703b6785b9/datasets/d05c5e1f-bae4-4c56-b5db-56ec2be0ec75/rows?experience=power-bi&key=55A4CHeHhhv9j3POB7NDWRMao%2BjdGlGbi7%2BLchGXsTGElHqHYPpmLW2fw4kKFw%2BpchpyM6ZVuFxq4oWA1bebxg%3D%3D",
        "SaaS": "https://api.powerbi.com/beta/a01ef85e-a667-4caf-905e-72703b6785b9/datasets/4b813613-a2ce-4868-aad9-9d6b44dde303/rows?experience=power-bi&key=kXYhCYJqHdBCkTa9IXcvG09Es3LfwGxTAtbGnCYkq2yAYFpuqWJSpXPMNH0m0t4cOgJAw19auys2bWf06C0SOQ%3D%3D",
        "FinTech": "https://api.powerbi.com/beta/a01ef85e-a667-4caf-905e-72703b6785b9/datasets/c41f5fd6-03c7-427f-8f7b-db4308aafe13/rows?experience=power-bi&key=yiN2wnN%2Fbso5mAFM8CxWbO0Gy%2BXa%2F85MO6aN6y%2Blhjacn4TvAmTJCz9la325BH67FMruOzaRO9akuAezEL%2FB3w%3D%3D",
        "Enterprise": "https://api.powerbi.com/beta/a01ef85e-a667-4caf-905e-72703b6785b9/datasets/0a381b33-4801-4c94-88b4-00a485a7561d/rows?experience=power-bi&key=I6kPtzjw9UPs%2FMZQ2PGxUpc4mRqhIPFTs4xeLoiLHgtToWeuF3KacDPsHQd0yz%2FG%2F4YPPGZLuh7TaBeE%2Bkt5Tg%3D%3D"
    }

    url = url_map.get(industry)

    if not url:
        st.error("❌ Power BI URL missing")
        return False

    data = df.to_dict(orient="records")

    for i in range(0, len(data), 1000):
        res = requests.post(url, json=data[i:i+1000])

        if res.status_code != 200:
            st.error(res.text)
            return False

    return True

# ================================================================
# MAIN FLOW
# ================================================================

uploaded_file = st.file_uploader("Upload CSV Dataset", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    if df.empty:
        st.error("Empty file ❌")
        st.stop()

    df = clean_dataset(df)
    df = smart_column_mapping(df)
    df = remove_duplicate_columns(df)
    df = convert_datetime_columns(df)
    df["load_time"] = pd.Timestamp.now()


    st.subheader("📊 Uploaded Data")
    st.dataframe(df.head())

    industry = detect_industry(df.columns)
    st.success(f"Detected Industry: {industry}")

    df = align_columns(df, industry)
    df = fix_json_issues(df)

    score = data_quality_score(df)
    st.metric("📊 Data Quality Score", f"{score}%")

    st.subheader("🤖 AI Insights")
    for insight in generate_ai_insights(df):
        st.write(insight)

    numeric_cols = df.select_dtypes(include=np.number)
    if len(numeric_cols.columns) > 1:
        fig = px.imshow(numeric_cols.corr())
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Power BI Dashboard")

    subcategory = st.selectbox("Select Section", SUBCATEGORIES[industry])
    base_url = POWERBI_LINKS[industry]["base_url"]
    page_map = POWERBI_LINKS[industry]["pages"]

    if subcategory in page_map:
        page = page_map[subcategory]
        final_url = f"{base_url}&pageName={page}"
        st.components.v1.iframe(final_url, height=800)

    if st.button("🚀 Push to Power BI"):
        with st.spinner("Uploading..."):
            if push_data(df, industry):
                st.success("✅ Data sent successfully!")

else:
    st.info("Upload dataset to begin")

# ================================================================
# FOOTER
# ================================================================

st.caption("Power BI dashboards read data from powerbi_dataset.csv.")