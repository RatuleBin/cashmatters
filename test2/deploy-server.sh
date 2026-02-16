#!/bin/bash

# CashMatters Django Deployment Script for VPS
# This script sets up the entire server environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting CashMatters Deployment...${NC}"

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx curl git ufw

# Setup PostgreSQL
echo -e "${YELLOW}🗄️ Setting up PostgreSQL...${NC}"
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
echo -e "${YELLOW}👤 Creating PostgreSQL database and user...${NC}"
sudo -u postgres psql -c "CREATE DATABASE cashmatters_db;" || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER cashmatters_user WITH PASSWORD 'your_secure_password_here';" || echo "User already exists"
sudo -u postgres psql -c "ALTER ROLE cashmatters_user SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE cashmatters_user SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE cashmatters_user SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cashmatters_db TO cashmatters_user;"

# Create application user
echo -e "${YELLOW}👤 Creating application user...${NC}"
sudo useradd --create-home --shell /bin/bash django || echo "User already exists"
sudo usermod -a -G www-data django

# Setup application directory
echo -e "${YELLOW}📁 Setting up application directory...${NC}"
sudo mkdir -p /home/django/apps
sudo chown django:django /home/django/apps

# Clone or copy application (assuming you're running this from the project directory)
echo -e "${YELLOW}📋 Copying application files...${NC}"
sudo cp -r . /home/django/apps/cashmatters/
sudo chown -R django:django /home/django/apps/cashmatters/

# Setup Python virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
sudo -u django bash -c "cd /home/django/apps/cashmatters && python3 -m venv venv"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && pip install --upgrade pip"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && pip install -r requirements.txt"

# Setup Django
echo -e "${YELLOW}⚙️ Setting up Django...${NC}"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && python manage.py collectstatic --noinput"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && python manage.py migrate"

# Create directories for static/media files
sudo mkdir -p /home/django/apps/cashmatters/staticfiles
sudo mkdir -p /home/django/apps/cashmatters/media
sudo chown -R django:www-data /home/django/apps/cashmatters/staticfiles
sudo chown -R django:www-data /home/django/apps/cashmatters/media

# Setup Gunicorn service
echo -e "${YELLOW}🔧 Setting up Gunicorn service...${NC}"
sudo cp /home/django/apps/cashmatters/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Setup Nginx
echo -e "${YELLOW}🌐 Setting up Nginx...${NC}"
sudo cp /home/django/apps/cashmatters/nginx.conf /etc/nginx/sites-available/cashmatters
sudo ln -sf /etc/nginx/sites-available/cashmatters /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Setup firewall
echo -e "${YELLOW}🔥 Setting up firewall...${NC}"
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Setup SSL with Let's Encrypt (optional)
read -p "Do you want to setup SSL with Let's Encrypt? (y/n): " setup_ssl
if [[ $setup_ssl =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔒 Setting up SSL...${NC}"
    sudo apt install -y certbot python3-certbot-nginx
    echo "Please run: sudo certbot --nginx -d yourdomain.com"
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your site should be available at your server's IP address${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Update ALLOWED_HOSTS in settings/production.py with your domain/IP"
echo "2. Update SECRET_KEY in production settings"
echo "3. Update database password in production settings"
echo "4. Create superuser: cd /home/django/apps/cashmatters && source venv/bin/activate && python manage.py createsuperuser"
echo "5. If using SSL, run: sudo certbot --nginx -d yourdomain.com"