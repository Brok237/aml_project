
import os
import pickle
import json
from datetime import datetime
from io import BytesIO
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename



app = Flask(__name__)


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'xlsx', 'csv', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


MODEL_PIPELINE = None
ENCODERS = None
SCALER = None
MODEL = None
LAST_PREDICTIONS = None

def load_model():
    
    global MODEL_PIPELINE, ENCODERS, SCALER, MODEL
    
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'model', 'best_lr_pipeline.pkl')
        
        with open(model_path, 'rb') as f:
            MODEL_PIPELINE = pickle.load(f)
        
        
        ENCODERS = MODEL_PIPELINE['encoder']
        SCALER = MODEL_PIPELINE['scaler']
        MODEL = MODEL_PIPELINE['model']
        
        print("✓ Model loaded successfully!")
        print("  - Encoders loaded for columns:", list(ENCODERS.keys()))
        print("  - Scaler features:", SCALER.get_feature_names_out())
        print("  - Model classes:", MODEL.classes_)


        
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        raise


def allowed_file(filename):
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_uploaded_file(file):

    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:  
            df = pd.read_excel(file)
        
        return df
    
    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")

def preprocess_data(df):

    try:
        df_processed = df.copy()

       
        for col, le in ENCODERS.items():
            if col in df_processed.columns:
                df_processed[col] = le.transform(df_processed[col].astype(str))

        
        numeric_cols = SCALER.feature_names_in_.tolist()  
        df_processed[numeric_cols] = SCALER.transform(df_processed[numeric_cols])

        return df_processed

    except Exception as e:
        raise ValueError(f"Error preprocessing data: {str(e)}")


def make_predictions(df_processed):

    try:
     
        predictions = MODEL.predict(df_processed)
        
        
        probabilities = MODEL.predict_proba(df_processed)
        
        return predictions, probabilities
    
    except Exception as e:
        raise ValueError(f"Error making predictions: {str(e)}")


@app.route('/')
def index():
  
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    
    return render_template('dashboard.html')

@app.route('/api/predict', methods=['POST'])
def predict():
   
    global LAST_PREDICTIONS
    
    try:
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use .xlsx, .xls, or .csv'}), 400
        
       
        df = read_uploaded_file(file)
        
        
        if df.empty:
            return jsonify({'error': 'Uploaded file is empty'}), 400
        
        
        df_processed = preprocess_data(df)
        
        
        predictions, probabilities = make_predictions(df_processed)
        
        
        LAST_PREDICTIONS = {
            'original_data': df.to_dict('records'),
            'predictions': predictions.tolist(),
            'probabilities': probabilities.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        
        total_rows = len(predictions)
        fraud_count = int(np.sum(predictions))
        legit_count = total_rows - fraud_count
        fraud_percentage = (fraud_count / total_rows * 100) if total_rows > 0 else 0
        
        
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
  
    global LAST_PREDICTIONS
    
    if LAST_PREDICTIONS is None:
        return jsonify({'error': 'No predictions available'}), 404
    
    return jsonify(LAST_PREDICTIONS), 200

@app.route('/api/download-predictions', methods=['GET'])
def download_predictions():
 
    global LAST_PREDICTIONS
    
    try:
        if LAST_PREDICTIONS is None:
            return jsonify({'error': 'No predictions available'}), 404
        
      
        df_results = pd.DataFrame(LAST_PREDICTIONS['original_data'])
        df_results['Prediction'] = LAST_PREDICTIONS['predictions']
        df_results['Fraud_Probability'] = [prob[1] for prob in LAST_PREDICTIONS['probabilities']]
        df_results['Legit_Probability'] = [prob[0] for prob in LAST_PREDICTIONS['probabilities']]
        
       
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
 
    return jsonify({
        'status': 'healthy',
        'model_loaded': MODEL is not None,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
   
    load_model()
    

    app.run(debug=True, host='0.0.0.0', port=5000)
