import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import os

st.set_page_config(page_title="Fraud Risk Analytics", page_icon="🛡️", layout="wide")

EXPECTED_COLUMNS = ['Time', 'Amount'] + [f'V{i}' for i in range(1, 29)]

@st.cache_resource
def load_artifacts():
    try:
        model = joblib.load('model.pkl')
        scaler = joblib.load('scaler.pkl')
        with open('threshold.txt', 'r') as f:
            default_threshold = float(f.read().strip())
        return model, scaler, default_threshold
    except Exception as e:
        return None, None, 0.50

model, scaler, default_threshold = load_artifacts()

st.sidebar.title("⚙️ System Controls")
st.sidebar.markdown("### Decision Threshold")
threshold = st.sidebar.slider(
    "Fraud Probability Threshold", 
    min_value=0.01, max_value=0.99, 
    value=default_threshold if default_threshold else 0.50, 
    step=0.01
)

st.title("🛡️ Transaction Risk & Anomaly Detection")
st.markdown("Upload a batch of transactions (CSV) to analyze risk and flag potential fraud anomalies.")

if model is None or scaler is None:
    st.error("🚨 Critical Error: 'model.pkl' or 'scaler.pkl' not found.")
    st.stop()

uploaded_file = st.file_uploader("Upload Transaction Data", type=["csv"])

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)
        
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df_raw.columns]
    if missing_cols:
        st.error(f"🚨 Missing expected columns: {', '.join(missing_cols)}")
        st.stop()
        
    with st.spinner("Analyzing transactions..."):
        df_display = df_raw.copy()
        
        # Feature Engineering to match training data
        df_processed = df_raw.copy()
        df_processed['Hour'] = (df_processed['Time'] // 3600) % 24
        df_processed['Scaled_Amount'] = scaler.transform(df_processed[['Amount']])
        df_processed = df_processed.drop(['Time', 'Amount'], axis=1)
        
        if 'Class' in df_processed.columns:
            df_processed = df_processed.drop('Class', axis=1)
            
        feature_order = [f'V{i}' for i in range(1, 29)] + ['Hour', 'Scaled_Amount']
        X_input = df_processed[feature_order]
        
        # Predictions
        probabilities = model.predict_proba(X_input)[:, 1]
        
        df_display['Fraud_Probability'] = probabilities
        df_display['Risk_Flag'] = (probabilities >= threshold).astype(int)
        df_display['Risk_Level'] = pd.cut(
            df_display['Fraud_Probability'], 
            bins=[-1, 0.3, 0.7, 1.1], 
            labels=['Low', 'Medium', 'High']
        )
        
        total_tx = len(df_display)
        flagged_tx = df_display['Risk_Flag'].sum()
        fraud_rate = (flagged_tx / total_tx) * 100 if total_tx > 0 else 0
        value_at_risk = df_display.loc[df_display['Risk_Flag'] == 1, 'Amount'].sum()

        st.markdown("### 📊 Batch Summary")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Transactions", f"{total_tx:,}")
        c2.metric("Flagged Anomalies", f"{flagged_tx:,}")
        c3.metric("Fraud Rate", f"{fraud_rate:.2f}%")
        c4.metric("Value at Risk", f"${value_at_risk:,.2f}")
        
        st.divider()

        st.markdown("### 📈 Risk Analytics")
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            fig_hist = px.histogram(
                df_display, x="Fraud_Probability", nbins=50, 
                title="Distribution of Fraud Probabilities",
                color="Risk_Level",
                color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'}
            )
            fig_hist.add_vline(x=threshold, line_dash="dash", line_color="black")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col_chart2:
            fig_scatter = px.scatter(
                df_display, x="Amount", y="Fraud_Probability", 
                color="Risk_Flag", title="Transaction Amount vs. Risk Probability",
                color_continuous_scale="Reds"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.divider()

        st.markdown("### 🚨 Suspicious Transactions")
        suspicious_df = df_display[df_display['Risk_Flag'] == 1].sort_values(by="Fraud_Probability", ascending=False)
        
        if not suspicious_df.empty:
            cols = ['Time', 'Amount', 'Fraud_Probability', 'Risk_Level'] + [f'V{i}' for i in range(1, 29)]
            st.dataframe(suspicious_df[cols].style.background_gradient(subset=['Fraud_Probability'], cmap='Reds'), use_container_width=True)
            
            csv_export = suspicious_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Flagged Transactions", csv_export, "flagged_anomalies.csv", "text/csv")
        else:
            st.success("No transactions flagged as high risk under the current threshold.")
else:
    st.info("Awaiting CSV file upload.")