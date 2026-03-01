"""
Database seeding script for Simply Law
Populates initial data for services, consultation types, and admin availability
"""
from app import create_app, db
from models import Service, ConsultationType, AdminAvailability
from datetime import datetime, timedelta

def seed_database():
    """Populate database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        
        # Clear existing data (optional, comment out if you want to append)
        # Service.query.delete()
        # ConsultationType.query.delete()
        # AdminAvailability.query.delete()
        
        # Check if data already exists
        if Service.query.first():
            print("⚠️  Services already exist. Skipping services seeding.")
        else:
            seed_services()
        
        if ConsultationType.query.first():
            print("⚠️  Consultation types already exist. Skipping consultation types seeding.")
        else:
            seed_consultation_types()
        
        if AdminAvailability.query.first():
            print("⚠️  Availability already exists. Skipping availability seeding.")
        else:
            seed_availability()
        
        db.session.commit()
        print("✅ Database seeding completed successfully!")


def seed_services():
    """Seed legal services"""
    services = [
        Service(
            name="Company Registration & CAC Filings",
            slug="company-registration",
            description="Expert guidance through company registration with CAC, including name search, documentation, and compliance setup.",
            detailed_content="""
            <h2>Complete Company Registration Service</h2>
            <p>Setting up a company in Nigeria requires navigating regulatory requirements and documentation. We handle the complete process:</p>
            
            <h3>What's Included:</h3>
            <ul>
                <li>Company name availability search</li>
                <li>Documentation preparation and filing</li>
                <li>CAC registration follow-up</li>
                <li>Tax Identification Number (TIN) registration</li>
                <li>Compliance documentation setup</li>
            </ul>
            
            <h3>Benefits:</h3>
            <p>Proper company registration ensures legal recognition, tax compliance, and operational credibility. We ensure your company is registered correctly from the start.</p>
            """,
            who_needs_it="New business owners, entrepreneurs establishing formal companies, investors setting up corporate entities.",
            typical_timeline="2-4 weeks",
            base_price=50000,
            seo_title="Company Registration & CAC Filings - Simply Law",
            seo_description="Expert CAC company registration in Nigeria. Professional guidance through documentation, filing, and compliance setup.",
            seo_keywords="CAC registration, company registration Nigeria, business setup, corporate formation",
            order=1,
            is_active=True
        ),
        Service(
            name="Contract Drafting & Review",
            slug="contract-drafting",
            description="Professional drafting and thorough review of business contracts to protect your interests.",
            detailed_content="""
            <h2>Professional Contract Services</h2>
            <p>Contracts are critical to business relationships. We provide expert drafting and review services to protect your interests:</p>
            
            <h3>Service Types:</h3>
            <ul>
                <li>Commercial contracts (sales, supply, service agreements)</li>
                <li>Employment agreements and offer letters</li>
                <li>Partnership and collaboration agreements</li>
                <li>Vendor and supplier contracts</li>
                <li>Non-disclosure agreements (NDAs)</li>
                <li>Terms of service and privacy policies</li>
            </ul>
            
            <h3>Our Approach:</h3>
            <p>We draft contracts tailored to your business needs, with clear terms that protect your interests and are fair to all parties. Existing contracts are reviewed thoroughly to identify risks and negotiate favorable terms.</p>
            """,
            who_needs_it="Businesses negotiating contracts, entrepreneurs creating formal agreements, companies needing contract review before signing.",
            typical_timeline="3-7 days",
            base_price=35000,
            seo_title="Contract Drafting & Review - Simply Law",
            seo_description="Professional contract drafting and review services in Nigeria. Protect your business with well-drafted contracts.",
            seo_keywords="contract drafting, contract review, business contracts Nigeria, legal agreements",
            order=2,
            is_active=True
        ),
        Service(
            name="Corporate Governance & Compliance",
            slug="compliance",
            description="Strategic guidance on corporate governance structures and regulatory compliance for your business.",
            detailed_content="""
            <h2>Corporate Governance & Compliance</h2>
            <p>Proper governance and compliance protect your business and set you up for growth:</p>
            
            <h3>Governance Services:</h3>
            <ul>
                <li>Corporate structure and board governance</li>
                <li>Shareholder agreements</li>
                <li>Board resolutions and corporate policies</li>
                <li>Founder and investment documentation</li>
            </ul>
            
            <h3>Compliance Guidance:</h3>
            <ul>
                <li>Regulatory requirement analysis</li>
                <li>Industry compliance frameworks</li>
                <li>Data protection and privacy compliance</li>
                <li>Tax and filing compliance</li>
            </ul>
            """,
            who_needs_it="Growing companies, startups with investors, businesses facing regulatory changes, companies seeking governance upgrades.",
            typical_timeline="2-4 weeks",
            base_price=75000,
            seo_title="Corporate Governance & Compliance - Simply Law",
            seo_description="Corporate governance and compliance advisory for Nigerian businesses. Ensure proper structure and regulatory compliance.",
            seo_keywords="corporate governance, compliance advice, business governance Nigeria",
            order=3,
            is_active=True
        ),
        Service(
            name="Regulatory Advisory",
            slug="regulatory-advisory",
            description="Expert guidance on industry-specific regulations and compliance requirements.",
            detailed_content="""
            <h2>Regulatory Advisory Service</h2>
            <p>Navigating regulations specific to your industry ensures compliance and reduces legal risk:</p>
            
            <h3>Covered Areas:</h3>
            <ul>
                <li>Industry-specific regulations</li>
                <li>License and permit requirements</li>
                <li>Compliance documentation and reporting</li>
                <li>Regulatory change management</li>
            </ul>
            """,
            who_needs_it="Businesses in regulated industries, companies facing new regulations, organizations seeking compliance clarity.",
            typical_timeline="1-3 weeks",
            base_price=40000,
            seo_title="Regulatory Advisory - Simply Law",
            seo_description="Expert regulatory advisory for Nigerian businesses. Industry-specific compliance guidance.",
            seo_keywords="regulatory compliance, industry regulations Nigeria",
            order=4,
            is_active=True
        ),
        Service(
            name="Due Diligence & Transaction Support",
            slug="due-diligence",
            description="Comprehensive business due diligence for transactions, acquisitions, and partnerships.",
            detailed_content="""
            <h2>Due Diligence & Transaction Services</h2>
            <p>Whether buying, selling, or partnering, thorough due diligence protects your investment:</p>
            
            <h3>Services Include:</h3>
            <ul>
                <li>Legal and regulatory due diligence</li>
                <li>Contract review and analysis</li>
                <li>Risk identification and assessment</li>
                <li>Transaction documentation preparation</li>
            </ul>
            """,
            who_needs_it="Buyers conducting acquisitions, businesses planning mergers, companies entering partnerships.",
            typical_timeline="2-6 weeks",
            base_price=100000,
            seo_title="Due Diligence & Transaction Support - Simply Law",
            seo_description="Professional due diligence and transaction support for Nigerian business deals.",
            seo_keywords="due diligence, M&A, business acquisition, transaction support",
            order=5,
            is_active=True
        ),
        Service(
            name="SME & Startup Legal Retainers",
            slug="retainer",
            description="Flexible ongoing legal support for growing businesses and startups.",
            detailed_content="""
            <h2>Legal Retainer Services</h2>
            <p>Ongoing legal support tailored to your business needs:</p>
            
            <h3>Retainer Benefits:</h3>
            <ul>
                <li>Priority access to legal advice</li>
                <li>Flexible consultation hours</li>
                <li>Document drafting and review</li>
                <li>Compliance support</li>
                <li>Cost-effective ongoing support</li>
            </ul>
            
            <p>Perfect for growing businesses needing regular legal guidance without hiring full-time counsel.</p>
            """,
            who_needs_it="Startups with ongoing legal needs, SMEs managing multiple legal matters, growing companies on a budget.",
            typical_timeline="Ongoing",
            base_price=None,
            seo_title="Legal Retainers for SMEs & Startups - Simply Law",
            seo_description="Flexible legal retainer packages for Nigerian startups and SMEs. Ongoing professional legal support.",
            seo_keywords="startup legal services, SME legal support, retainer agreement",
            order=6,
            is_active=True
        ),
    ]
    
    for service in services:
        db.session.add(service)
    
    print(f"✅ Added {len(services)} services")


def seed_consultation_types():
    """Seed consultation types"""
    consultation_types = [
        ConsultationType(
            name="30-Minute Express Consultation",
            duration_minutes=30,
            price_naira=15000,
            description="Quick legal clarification and preliminary advice. Ideal for urgent matters or quick questions.",
            includes_document_review=False,
            includes_written_advice=False,
            includes_follow_up=False,
            is_active=True,
            order=1
        ),
        ConsultationType(
            name="60-Minute Strategy Session",
            duration_minutes=60,
            price_naira=30000,
            description="Comprehensive legal analysis with document review and strategic recommendations.",
            includes_document_review=True,
            includes_written_advice=True,
            includes_follow_up=False,
            is_active=True,
            order=2
        ),
        ConsultationType(
            name="90-Minute In-Depth Session",
            duration_minutes=90,
            price_naira=42000,
            description="Extended consultation with thorough analysis, document review, and detailed advice.",
            includes_document_review=True,
            includes_written_advice=True,
            includes_follow_up=True,
            is_active=True,
            order=3
        ),
        ConsultationType(
            name="Retainer Onboarding Session",
            duration_minutes=120,
            price_naira=60000,
            description="Half-day session for new retainer clients. Comprehensive business legal assessment and strategy planning.",
            includes_document_review=True,
            includes_written_advice=True,
            includes_follow_up=True,
            is_active=True,
            order=4
        ),
    ]
    
    for consultation_type in consultation_types:
        db.session.add(consultation_type)
    
    print(f"✅ Added {len(consultation_types)} consultation types")


def seed_availability():
    """Seed admin availability for next 30 days"""
    availabilities = []
    
    # Working hours: 9 AM - 5 PM, Monday to Friday
    for days_ahead in range(1, 31):
        check_date = (datetime.utcnow() + timedelta(days=days_ahead)).date()
        
        # Skip weekends
        if check_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            continue
        
        # Morning slot: 9 AM - 1 PM
        availabilities.append(AdminAvailability(
            date=check_date,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("13:00", "%H:%M").time(),
            is_available=True,
            max_slots=2,
            slot_duration_minutes=30,
            notes="Morning availability"
        ))
        
        # Afternoon slot: 2 PM - 5 PM
        availabilities.append(AdminAvailability(
            date=check_date,
            start_time=datetime.strptime("14:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            is_available=True,
            max_slots=2,
            slot_duration_minutes=30,
            notes="Afternoon availability"
        ))
    
    for availability in availabilities:
        db.session.add(availability)
    
    print(f"✅ Added {len(availabilities)} availability slots")


if __name__ == '__main__':
    seed_database()
