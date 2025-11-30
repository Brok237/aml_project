# Quick Start Guide

Get the ML Prediction Dashboard running in 5 minutes!

## 🚀 Quick Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python3 app.py
```

### 4. Open in Browser

Navigate to: **http://localhost:5000**

## 📤 Upload Your Data

### Supported Formats
- Excel files (.xlsx, .xls)
- CSV files (.csv)
- Maximum size: 16 MB

### Required Columns

Your file must contain these columns:

```
Amount                  (numeric)
avg_amount_per_customer (numeric)
amount_ratio            (numeric)
category                (categorical, 0-27)
```

### Example CSV

```csv
Amount,avg_amount_per_customer,amount_ratio,category
500.50,250.25,2.0,1
1000.00,500.00,2.0,5
250.75,125.50,2.0,3
```

## 📊 View Results

After upload, you'll see:

1. **Summary Cards**: Total records, fraud count, statistics
2. **Charts**: Pie chart and bar chart visualization
3. **Results Table**: Detailed predictions with probabilities
4. **Export**: Download as CSV

## 🔧 Common Commands

### Stop the Server
```bash
Ctrl + C
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Run on Different Port
Edit `app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=8000)
```

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "No module named 'flask'" | Run: `pip install -r requirements.txt` |
| "Port 5000 already in use" | Change port in `app.py` or kill process: `lsof -i :5000` |
| "Model not found" | Check: `ls model/best_lr_pipeline.pkl` |
| "Upload fails" | Verify file format and column names |

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Customize colors in `static/style.css`
- Modify templates in `templates/` directory
- Deploy to production using Gunicorn

## 🎯 API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Upload file and predict
curl -X POST -F "file=@data.csv" http://localhost:5000/api/predict

# Get last predictions
curl http://localhost:5000/api/predictions

# Download predictions as CSV
curl http://localhost:5000/api/download-predictions > predictions.csv
```

## 💡 Tips

- Use the test_data.csv file to test the application
- Check browser console (F12) for any errors
- Review Flask logs for detailed error messages
- Monitor the uploads/ directory for temporary files

---

**Need help?** Check the full [README.md](README.md) for comprehensive documentation.
