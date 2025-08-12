# 🚀 FemboyWorld Production Deployment Guide

## 📋 Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Domain name (optional but recommended)

## 🛠️ Installation

### 1. Install Production Dependencies
```bash
pip install -r requirements-prod.txt
```

### 2. Set Environment Variables
Copy `env.example` to `.env` and configure:
```bash
cp env.example .env
# Edit .env with your production values
```

### 3. Configure Database
For production, use PostgreSQL or MySQL instead of SQLite:

**PostgreSQL:**
```bash
pip install psycopg2-binary
# Set DATABASE_URL in .env
```

**MySQL:**
```bash
pip install mysqlclient
# Set DATABASE_URL in .env
```

## 🚀 Deployment Options

### Option 1: Railway (Recommended for beginners)
1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables in Railway dashboard
4. Deploy automatically

### Option 2: Render
1. Create account at [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Set environment variables
5. Deploy

### Option 3: DigitalOcean App Platform
1. Create account at [digitalocean.com](https://digitalocean.com)
2. Create new App
3. Connect your GitHub repository
4. Configure environment variables
5. Deploy

## 🔧 Environment Variables

Required environment variables:
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://username:password@host/database
UPLOAD_FOLDER=static/uploads
LOG_LEVEL=INFO
```

## 📁 File Structure
```
femboyworld/
├── app.py                 # Main application
├── config.py             # Configuration classes
├── wsgi.py               # Production WSGI entry point
├── gunicorn.conf.py      # Gunicorn configuration
├── requirements-prod.txt  # Production dependencies
├── .env                  # Environment variables (create from env.example)
├── static/               # Static files
│   └── uploads/         # User uploads
├── templates/            # HTML templates
└── logs/                 # Log files (auto-created)
```

## 🚀 Starting Production Server

### Windows:
```bash
start_production.bat
```

### PowerShell:
```powershell
.\start_production.ps1
```

### Manual:
```bash
set FLASK_ENV=production
gunicorn -c gunicorn.conf.py wsgi:app
```

## 🔒 Security Features

- ✅ HTTPS/SSL support
- ✅ Security headers (XSS, CSRF protection)
- ✅ Content Security Policy
- ✅ Secure session cookies
- ✅ File upload validation
- ✅ Error handling without information leakage

## 📊 Monitoring & Logging

- Logs are stored in `logs/` directory
- Gunicorn access and error logs
- Application logs with structured formatting
- Error tracking and monitoring

## 🌐 Domain & SSL

1. **Buy a domain** (Namecheap, GoDaddy, etc.)
2. **Configure DNS** to point to your hosting provider
3. **Enable SSL/HTTPS** (most hosting providers do this automatically)

## 🔄 Updates & Maintenance

1. Pull latest changes from GitHub
2. Install new dependencies: `pip install -r requirements-prod.txt`
3. Restart the server
4. Monitor logs for any issues

## 🆘 Troubleshooting

### Common Issues:
- **Database connection errors**: Check DATABASE_URL in .env
- **File upload failures**: Verify UPLOAD_FOLDER permissions
- **Port conflicts**: Change port in gunicorn.conf.py
- **Memory issues**: Reduce workers in gunicorn.conf.py

### Logs:
Check these files for errors:
- `logs/femboyworld.log` - Application logs
- `logs/gunicorn_error.log` - Server errors
- `logs/gunicorn_access.log` - Access logs

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally with production config
4. Check hosting provider documentation

---

**Happy Deploying! 🎉**
