"""
DREAM AI - Prisma Database Seeding Script
Task 1.1: Database Schema Setup - Seed Data
Version: 1.0
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from prisma import Prisma
from prisma.enums import (
    PropertyType, PropertyClass, SourceType, HowReceived, 
    MarketStatus, DealStage, Priority
)

async def seed_database():
    """
    Seed the database with sample data for testing.
    Creates organization, users, and sample deals.
    """
    prisma = Prisma()
    
    try:
        await prisma.connect()
        print("🌱 Starting database seeding...")
        
        # 1. Create or get Organization
        print("Creating organization...")
        org = await prisma.organization.find_first()
        if not org:
            org = await prisma.organization.create(
                data={
                    "name": "Shieldstone Acquisitions Demo",
                    "subscriptionTier": "PROFESSIONAL",
                    "settings": {
                        "default_hold_period": 60,
                        "default_market_tier": "SECONDARY",
                        "timezone": "America/New_York"
                    }
                }
            )
            print(f"✅ Created organization: {org.name}")
        else:
            print(f"✅ Using existing organization: {org.name}")
        
        # 2. Create or get Users
        print("Creating users...")
        users = []
        user_emails = [
            "john.analyst@shieldstone.com",
            "sarah.manager@shieldstone.com"
        ]
        
        for email in user_emails:
            user = await prisma.user.find_unique(where={"email": email})
            if not user:
                user = await prisma.user.create(
                    data={
                        "organizationId": org.id,
                        "email": email,
                        "name": "John Analyst" if "john" in email else "Sarah Manager",
                        "role": "ANALYST" if "john" in email else "ADMIN",
                        "preferences": {
                            "email_notifications": True,
                            "default_view": "pipeline" if "john" in email else "dashboard"
                        }
                    }
                )
                print(f"✅ Created user: {user.email}")
            else:
                print(f"✅ Using existing user: {user.email}")
            users.append(user)
        
        # 3. Create Sample Deals
        print("Creating sample deals...")
        
        sample_deals = [
            {
                "propertyName": "Oak Creek Apartments",
                "addressStreet": "1234 Oak Creek Drive",
                "addressCity": "Austin",
                "addressState": "TX",
                "addressZip": "78744",
                "propertyType": PropertyType.MULTIFAMILY,
                "propertyClass": PropertyClass.B,
                "yearBuilt": 1985,
                "units": 196,
                "askingPrice": Decimal("34300000"),
                "occupancy": Decimal("0.88"),
                "noiInPlace": Decimal("1959275"),
                "noiProForma": Decimal("2450000"),
                "sourceType": SourceType.BROKER,
                "sourceName": "John Smith",
                "sourceCompany": "CBRE",
                "sourceEmail": "jsmith@cbre.com",
                "howReceived": HowReceived.EMAIL,
                "marketStatus": MarketStatus.OFF_MARKET,
                "stage": DealStage.SCREENING,
                "priority": Priority.HIGH,
                "notes": "Value-add opportunity in South Austin. 1985 vintage with partial 2015 renovation. Strong tech-driven market growth."
            },
            {
                "propertyName": "Riverside Gardens",
                "addressStreet": "5678 Riverside Blvd",
                "addressCity": "Dallas",
                "addressState": "TX",
                "addressZip": "75201",
                "propertyType": PropertyType.MULTIFAMILY,
                "propertyClass": PropertyClass.A,
                "yearBuilt": 2010,
                "units": 120,
                "askingPrice": Decimal("28000000"),
                "occupancy": Decimal("0.95"),
                "noiInPlace": Decimal("1680000"),
                "sourceType": SourceType.DIRECT_OWNER,
                "sourceName": "Jane Doe",
                "howReceived": HowReceived.PHONE,
                "marketStatus": MarketStatus.LISTED,
                "stage": DealStage.NEW,
                "priority": Priority.MEDIUM,
                "notes": "Class A property in prime Dallas location. Fully stabilized."
            },
            {
                "propertyName": "Maple Street Apartments",
                "addressStreet": "9012 Maple Street",
                "addressCity": "Houston",
                "addressState": "TX",
                "addressZip": "77002",
                "propertyType": PropertyType.MULTIFAMILY,
                "propertyClass": PropertyClass.C,
                "yearBuilt": 1975,
                "units": 85,
                "askingPrice": Decimal("8500000"),
                "occupancy": Decimal("0.82"),
                "noiInPlace": Decimal("510000"),
                "sourceType": SourceType.WHOLESALER,
                "sourceName": "Bob Wholesaler",
                "howReceived": HowReceived.EMAIL,
                "marketStatus": MarketStatus.PRE_MARKET,
                "stage": DealStage.NEW,
                "priority": Priority.LOW,
                "notes": "Distressed property requiring significant renovation."
            }
        ]
        
        created_deals = []
        for deal_data in sample_deals:
            # Check if deal already exists
            existing = await prisma.deal.find_first(
                where={
                    "organizationId": org.id,
                    "propertyName": deal_data["propertyName"]
                }
            )
            
            if not existing:
                deal_data["organizationId"] = org.id
                deal_data["createdById"] = users[0].id
                
                deal = await prisma.deal.create(data=deal_data)
                created_deals.append(deal)
                print(f"✅ Created deal: {deal.propertyName}")
            else:
                print(f"✅ Deal already exists: {deal_data['propertyName']}")
                created_deals.append(existing)
        
        print("\n✅ Database seeding completed!")
        print(f"""
        Summary:
        - Organization: {org.name}
        - Users: {len(users)}
        - Deals: {len(created_deals)}
        
        Sample deals created:
        """)
        for deal in created_deals:
            print(f"  - {deal.propertyName} ({deal.units} units, {deal.stage})")
        
    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(seed_database())







