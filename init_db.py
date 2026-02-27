#!/usr/bin/env python
"""Initialize and seed Simply Lawverse database"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    try:
        from app import app, db
        from models import Service, ConsultationType
        
        with app.app_context():
            print("\n" + "="*60)
            print("Simply Lawverse - Database Initialization")
            print("="*60 + "\n")
            
            # Check if database exists and is complete
            db_path = project_root / 'instance' / 'site.db'
            if db_path.exists():
                print(f"Found existing database at {db_path}")
                print("Removing incomplete database...")
                db_path.unlink()
                print("[OK] Database removed\n")
            
            print("Creating database tables...")
            db.create_all()
            print("[OK] All tables created\n")
            
            # Seed initial data
            print("Seeding initial data...")
            
            # Add consultation types
            consultation_types = [
                ConsultationType(
                    name="15-Minute Quick Consultation",
                    duration_minutes=15,
                    price_naira=5000,
                    description="Quick overview of your legal matter",
                    includes_document_review=False,
                    includes_written_advice=False,
                    includes_follow_up=False,
                    is_active=True,
                    order=1
                ),
                ConsultationType(
                    name="30-Minute Standard Consultation",
                    duration_minutes=30,
                    price_naira=15000,
                    description="Comprehensive consultation with document review",
                    includes_document_review=True,
                    includes_written_advice=True,
                    includes_follow_up=False,
                    is_active=True,
                    order=2
                ),
                ConsultationType(
                    name="1-Hour Premium Consultation",
                    duration_minutes=60,
                    price_naira=35000,
                    description="In-depth consultation with follow-up support",
                    includes_document_review=True,
                    includes_written_advice=True,
                    includes_follow_up=True,
                    is_active=True,
                    order=3
                ),
            ]
            
            for ct in consultation_types:
                existing = ConsultationType.query.filter_by(name=ct.name).first()
                if not existing:
                    db.session.add(ct)
            
            # Add services
            services = [
                Service(
                    name="Corporate Law",
                    slug="corporate-law",
                    description="Expert guidance on corporate governance, mergers, and acquisitions",
                    detailed_content="We provide comprehensive corporate legal services including company formation, corporate restructuring, mergers and acquisitions, and ongoing governance support.",
                    who_needs_it="Businesses and corporations seeking expert corporate counsel",
                    typical_timeline="2-4 weeks",
                    base_price=50000,
                    icon_class="fas fa-building",
                    order=1,
                    is_active=True
                ),
                Service(
                    name="Family Law",
                    slug="family-law",
                    description="Compassionate support for family matters including divorce, custody, and inheritance",
                    detailed_content="We handle all aspects of family law with sensitivity and professionalism. Our services include divorce proceedings, child custody arrangements, inheritance disputes, and domestic matters.",
                    who_needs_it="Individuals and families navigating personal legal matters",
                    typical_timeline="4-8 weeks",
                    base_price=30000,
                    icon_class="fas fa-heart",
                    order=2,
                    is_active=True
                ),
                Service(
                    name="Real Estate Law",
                    slug="real-estate-law",
                    description="Complete property transactions and dispute resolution services",
                    detailed_content="From property purchase and sale to leasing agreements and dispute resolution, we provide comprehensive real estate legal services.",
                    who_needs_it="Property buyers, sellers, and investors",
                    typical_timeline="3-6 weeks",
                    base_price=40000,
                    icon_class="fas fa-home",
                    order=3,
                    is_active=True
                ),
                Service(
                    name="Criminal Defense",
                    slug="criminal-defense",
                    description="Strong representation and defense strategies in criminal matters",
                    detailed_content="Our experienced criminal defense lawyers provide aggressive representation at all levels of the criminal justice system.",
                    who_needs_it="Individuals facing criminal charges",
                    typical_timeline="Varies by case",
                    base_price=50000,
                    icon_class="fas fa-gavel",
                    order=4,
                    is_active=True
                ),
            ]
            
            for service in services:
                existing = Service.query.filter_by(slug=service.slug).first()
                if not existing:
                    db.session.add(service)
            
            db.session.commit()
            
            ct_count = ConsultationType.query.count()
            svc_count = Service.query.count()
            
            print(f"[OK] Added {ct_count} consultation types")
            print(f"[OK] Added {svc_count} services")
            
            print("\n" + "="*60)
            print("[OK] DATABASE INITIALIZATION COMPLETE!")
            print("="*60)
            print("\nYou can now start the Flask server with:")
            print("  flask run --debug")
            print()
            
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
