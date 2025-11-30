import streamlit as st
import os
import pickle
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- GLOBAL VARIABLES FOR MODEL ---
MODEL_PIPELINE = None
ENCODER = None
SCALER = None
MODEL = None

# --- MODEL LOADING FUNCTION ---
@st.cache_resource
def load_model():
    global MODEL_PIPELINE, ENCODER, SCALER, MODEL
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'best_lr_pipeline.pkl')
        with open(model_path, 'rb') as f:
            MODEL_PIPELINE = pickle.load(f)
        
        ENCODER = MODEL_PIPELINE['encoder']   # dict of encoders
        SCALER = MODEL_PIPELINE['scaler']     # numeric scaler
        MODEL = MODEL_PIPELINE['model']       # logistic regression
        
        st.success("Machine Learning Model loaded successfully!")
        return ENCODER, SCALER, MODEL
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

# --- UTILITY FUNCTIONS ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls', 'csv'}

def read_uploaded_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)

def preprocess_data(df, ENCODER, SCALER, MODEL):
    df_processed = df.copy()

    # --- Encode categorical columns ---
    for col, le in ENCODER.items():
        if col in df_processed.columns:
            val = df_processed[col].astype(str)
            df_processed[col] = val.apply(lambda x: x if x in le.classes_ else le.classes_[0])
            df_processed[col] = le.transform(df_processed[col])

    # --- Ensure numeric columns ---
    numeric_cols = SCALER.feature_names_in_.tolist()
    for col in numeric_cols:
        if col not in df_processed.columns:
            raise ValueError(f"Missing numeric column: {col}")
        df_processed[col] = pd.to_numeric(df_processed[col], errors='coerce')
    
    # --- Scale numeric columns ---
    df_processed[numeric_cols] = SCALER.transform(df_processed[numeric_cols])

    # --- Align columns with model ---
    expected_features = MODEL.feature_names_in_.tolist()
    missing_cols = set(expected_features) - set(df_processed.columns)
    if missing_cols:
        raise ValueError(f"Missing features: {missing_cols}")
    df_processed = df_processed[expected_features]
    
    return df_processed

def apply_custom_rules(df):
    """
    Apply your special fraud rules:
    1. Amount > 13500 → Fraud
    2. Amount <= 13500 and Country in ['Morocco', 'Pakistan'] → Fraud
    3. Payment type is 'Check' or 'Credit Card' AND currency in ['MAD', 'PKR', 'AED'] → Fraud
    """
    df_rules = df.copy()
    fraud_flags = np.zeros(len(df_rules), dtype=int)

    for i, row in df_rules.iterrows():
        amount = row.get('Amount', 0)
        country = str(row.get('Country', '')).strip()
        pay_type = str(row.get('PaymentType', '')).strip()
        currency = str(row.get('Currency', '')).strip()

        if amount > 13500:
            fraud_flags[i] = 1
        elif amount <= 13500 and country in ['Morocco', 'Pakistan']:
            fraud_flags[i] = 1
        elif pay_type in ['Check', 'Credit Card'] and currency in ['MAD', 'PKR', 'AED']:
            fraud_flags[i] = 1

    df_rules['Rule_Fraud'] = fraud_flags
    return df_rules

def make_predictions(df_processed, MODEL):
    preds = MODEL.predict(df_processed)
    probs = MODEL.predict_proba(df_processed)
    return preds, probs

def get_download_link(df_results):
    output = BytesIO()
    df_results.to_csv(output, index=False)
    output.seek(0)
    st.download_button(
        label="Download Predictions as CSV",
        data=output,
        file_name=f'predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv'
    )

# --- MAIN APPLICATION ---
def main():
    ENCODER, SCALER, MODEL = load_model()

    st.title("Fraud Detection Dashboard")
    st.markdown("Upload an Excel/CSV file containing transaction data for real-time fraud prediction.")

    uploaded_file = st.file_uploader("Choose a file (.xlsx, .xls, .csv)", type=['xlsx', 'xls', 'csv'])

    if uploaded_file is not None:
        if not allowed_file(uploaded_file.name):
            st.error("File type not allowed. Please use .xlsx, .xls, or .csv.")
            return

        try:
            df = read_uploaded_file(uploaded_file)
            if df.empty:
                st.error("Uploaded file is empty.")
                return
            
            st.subheader("1. Data Preview")
            st.dataframe(df.head())

            if st.button("Run Fraud Prediction"):
                with st.spinner("Processing..."):
                    df_processed = preprocess_data(df, ENCODER, SCALER, MODEL)
                    preds, probs = make_predictions(df_processed, MODEL)

                    df_results = df.copy()
                    df_results['Model_Prediction'] = preds
                    df_results['Fraud_Probability'] = [p[1] for p in probs]
                    df_results['Legit_Probability'] = [p[0] for p in probs]

                    # Apply custom fraud rules
                    df_results = apply_custom_rules(df_results)

                    # Metrics
                    total = len(df_results)
                    fraud_count = df_results['Rule_Fraud'].sum()
                    legit_count = total - fraud_count
                    fraud_percent = (fraud_count / total) * 100 if total else 0

                    st.header("2. Prediction Results")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Records", total)
                    col2.metric("Fraud Cases (Rules)", fraud_count)
                    col3.metric("Fraud Percentage", f"{fraud_percent:.2f}%")

                    st.subheader("Prediction Table")
                    st.dataframe(df_results)

                    st.subheader("Download Results")
                    get_download_link(df_results)

        except Exception as e:
            st.exception(f"Error: {e}")

if __name__ == "__main__":
    main()
