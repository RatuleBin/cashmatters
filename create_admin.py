#!/usr/bin/env python
"""Script to create or update admin superuser"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cashmatters.settings.dev')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Delete existing admin user if exists
User.objects.filter(username='admin').delete()

# Create new superuser
user = User.objects.create_superuser(
    username='admin',
    email='admin@cashmatters.com',
    password='admin123'
)

print("✅ Superuser created successfully!")
print("=" * 50)
print("Username: admin")
print("Password: admin123")
print("=" * 50)
print("\nYou can now log in at: http://127.0.0.1:8000/admin/")
