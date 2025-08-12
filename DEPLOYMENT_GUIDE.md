# 🚀 FemboyWorld Deployment Guide

## 🌐 Domain: femboyworld.online

This guide will help you deploy FemboyWorld to your new domain with proper production settings.

## 📋 Prerequisites

- Domain: `femboyworld.online` ✅
- Web hosting service (VPS, shared hosting, or cloud platform)
- SSL certificate (HTTPS)
- Python 3.8+ support
- Database service (PostgreSQL recommended for production)

## 🏗️ Deployment Options

### **Option 1: VPS/Cloud Server (Recommended)**

#### **1.1 Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib
```

#### **1.2 Application Setup**
```bash
# Create application directory
sudo mkdir -p /var/www/femboyworld
sudo chown $USER:$USER /var/www/femboyworld
cd /var/www/femboyworld

# Clone your repository or upload files
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn
```

#### **1.3 Environment Configuration**
```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=postgresql://username:password@localhost/femboyworld
EOF
```

#### **1.4 Database Setup**
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE femboyworld;
CREATE USER femboyworld_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE femboyworld TO femboyworld_user;
\q

# Run migrations
python migrate_db.py
```

#### **1.5 Gunicorn Service**
```bash
# Create systemd service
sudo tee /etc/systemd/system/femboyworld.service > /dev/null << EOF
[Unit]
Description=FemboyWorld Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/femboyworld
Environment="PATH=/var/www/femboyworld/venv/bin"
ExecStart=/var/www/femboyworld/venv/bin/gunicorn --workers 3 --bind unix:/var/www/femboyworld/femboyworld.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl start femboyworld
sudo systemctl enable femboyworld
```

#### **1.6 Nginx Configuration**
```bash
# Create Nginx site configuration
sudo tee /etc/nginx/sites-available/femboyworld.online > /dev/null << EOF
server {
    listen 80;
    server_name femboyworld.online www.femboyworld.online;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name femboyworld.online www.femboyworld.online;
    
    # SSL Configuration (update paths)
    ssl_certificate /etc/letsencrypt/live/femboyworld.online/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/femboyworld.online/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Static files
    location /static/ {
        alias /var/www/femboyworld/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Uploads
    location /static/uploads/ {
        alias /var/www/femboyworld/static/uploads/;
        expires 7d;
    }
    
    # Proxy to Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/femboyworld/femboyworld.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/femboyworld.online /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **1.7 SSL Certificate (Let's Encrypt)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d femboyworld.online -d www.femboyworld.online

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Option 2: Shared Hosting**

#### **2.1 File Upload**
- Upload all project files to your hosting directory
- Ensure `static/uploads/` directory is writable
- Update `.htaccess` for URL rewriting if needed

#### **2.2 Configuration**
- Set `FLASK_ENV=production` in environment
- Update database connection string
- Ensure proper file permissions

### **Option 3: Cloud Platforms**

#### **3.1 Heroku**
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Deploy
heroku create femboyworld-online
git push heroku main
```

#### **3.2 DigitalOcean App Platform**
- Connect your GitHub repository
- Set environment variables
- Configure domain

#### **3.3 AWS/GCP/Azure**
- Use their respective deployment services
- Configure load balancers and auto-scaling
- Set up managed databases

## 🔧 Production Configuration

### **Environment Variables**
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key
DATABASE_URL=postgresql://user:pass@host/db
UPLOAD_FOLDER=/var/www/femboyworld/static/uploads
MAX_CONTENT_LENGTH=16777216
```

### **Security Checklist**
- [ ] HTTPS enabled
- [ ] Strong SECRET_KEY
- [ ] Database credentials secured
- [ ] File upload restrictions
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] Regular backups scheduled

## 📊 Monitoring & Maintenance

### **Logs**
```bash
# Application logs
sudo journalctl -u femboyworld -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### **Backups**
```bash
# Database backup
pg_dump femboyworld > backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf uploads_$(date +%Y%m%d_%H%M%S).tar.gz static/uploads/
```

### **Updates**
```bash
# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart femboyworld
```

## 🚨 Troubleshooting

### **Common Issues**
1. **500 Errors**: Check logs, database connection
2. **Static files not loading**: Verify Nginx configuration
3. **Upload failures**: Check directory permissions
4. **Database errors**: Verify connection string and credentials

### **Performance Optimization**
- Enable Gunicorn worker processes
- Configure Nginx caching
- Use CDN for static assets
- Database query optimization
- Image compression

## 🌟 Next Steps

1. **Choose deployment option** based on your needs
2. **Set up hosting environment**
3. **Configure domain DNS** to point to your server
4. **Deploy application** following the guide
5. **Test thoroughly** before going live
6. **Monitor performance** and user feedback

## 📞 Support

- Check logs for error details
- Review this deployment guide
- Consult hosting provider documentation
- Open issues on the project repository

---

**Good luck with your deployment! 🚀**

Your platform will be accessible at: `https://femboyworld.online`
