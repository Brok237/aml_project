import streamlit as st
import os
import pickle
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="ML Model Prediction Dashboard",
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
    """
    Load the ML model from the pickle file at application startup.
    Uses st.cache_resource to load the model only once.
    """
    global MODEL_PIPELINE, ENCODER, SCALER, MODEL
    
    try:
        # Model path relative to the Streamlit app file
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'best_lr_pipeline.pkl')
        
        with open(model_path, 'rb') as f:
            MODEL_PIPELINE = pickle.load(f)
        
        # Extract components from the pipeline dictionary
        ENCODER = MODEL_PIPELINE['encoder']
        SCALER = MODEL_PIPELINE['scaler']
        MODEL = MODEL_PIPELINE['model']
        
        st.success("Machine Learning Model loaded successfully!")
        return ENCODER, SCALER, MODEL
        
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

# --- UTILITY FUNCTIONS (Reused from Flask app) ---

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_uploaded_file(file):
    """
    Read uploaded Excel or CSV file and return a pandas DataFrame.
    Handles both .xlsx and .csv formats.
    """
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:  # .xlsx or .xls
            df = pd.read_excel(file)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

def preprocess_data(df, ENCODER, SCALER):
    """
    Preprocess the input data using the loaded encoder and scaler.
    Applies encoding and scaling to match the training pipeline.
    """
    try:
        df_processed = df.copy()
        
        # Identify categorical and numerical columns
        categorical_cols = df_processed.select_dtypes(include=['object']).columns.tolist()
        numerical_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        
        # Encode categorical columns using the loaded encoder
        for col in categorical_cols:
            if col in df_processed.columns:
                try:
                    df_processed[col] = df_processed[col].astype(str)
                    df_processed[col] = ENCODER.transform(df_processed[col])
                except Exception as e:
                    st.warning(f"Warning: Could not encode column {col}: {e}")
        
        # Scale numerical features using the loaded scaler
        scaler_features = SCALER.get_feature_names_out()
        features_to_scale = [col for col in scaler_features if col in df_processed.columns]
        
        if features_to_scale:
            df_processed[features_to_scale] = SCALER.transform(df_processed[features_to_scale])
        
        return df_processed
    
    except Exception as e:
        raise ValueError(f"Error preprocessing data: {str(e)}")

def make_predictions(df_processed, MODEL):
    """
    Make predictions using the loaded Logistic Regression model.
    Returns both class predictions and probability scores.
    """
    try:
        predictions = MODEL.predict(df_processed)
        probabilities = MODEL.predict_proba(df_processed)
        return predictions, probabilities
    
    except Exception as e:
        raise ValueError(f"Error making predictions: {str(e)}")

def get_download_link(df_results):
    """Generates a download link for the prediction results DataFrame."""
    output = BytesIO()
    df_results.to_csv(output, index=False)
    output.seek(0)
    
    # Create a download button
    st.download_button(
        label="Download Predictions as CSV",
        data=output,
        file_name=f'predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv',
        key='download_csv'
    )

# --- MAIN APPLICATION LOGIC ---

def main():
    # Load model components
    ENCODER, SCALER, MODEL = load_model()

    st.title("Fraud Detection Dashboard")
    st.markdown("Upload an Excel or CSV file containing customer data to get real-time fraud predictions.")

    # File Uploader
    uploaded_file = st.file_uploader(
        "Choose a file (.xlsx, .xls, .csv)",
        type=['xlsx', 'xls', 'csv']
    )

    if uploaded_file is not None:
        if not allowed_file(uploaded_file.name):
            st.error("File type not allowed. Please use .xlsx, .xls, or .csv.")
            return

        try:
            # Read the uploaded file
            df = read_uploaded_file(uploaded_file)
            
            if df.empty:
                st.error("Uploaded file is empty.")
                return

            st.subheader("1. Data Preview")
            st.dataframe(df.head())
            st.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns.")

            # Prediction Button
            if st.button("Run Fraud Prediction"):
                with st.spinner("Processing data and generating predictions..."):
                    # Preprocess the data
                    df_processed = preprocess_data(df, ENCODER, SCALER)
                    
                    # Make predictions
                    predictions, probabilities = make_predictions(df_processed, MODEL)
                    
                    # Calculate statistics
                    total_rows = len(predictions)
                    fraud_count = int(np.sum(predictions))
                    legit_count = total_rows - fraud_count
                    fraud_percentage = (fraud_count / total_rows * 100) if total_rows > 0 else 0
                    
                    # Prepare results DataFrame
                    df_results = df.copy()
                    df_results['Prediction'] = predictions
                    df_results['Fraud_Probability'] = [prob[1] for prob in probabilities]
                    df_results['Legit_Probability'] = [prob[0] for prob in probabilities]
                    
                    # Store results in session state
                    st.session_state['results'] = {
                        'total_rows': total_rows,
                        'fraud_count': fraud_count,
                        'legit_count': legit_count,
                        'fraud_percentage': fraud_percentage,
                        'df_results': df_results
                    }
                    st.success(f"Prediction complete! Processed {total_rows} records.")

        except ValueError as e:
            st.error(f"Data Error: {e}")
        except Exception as e:
            st.exception(f"An unexpected error occurred: {e}")

    # Display Results (Dashboard)
    if 'results' in st.session_state:
        results = st.session_state['results']
        df_results = results['df_results']

        st.header("2. Prediction Results Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(label="Total Records Processed", value=results['total_rows'])
        
        with col2:
            st.metric(label="Predicted Fraud Cases", value=results['fraud_count'])
            
        with col3:
            st.metric(label="Fraud Percentage", value=f"{results['fraud_percentage']:.2f}%")

        st.subheader("Predicted Data Table")
        st.dataframe(df_results)
        
        st.subheader("Download Results")
        get_download_link(df_results)

if __name__ == '__main__':
    main()
