# Deployment Guide

Complete guide for deploying the ML Prediction Dashboard to production.

## 🌐 Deployment Options

### Option 1: Heroku Deployment

#### Step 1: Create Heroku Account
- Sign up at [heroku.com](https://www.heroku.com)
- Install Heroku CLI

#### Step 2: Create Procfile

```bash
cat > Procfile << 'PROCFILE'
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
PROCFILE
```

#### Step 3: Create .gitignore

```bash
cat > .gitignore << 'GITIGNORE'
venv/
__pycache__/
*.pyc
.env
uploads/
*.log
.DS_Store
GITIGNORE
```

#### Step 4: Deploy

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main
```

### Option 2: AWS Deployment

#### Using EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 LTS
   - Configure security groups (allow ports 80, 443, 22)

2. **Connect and Setup**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3 python3-pip python3-venv

# Clone/upload your project
git clone your-repo-url
cd ml_flask_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

3. **Create Systemd Service**

```bash
sudo cat > /etc/systemd/system/ml-dashboard.service << 'SERVICE'
[Unit]
Description=ML Prediction Dashboard
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ml_flask_app
ExecStart=/home/ubuntu/ml_flask_app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ml-dashboard
sudo systemctl start ml-dashboard
```

4. **Setup Nginx Reverse Proxy**

```bash
sudo apt install -y nginx

sudo cat > /etc/nginx/sites-available/ml-dashboard << 'NGINX'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/ml_flask_app/static;
    }
}
NGINX

# Enable site
sudo ln -s /etc/nginx/sites-available/ml-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

5. **Setup SSL with Let's Encrypt**

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Option 3: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### Create .dockerignore

```
venv/
__pycache__/
*.pyc
.env
uploads/
*.log
.git
.gitignore
```

#### Build and Run

```bash
# Build image
docker build -t ml-dashboard:latest .

# Run container
docker run -p 5000:5000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/model:/app/model \
  ml-dashboard:latest
```

#### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./uploads:/app/uploads
      - ./model:/app/model
    environment:
      - FLASK_ENV=production
    restart: always
```

Run with: `docker-compose up -d`

### Option 4: DigitalOcean App Platform

1. **Push to GitHub**
   - Create GitHub repository
   - Push your code

2. **Connect to DigitalOcean**
   - Go to App Platform
   - Connect GitHub repository
   - Select Python environment
   - Configure port 5000

3. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

## 🔒 Production Checklist

- [ ] Set `debug=False` in Flask
- [ ] Use environment variables for configuration
- [ ] Enable HTTPS/SSL certificate
- [ ] Setup database for prediction history
- [ ] Configure logging and monitoring
- [ ] Setup error tracking (Sentry)
- [ ] Implement rate limiting
- [ ] Setup backup strategy
- [ ] Configure CDN for static files
- [ ] Setup monitoring and alerts
- [ ] Document deployment process
- [ ] Test disaster recovery

## 📊 Monitoring

### Application Monitoring

```bash
# Install monitoring tools
pip install prometheus-flask-exporter
```

### Log Aggregation

```bash
# Using ELK Stack or similar
# Configure Flask logging to send to centralized service
```

### Performance Monitoring

- Setup New Relic or DataDog
- Monitor response times
- Track error rates
- Monitor resource usage

## 🔄 Continuous Deployment

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh user@your-server.com 'cd /app && git pull && systemctl restart ml-dashboard'
```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer Setup**
   - Use Nginx or HAProxy
   - Route traffic to multiple instances

2. **Database Scaling**
   - Use managed database service
   - Enable read replicas

3. **Caching**
   - Implement Redis for caching
   - Cache predictions for common inputs

### Vertical Scaling

- Increase server resources (CPU, RAM)
- Optimize code and queries
- Use faster storage

## 🚨 Troubleshooting

### Issue: Application won't start

```bash
# Check logs
journalctl -u ml-dashboard -n 50

# Verify dependencies
pip install -r requirements.txt

# Test locally
python3 app.py
```

### Issue: High memory usage

- Reduce worker count
- Implement caching
- Profile application

### Issue: Slow predictions

- Optimize model
- Implement prediction caching
- Use async processing

## 📞 Support

For deployment issues:
1. Check application logs
2. Review Flask documentation
3. Check Gunicorn documentation
4. Review web server configuration

---

**Last Updated**: 2024
**Version**: 1.0
