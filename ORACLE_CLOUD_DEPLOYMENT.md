# 🚀 FemboyWorld on Oracle Cloud Free Tier

## 🌐 Domain: femboyworld.online

This guide will help you deploy FemboyWorld to Oracle Cloud Free Tier for FREE!

## 📋 Prerequisites

- Oracle Cloud account (free tier)
- Domain: `femboyworld.online` ✅
- Credit card for verification (won't be charged)

## 🆓 Oracle Cloud Free Tier Setup

### **Step 1: Create Oracle Cloud Account**
1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Start for free"
3. Choose "Always Free" option
4. Complete registration with credit card verification

### **Step 2: Create VM Instance**
1. **Compute** → **Instances** → **Create Instance**
2. **Name**: `femboyworld-server`
3. **Image**: Canonical Ubuntu 22.04
4. **Shape**: VM.Standard.A1.Flex (Always Free)
5. **Memory**: 6 GB
6. **OCPU**: 1
7. **Network**: Create new VCN with public subnet
8. **Public IP**: Yes
9. **SSH Key**: Generate new key pair

### **Step 3: Connect to Your Server**
```bash
# Download your private key and connect
ssh -i your-key.pem ubuntu@YOUR_SERVER_IP
```

## 🏗️ Application Deployment

### **Step 4: Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx
```

### **Step 5: Setup Application**
```bash
# Create app directory
sudo mkdir -p /var/www/femboyworld
sudo chown ubuntu:ubuntu /var/www/femboyworld
cd /var/www/femboyworld

# Clone your repository or upload files
# (You'll need to upload your project files)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### **Step 6: Database Setup**
```bash
# Create database
sudo -u postgres psql
CREATE DATABASE femboyworld;
CREATE USER femboyworld_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE femboyworld TO femboyworld_user;
\q

# Run migrations
python migrate_db.py
```

### **Step 7: Gunicorn Service**
```bash
# Create systemd service
sudo tee /etc/systemd/system/femboyworld.service > /dev/null << EOF
[Unit]
Description=FemboyWorld Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/femboyworld
Environment="PATH=/var/www/femboyworld/venv/bin"
ExecStart=/var/www/femboyworld/venv/bin/gunicorn --workers 2 --bind unix:/var/www/femboyworld/femboyworld.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl start femboyworld
sudo systemctl enable femboyworld
```

### **Step 8: Nginx Configuration**
```bash
# Create Nginx site configuration
sudo tee /etc/nginx/sites-available/femboyworld.online > /dev/null << EOF
server {
    listen 80;
    server_name femboyworld.online www.femboyworld.online;
    
    location /static/ {
        alias /var/www/femboyworld/static/;
        expires 30d;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/femboyworld/femboyworld.sock;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/femboyworld.online /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **Step 9: SSL Certificate**
```bash
# Get SSL certificate
sudo certbot --nginx -d femboyworld.online -d www.femboyworld.online

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔧 Environment Configuration

Create `.env` file in `/var/www/femboyworld/`:
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-production-key-here
DATABASE_URL=postgresql://femboyworld_user:your_secure_password@localhost/femboyworld
```

## 📊 Monitoring

```bash
# Check service status
sudo systemctl status femboyworld

# View logs
sudo journalctl -u femboyworld -f

# Check Nginx
sudo systemctl status nginx
```

## 🚨 Troubleshooting

### **Common Issues:**
1. **Port 80/443 blocked**: Check Oracle Cloud security lists
2. **Permission denied**: Ensure proper file ownership
3. **Database connection**: Verify PostgreSQL is running

### **Security List Configuration:**
1. **Networking** → **Virtual Cloud Networks**
2. **Security Lists** → **Default Security List**
3. **Ingress Rules** → **Add Ingress Rules**:
   - Port: 80, Source: 0.0.0.0/0
   - Port: 443, Source: 0.0.0.0/0
   - Port: 22, Source: 0.0.0.0/0 (SSH)

## 💰 Cost Breakdown

- **VM Instance**: FREE (Always Free Tier)
- **Storage**: FREE (200 GB included)
- **Network**: FREE (10 TB/month included)
- **SSL Certificate**: FREE (Let's Encrypt)
- **Total Cost**: $0/month! 🎉

## 🌟 Benefits of Oracle Cloud Free Tier

- ✅ **Always Free** - No expiration
- ✅ **1 GB RAM** - Perfect for FemboyWorld
- ✅ **200 GB Storage** - Plenty for uploads
- ✅ **Global CDN** - Fast worldwide access
- ✅ **Professional Infrastructure** - Enterprise-grade reliability

---

**Your FemboyWorld will be live at: `https://femboyworld.online`**

**Total cost: $0/month! 🚀**
