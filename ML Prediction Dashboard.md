# ML Prediction Dashboard

A complete, production-ready Flask web application for machine learning model predictions. Upload Excel or CSV files, process them with a pre-trained Logistic Regression model, and visualize results in an interactive dashboard.

## 📋 Features

- **Model Integration**: Loads a pre-trained Logistic Regression model with encoder and scaler from a pickle file
- **File Upload**: Support for Excel (.xlsx, .xls) and CSV (.csv) files up to 16 MB
- **Data Processing**: Automatic encoding and scaling of input data
- **Predictions**: Binary classification with probability scores
- **Dashboard**: Interactive charts, statistics, and detailed prediction tables
- **Export**: Download predictions as CSV for further analysis
- **Responsive Design**: Modern UI that works on desktop and mobile devices
- **Error Handling**: Comprehensive error messages and validation

## 🏗️ Project Structure

```
ml_flask_app/
│
├── app.py                          # Flask application backend
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── model/
│   └── best_lr_pipeline.pkl       # Pre-trained ML model (encoder, scaler, model)
│
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── index.html                 # Home page with upload form
│   └── dashboard.html             # Results dashboard with charts
│
├── static/
│   ├── style.css                  # Main stylesheet (responsive design)
│   └── script.js                  # JavaScript utilities and interactivity
│
└── uploads/                        # Directory for uploaded files (auto-created)
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Clone or Download the Project

```bash
# Navigate to the project directory
cd ml_flask_app
```

### Step 2: Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install required packages
pip install flask pandas scikit-learn openpyxl
```

Alternatively, use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 4: Verify Model File

Ensure the pickle file is in the correct location:

```bash
ls -la model/best_lr_pipeline.pkl
```

The pickle file should contain:
- `encoder`: LabelEncoder for categorical features
- `scaler`: StandardScaler for numerical features
- `model`: LogisticRegression for predictions

## 🚀 Running the Application

### Development Mode

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Linux/macOS

# Run the Flask development server
python3 app.py
```

The application will start at `http://localhost:5000`

### Production Mode

For production deployment, use a production WSGI server:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Or use other WSGI servers like uWSGI, Waitress, etc.

## 📖 Usage Guide

### 1. Home Page (`/`)

- **Upload Form**: Drag and drop or click to select a file
- **Supported Formats**: Excel (.xlsx, .xls) or CSV (.csv)
- **File Size Limit**: 16 MB maximum
- **Submit**: Click "Analyze Data" to process the file

### 2. Data Format Requirements

Your input file should contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Amount | Numeric | Transaction amount |
| avg_amount_per_customer | Numeric | Average amount per customer |
| amount_ratio | Numeric | Ratio of amounts |
| category | Categorical | Category code (0-27) |

**Example CSV:**

```csv
Amount,avg_amount_per_customer,amount_ratio,category
500.50,250.25,2.0,1
1000.00,500.00,2.0,5
250.75,125.50,2.0,3
```

### 3. Dashboard (`/dashboard`)

After uploading a file, you'll be redirected to the dashboard showing:

- **Summary Cards**: Total records, fraud count, legitimate count, model status
- **Pie Chart**: Distribution of fraud vs. legitimate cases
- **Bar Chart**: Statistical comparison
- **Results Table**: Detailed predictions with probabilities and confidence scores
- **Pagination**: Navigate through large result sets
- **Export**: Download predictions as CSV

### 4. API Endpoints

#### Health Check
```
GET /api/health
```
Returns the application status and model state.

#### Make Predictions
```
POST /api/predict
Content-Type: multipart/form-data

Parameters:
- file: The uploaded Excel or CSV file
```

Response:
```json
{
  "success": true,
  "total_rows": 50,
  "fraud_count": 5,
  "legit_count": 45,
  "fraud_percentage": 10.0,
  "predictions": [0, 1, 0, ...],
  "probabilities": [[0.8, 0.2], [0.3, 0.7], ...],
  "message": "Successfully processed 50 records"
}
```

#### Get Predictions
```
GET /api/predictions
```
Retrieves the last set of predictions.

#### Download Predictions
```
GET /api/download-predictions
```
Downloads predictions as a CSV file.

## 🎨 Customization

### Change the Model

To use a different model:

1. Replace `model/best_lr_pipeline.pkl` with your new model file
2. Ensure it's a dictionary with keys: `encoder`, `scaler`, `model`
3. Restart the Flask application

### Modify the UI

- **Colors**: Edit the CSS variables in `static/style.css` (`:root` section)
- **Layout**: Modify HTML templates in `templates/` directory
- **Charts**: Customize Chart.js configuration in `templates/dashboard.html`

### Update Feature Names

If your model uses different feature names:

