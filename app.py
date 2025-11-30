"""
Flask Application for ML Model Prediction Dashboard
Loads a pre-trained Logistic Regression model with encoder and scaler from a pickle file.
Handles Excel/CSV uploads, processes data, and displays predictions in a dashboard.
"""

import os
import pickle
import json
from datetime import datetime
from io import BytesIO
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# ============================================================================
# GLOBAL VARIABLES FOR MODEL
# ============================================================================

# These will be loaded once at app startup
MODEL_PIPELINE = None
ENCODER = None
SCALER = None
MODEL = None
LAST_PREDICTIONS = None

# ============================================================================
# MODEL LOADING FUNCTION
# ============================================================================

def load_model():
    """
    Load the ML model from the pickle file at application startup.
    This function is called once when the app starts to avoid repeated loading.
    """
    global MODEL_PIPELINE, ENCODER, SCALER, MODEL
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'best_lr_pipeline.pkl')
        
        with open(model_path, 'rb') as f:
            MODEL_PIPELINE = pickle.load(f)
        
        # Extract components from the pipeline dictionary
        ENCODER = MODEL_PIPELINE['encoder']
        SCALER = MODEL_PIPELINE['scaler']
        MODEL = MODEL_PIPELINE['model']
        
        print("✓ Model loaded successfully!")
        print(f"  - Encoder classes: {len(ENCODER.classes_)}")
        print(f"  - Scaler features: {SCALER.get_feature_names_out()}")
        print(f"  - Model classes: {MODEL.classes_}")
        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_uploaded_file(file):
    """
    Read uploaded Excel or CSV file and return a pandas DataFrame.
    Handles both .xlsx and .csv formats.
    """
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:  # .xlsx or .xls
            df = pd.read_excel(file)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

def preprocess_data(df):
    """
    Preprocess the input data using the loaded encoder and scaler.
    Applies encoding and scaling to match the training pipeline.
    """
    try:
        # Make a copy to avoid modifying the original
        df_processed = df.copy()
        
        # Identify categorical and numerical columns
        categorical_cols = df_processed.select_dtypes(include=['object']).columns.tolist()
        numerical_cols = df_processed.select_dtypes(include=[np.number]).columns.tolist()
        
        # Encode categorical columns using the loaded encoder
        for col in categorical_cols:
            if col in df_processed.columns:
                try:
                    # Convert to string to match encoder training
                    df_processed[col] = df_processed[col].astype(str)
                    df_processed[col] = ENCODER.transform(df_processed[col])
                except Exception as e:
                    print(f"Warning: Could not encode column {col}: {e}")
        
        # Scale numerical features using the loaded scaler
        # The scaler expects specific feature names: ['Amount', 'avg_amount_per_customer', 'amount_ratio']
        scaler_features = SCALER.get_feature_names_out()
        
        # Select only the features that the scaler expects
        features_to_scale = [col for col in scaler_features if col in df_processed.columns]
        
        if features_to_scale:
            df_processed[features_to_scale] = SCALER.transform(df_processed[features_to_scale])
        
        return df_processed
    
    except Exception as e:
        raise ValueError(f"Error preprocessing data: {str(e)}")

def make_predictions(df_processed):
    """
    Make predictions using the loaded Logistic Regression model.
    Returns both class predictions and probability scores.
    """
    try:
        # Get predictions (0 or 1)
        predictions = MODEL.predict(df_processed)
        
        # Get probability scores for both classes
        probabilities = MODEL.predict_proba(df_processed)
        
        return predictions, probabilities
    
    except Exception as e:
        raise ValueError(f"Error making predictions: {str(e)}")

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the home page with upload form."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page with prediction results."""
    return render_template('dashboard.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    API endpoint to handle file upload, preprocessing, and prediction.
    Expects a multipart form with a file field.
    Returns JSON with predictions and statistics.
    """
    global LAST_PREDICTIONS
    
    try:
        # Check if file is present in the request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use .xlsx, .xls, or .csv'}), 400
        
        # Read the uploaded file
        df = read_uploaded_file(file)
        
        # Check if dataframe is empty
        if df.empty:
            return jsonify({'error': 'Uploaded file is empty'}), 400
        
        # Preprocess the data
        df_processed = preprocess_data(df)
        
        # Make predictions
        predictions, probabilities = make_predictions(df_processed)
        
        # Store predictions for dashboard
        LAST_PREDICTIONS = {
            'original_data': df.to_dict('records'),
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Calculate statistics
        total_rows = len(predictions)
        fraud_count = int(np.sum(predictions))
        legit_count = total_rows - fraud_count
        fraud_percentage = (fraud_count / total_rows * 100) if total_rows > 0 else 0
        
        # Prepare response
        response = {
            'success': True,
            'total_rows': total_rows,
            'fraud_count': fraud_count,
            'legit_count': legit_count,
            'fraud_percentage': round(fraud_percentage, 2),
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'message': f'Successfully processed {total_rows} records'
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error in /api/predict: {e}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    """
    API endpoint to retrieve the last predictions.
    Used by the dashboard to display results.
    """
    global LAST_PREDICTIONS
    
    if LAST_PREDICTIONS is None:
        return jsonify({'error': 'No predictions available'}), 404
    
    return jsonify(LAST_PREDICTIONS), 200

@app.route('/api/download-predictions', methods=['GET'])
def download_predictions():
    """
    API endpoint to download predictions as a CSV file.
    """
    global LAST_PREDICTIONS
    
    try:
        if LAST_PREDICTIONS is None:
            return jsonify({'error': 'No predictions available'}), 404
        
        # Create a DataFrame with predictions
        df_results = pd.DataFrame(LAST_PREDICTIONS['original_data'])
        df_results['Prediction'] = LAST_PREDICTIONS['predictions']
        df_results['Fraud_Probability'] = [prob[1] for prob in LAST_PREDICTIONS['probabilities']]
        df_results['Legit_Probability'] = [prob[0] for prob in LAST_PREDICTIONS['probabilities']]
        
        # Create CSV in memory
        output = BytesIO()
        df_results.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    
    except Exception as e:
        print(f"Error downloading predictions: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the app is running and model is loaded."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL is not None,
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    # Load the model at startup
    load_model()
    
    # Run the Flask development server
    # Set debug=False for production
    app.run(debug=True, host='0.0.0.0', port=5000)
