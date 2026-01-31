#!/bin/bash

# SSL Certificate Setup Script for CashMatters Docker Deployment
# Run this on your server to obtain SSL certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔒 Setting up SSL certificates for CashMatters...${NC}"

# Install certbot if not already installed
echo -e "${YELLOW}📦 Installing certbot...${NC}"
sudo apt update
sudo apt install -y certbot

# Stop nginx if it's running (to free up port 80)
echo -e "${YELLOW}🛑 Stopping nginx temporarily...${NC}"
sudo systemctl stop nginx 2>/dev/null || echo "nginx not running"

# Obtain SSL certificate
echo -e "${YELLOW}🔐 Obtaining SSL certificate from Let's Encrypt...${NC}"
sudo certbot certonly --standalone -d cashmatters.org -d www.cashmatters.org

# Set proper permissions for Docker access
echo -e "${YELLOW}🔐 Setting certificate permissions...${NC}"
sudo chmod 755 /etc/letsencrypt
sudo chmod 755 /etc/letsencrypt/live
sudo chmod 755 /etc/letsencrypt/archive
sudo chmod 644 /etc/letsencrypt/live/cashmatters.org/fullchain.pem
sudo chmod 644 /etc/letsencrypt/live/cashmatters.org/privkey.pem

# Restart nginx if it was running
echo -e "${YELLOW}🚀 Restarting services...${NC}"
sudo systemctl start nginx 2>/dev/null || echo "nginx not restarted"

echo -e "${GREEN}✅ SSL certificates obtained successfully!${NC}"
echo -e "${YELLOW}📝 Certificate details:${NC}"
echo "  Certificate: /etc/letsencrypt/live/cashmatters.org/fullchain.pem"
echo "  Private Key: /etc/letsencrypt/live/cashmatters.org/privkey.pem"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Deploy your application with: git push origin main"
echo "2. Test HTTPS at: https://cashmatters.org"
echo ""
echo -e "${YELLOW}🔄 Certificate renewal:${NC}"
echo "  Certificates auto-renew. Test renewal with: sudo certbot renew --dry-run"