1. Edit the preprocessing logic in `app.py` (function `preprocess_data`)
2. Update the expected column names in the comments
3. Modify the input validation accordingly

## 🔐 Security Considerations

### For Production Deployment

1. **Set `debug=False`** in `app.py`
2. **Use environment variables** for sensitive configuration
3. **Implement authentication** if needed
4. **Validate file uploads** (already done, but review for your use case)
5. **Use HTTPS** with a reverse proxy (nginx, Apache)
6. **Set file size limits** appropriately
7. **Implement rate limiting** to prevent abuse
8. **Use a production WSGI server** (Gunicorn, uWSGI)

### Example Production Configuration

```python
# In app.py, before running:
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['UPLOAD_FOLDER'] = '/var/tmp/uploads'
app.run(debug=False, host='127.0.0.1', port=5000)
```

## 📊 Model Details

The pre-trained model includes:

- **Encoder**: LabelEncoder with 28 classes for categorical features
- **Scaler**: StandardScaler for normalizing numerical features
- **Model**: LogisticRegression for binary classification (0 = Legitimate, 1 = Fraud)

### Prediction Output

- **Prediction**: 0 (Legitimate) or 1 (Fraud)
- **Probabilities**: [P(Legitimate), P(Fraud)]
- **Confidence**: Maximum probability value

## 🐛 Troubleshooting

### Issue: "Model not found" error

**Solution**: Ensure the pickle file is in `model/best_lr_pipeline.pkl`

```bash
ls -la model/best_lr_pipeline.pkl
```

### Issue: "No module named 'sklearn'"

**Solution**: Install scikit-learn

```bash
pip install scikit-learn
```

### Issue: Port 5000 already in use

**Solution**: Use a different port

```bash
python3 app.py  # Then modify app.run(port=5001)
```

Or kill the process using port 5000:

```bash
# On Linux/macOS:
lsof -i :5000
kill -9 <PID>

# On Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: File upload fails

**Solution**: Check file format and size

- Ensure file is .xlsx, .xls, or .csv
- File size must be less than 16 MB
- File should have required columns

### Issue: Predictions not showing

**Solution**: Check the browser console for errors

- Open Developer Tools (F12)
- Check the Console tab for JavaScript errors
- Check the Network tab to see API responses

## 📈 Performance Optimization

### For Large Files

1. **Increase timeout** in production server configuration
2. **Use async processing** for very large datasets
3. **Implement batch processing** if needed

### For Multiple Users

1. **Use a production WSGI server** with multiple workers
2. **Implement caching** for model predictions
3. **Use a database** to store prediction history
4. **Implement queue system** (Celery) for background processing

## 📝 Example Workflow

1. **Prepare Data**: Create a CSV or Excel file with required columns
2. **Upload**: Go to `http://localhost:5000/` and upload the file
3. **View Results**: Dashboard automatically loads with predictions
4. **Analyze**: Review charts, statistics, and detailed predictions
5. **Export**: Download results as CSV for further analysis

## 🔄 Model Replacement Guide

To use a different ML model:

### Step 1: Prepare Your Model

Ensure your model is saved as a pickle file with this structure:

```python
pipeline = {
    'encoder': your_label_encoder,      # For categorical features
    'scaler': your_standard_scaler,     # For numerical features
    'model': your_trained_model         # Any sklearn model
}

import pickle
with open('best_lr_pipeline.pkl', 'wb') as f:
    pickle.dump(pipeline, f)
```

### Step 2: Update Feature Mapping

Edit `app.py` and update the `preprocess_data()` function:

```python
def preprocess_data(df):
    # Update feature names to match your model
    scaler_features = ['feature1', 'feature2', 'feature3']
    # ... rest of the function
```

### Step 3: Replace the Model File

```bash
cp your_model.pkl model/best_lr_pipeline.pkl
```

### Step 4: Test

Upload a sample file and verify predictions work correctly.

## 📞 Support & Maintenance

### Regular Maintenance

- Monitor error logs
- Update dependencies periodically
- Backup prediction history
- Review model performance

### Model Monitoring

- Track prediction accuracy
- Monitor fraud detection rate
- Analyze false positives/negatives
- Retrain model periodically

## 📄 License

This project is provided as-is for educational and commercial use.

## 🎯 Future Enhancements

Potential improvements:

- [ ] User authentication and authorization
- [ ] Prediction history database
- [ ] Model performance metrics dashboard
- [ ] Batch processing for large files
- [ ] API key authentication
- [ ] Webhook notifications
- [ ] Model versioning
- [ ] A/B testing framework
- [ ] Real-time prediction streaming
- [ ] Advanced visualization options

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Chart.js Documentation](https://www.chartjs.org/)

---

**Created**: 2024
**Version**: 1.0
**Status**: Production Ready
