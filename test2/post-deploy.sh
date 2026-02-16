#!/bin/bash

# Post-deployment setup script for CashMatters
# Run this after the main deployment script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 Running post-deployment setup...${NC}"

# Change to application directory
cd /home/django/apps/cashmatters

# Generate a new SECRET_KEY
echo -e "${YELLOW}🔑 Generating new SECRET_KEY...${NC}"
NEW_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Update production settings
echo -e "${YELLOW}⚙️ Updating production settings...${NC}"
sed -i "s/your-production-secret-key-change-this-immediately/$NEW_SECRET_KEY/" cashmatters/settings/production.py

# Prompt for domain/IP
read -p "Enter your domain name or server IP: " SERVER_HOST
sed -i "s/your-domain.com/$SERVER_HOST/g" cashmatters/settings/production.py
sed -i "s/your-server-ip/$SERVER_HOST/g" cashmatters/settings/production.py
sed -i "s/your-domain.com/$SERVER_HOST/g" nginx.conf

# Prompt for database password
read -s -p "Enter your PostgreSQL password: " DB_PASSWORD
echo
sed -i "s/your_secure_db_password_here/$DB_PASSWORD/" cashmatters/settings/production.py

# Update nginx configuration
echo -e "${YELLOW}🌐 Updating nginx configuration...${NC}"
sudo cp nginx.conf /etc/nginx/sites-available/cashmatters
sudo nginx -t && sudo systemctl reload nginx

# Create superuser
echo -e "${YELLOW}👤 Creating Django superuser...${NC}"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && DJANGO_SETTINGS_MODULE=cashmatters.settings.production python manage.py createsuperuser"

# Final setup
echo -e "${YELLOW}🔄 Running final migrations and setup...${NC}"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && DJANGO_SETTINGS_MODULE=cashmatters.settings.production python manage.py migrate"
sudo -u django bash -c "cd /home/django/apps/cashmatters && source venv/bin/activate && DJANGO_SETTINGS_MODULE=cashmatters.settings.production python manage.py collectstatic --noinput"

# Restart services
echo -e "${YELLOW}🔄 Restarting services...${NC}"
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo -e "${GREEN}✅ Post-deployment setup completed!${NC}"
echo -e "${GREEN}🌐 Your site should be available at: http://$SERVER_HOST${NC}"
echo -e "${YELLOW}🔒 Consider setting up SSL with: sudo certbot --nginx -d $SERVER_HOST${NC}"