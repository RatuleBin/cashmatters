#!/bin/bash

# CashMatters Docker Deployment Setup Script
# Run this on your server to prepare for GitHub Actions deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up CashMatters Docker deployment...${NC}"

# Create application directory
echo -e "${YELLOW}📁 Creating application directory...${NC}"
sudo mkdir -p /home/django/apps
sudo chown $USER:$USER /home/django/apps

# Clone repository (replace with your actual repo URL)
echo -e "${YELLOW}📋 Cloning repository...${NC}"
cd /home/django/apps
git clone https://github.com/RatuleBin/cashmatters.git

# Set proper permissions
echo -e "${YELLOW}🔐 Setting permissions...${NC}"
sudo chown -R $USER:$USER /home/django/apps/cashmatters

# Create .env file from example
echo -e "${YELLOW}⚙️ Setting up environment file...${NC}"
cd /home/django/apps/cashmatters
cp .env.example .env
echo -e "${RED}⚠️  Please edit .env file with your production settings!${NC}"

# Create necessary directories
echo -e "${YELLOW}📁 Creating media and static directories...${NC}"
mkdir -p media staticfiles

echo -e "${GREEN}✅ Setup completed!${NC}"
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Edit /home/django/apps/cashmatters/.env with production settings"
echo "2. Set up GitHub Actions secrets"
echo "3. Push to main branch to trigger deployment"