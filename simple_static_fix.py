#!/usr/bin/env python3
"""
Simple Wagtail Static Files Fix
Run this on your server to collect Wagtail static files
"""

import os
import sys
import subprocess
import shutil

def run_command(cmd, description):
    """Run a shell command and return success"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd='/root/apps/cashmatters')
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 Simple Wagtail Static Files Fix")
    print("=" * 40)

    # 1. Clear any existing static files
    static_root = '/root/apps/cashmatters/staticfiles'
    if os.path.exists(static_root):
        print("🧹 Clearing old static files...")
        shutil.rmtree(static_root)
        os.makedirs(static_root, exist_ok=True)

    # 2. Run collectstatic with verbose output
    if not run_command('python manage.py collectstatic --noinput --clear --verbosity=2', 'Collecting static files (verbose)'):
        return False

    # 3. Check if Wagtail admin static files exist
    wagtail_admin_static = os.path.join(static_root, 'wagtailadmin')
    if os.path.exists(wagtail_admin_static):
        js_files = []
        css_files = []
        for root, dirs, files in os.walk(wagtail_admin_static):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(file)
                elif file.endswith('.css'):
                    css_files.append(file)

        print(f"✅ Found {len(js_files)} Wagtail JS files and {len(css_files)} CSS files")

        # List some key files
        key_files = ['wagtailadmin.js', 'core.js']
        for root, dirs, files in os.walk(wagtail_admin_static):
            for file in files:
                if file in key_files:
                    print(f"   Found: {file}")
                    break
    else:
        print("❌ Wagtail admin static files not found")
        print("   Checking what was collected...")

        # List what's in staticfiles
        if os.path.exists(static_root):
            print("   Contents of staticfiles/:")
            for item in os.listdir(static_root)[:10]:  # Show first 10 items
                print(f"     {item}")
        return False

    print("\n🎉 Static files collected successfully!")
    print("\n📋 NEXT STEPS:")
    print("1. Restart your web server:")
    print("   sudo systemctl restart gunicorn")
    print("   sudo systemctl restart nginx")
    print("")
    print("2. Clear browser cache and test the admin interface")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)