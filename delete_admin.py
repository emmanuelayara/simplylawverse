#!/usr/bin/env python
"""
Admin Account Deletion Script
Use this to delete all admin accounts so you can create a fresh one
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import app
from models import User
from extensions import db

def delete_admin_accounts():
    """Delete all admin accounts from the database"""
    with app.app_context():
        # Get all admin accounts
        admins = User.query.filter_by(is_admin=True).all()
        
        if not admins:
            print("❌ No admin accounts found to delete.")
            return False
        
        print(f"Found {len(admins)} admin account(s):")
        for admin in admins:
            print(f"  - Username: {admin.username} (Email: {admin.email})")
        
        # Confirm deletion
        confirm = input("\n⚠️  Are you sure you want to delete these admin account(s)? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Deletion cancelled.")
            return False
        
        try:
            for admin in admins:
                db.session.delete(admin)
            
            db.session.commit()
            print(f"\n✅ Successfully deleted {len(admins)} admin account(s)!")
            print("✅ You can now create a new admin account by visiting /admin/register")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting admin accounts: {str(e)}")
            return False

def delete_specific_user(username=None, email=None):
    """Delete a specific user by username or email"""
    with app.app_context():
        user = None
        
        if username:
            user = User.query.filter_by(username=username).first()
        elif email:
            user = User.query.filter_by(email=email).first()
        
        if not user:
            print("❌ User not found.")
            return False
        
        print(f"Found user: {user.username} (Email: {user.email}) - Admin: {user.is_admin}")
        
        confirm = input(f"\n⚠️  Delete user '{user.username}'? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Deletion cancelled.")
            return False
        
        try:
            db.session.delete(user)
            db.session.commit()
            print(f"✅ Successfully deleted user '{user.username}'!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error deleting user: {str(e)}")
            return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--username' and len(sys.argv) > 2:
            delete_specific_user(username=sys.argv[2])
        elif sys.argv[1] == '--email' and len(sys.argv) > 2:
            delete_specific_user(email=sys.argv[2])
        elif sys.argv[1] == '--help':
            print("Admin Account Deletion Script")
            print("\nUsage:")
            print("  python delete_admin.py                    - Delete all admin accounts")
            print("  python delete_admin.py --username john    - Delete user by username")
            print("  python delete_admin.py --email john@ex.com - Delete user by email")
            print("  python delete_admin.py --help             - Show this help message")
        else:
            print("❌ Invalid argument. Use --help for usage information.")
    else:
        delete_admin_accounts()
