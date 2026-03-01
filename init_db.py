#!/usr/bin/env python
"""Initialize and seed Simply Law database"""
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
            print("Simply Law - Database Initialization")
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
                    name="Company Registration & CAC Filings",
                    slug="company-registration",
                    description="Expert guidance through company registration with CAC, including name search, documentation, and compliance setup.",
                    detailed_content="We handle the complete CAC registration process including company name availability search, documentation preparation, filing, and compliance setup. Legal recognition and tax compliance guaranteed.",
                    who_needs_it="New business owners, entrepreneurs establishing formal companies, investors setting up corporate entities.",
                    typical_timeline="2-4 weeks",
                    base_price=50000,
                    icon_class="fas fa-building",
                    order=1,
                    is_active=True
                ),
                Service(
                    name="Contract Drafting & Review",
                    slug="contract-drafting",
                    description="Professional drafting and thorough review of business contracts to protect your interests.",
                    detailed_content="We provide expert drafting and review of commercial contracts, employment agreements, partnerships, NDAs, and vendor contracts. Tailored terms that protect your business.",
                    who_needs_it="Businesses negotiating contracts, entrepreneurs creating formal agreements, companies needing contract review.",
                    typical_timeline="3-7 days",
                    base_price=35000,
                    icon_class="fas fa-file-contract",
                    order=2,
                    is_active=True
                ),
                Service(
                    name="Corporate Governance & Compliance",
                    slug="compliance",
                    description="Strategic guidance on corporate governance structures and regulatory compliance for your business.",
                    detailed_content="Proper governance and compliance protect your business and set you up for growth. Services include corporate structure, shareholder agreements, board governance, and regulatory compliance.",
                    who_needs_it="Growing companies, startups with investors, businesses facing regulatory changes, companies seeking governance upgrades.",
                    typical_timeline="2-4 weeks",
                    base_price=75000,
                    icon_class="fas fa-shield-alt",
                    order=3,
                    is_active=True
                ),
                Service(
                    name="Business & Corporate Law",
                    slug="corporate-law",
                    description="Comprehensive legal solutions for business operations, mergers, and corporate matters.",
                    detailed_content="We provide comprehensive corporate legal services including corporate restructuring, mergers and acquisitions, ongoing governance support, and general business legal matters.",
                    who_needs_it="Businesses and corporations seeking expert corporate counsel and legal support.",
                    typical_timeline="2-4 weeks",
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
