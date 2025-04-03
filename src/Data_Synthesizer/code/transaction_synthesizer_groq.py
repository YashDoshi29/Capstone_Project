import os
import json
import pandas as pd
import numpy as np
from groq import Groq
from datetime import datetime, timedelta

client = Groq(api_key=api_key)

# Configuration optimized for DC-specific data
PROFESSIONS = ["Student", "Federal Employee", "Businessman"]
CATEGORY_WEIGHTS = {
    "Student": {"Education": 0.3, "Food": 0.4, **{k: 0.3 / 3 for k in ["Housing", "Transportation", "Entertainment"]}},
    "Federal Employee": {"Housing": 0.4, "Transportation": 0.3,
                         **{k: 0.3 / 3 for k in ["Food", "Entertainment", "Education"]}},
    "Businessman": {"Entertainment": 0.3, "Food": 0.4,
                    **{k: 0.3 / 3 for k in ["Housing", "Transportation", "Education"]}}
}

DC_MERCHANTS = {
    "Grocery Store": [
        "Giant Food", "Safeway", "Whole Foods DC", "Yes! Organic Market", "Trader Joe's", "Harris Teeter",
        "ALDI Northeast", "MOM's Organic Market", "Dean & DeLuca", "Costco DC", "Wegmans DC", "La Cosecha Market",
        "Union Market", "Eastern Market Grocery", "Capitol Supermarket", "Good Food Markets", "Corner Market DC",
        "Neighborhood Grocery", "Foxtrot Market", "Lidl DC", "Greenheart Organic", "FreshFarm DC", "Capitol Hill Mart",
        "Metro Market", "Southeast Market", "FRESHFARM H Street", "Bloom Grocery", "Vegan Market DC", "Organic Brothers"
    ],
    "Restaurant": [
        "Ben's Chili Bowl", "Old Ebbitt Grill", "Founding Farmers", "Baan Siam", "Le Diplomate", "Busboys and Poets",
        "RPM Italian", "Barcelona Wine Bar", "Jaleo DC", "Maketto", "Blue Duck Tavern", "Zaytinya", "Ted's Bulletin",
        "Osteria Morini", "Duke's Grocery", "Rose’s Luxury", "Cava Mezze", "Farmbird", "Roaming Rooster", "Toki Underground",
        "District Taco", "Shouk DC", "El Rey", "Compass Rose", "Rasika", "CIRCA at Foggy Bottom", "The Smith", "Nando’s DC",
        "Pho 14", "Surfside", "Mastro’s DC", "Del Mar Wharf", "Tiger Fork", "Hatoba", "All-Purpose Pizzeria"
    ],
    "Gasoline Dealer": [
        "ExxonMobil DC", "Shell Capitol Hill", "BP Foggy Bottom", "Sunoco New York Ave", "Chevron Georgia Ave",
        "Citgo U Street", "Liberty Gas NW", "Shell Adams Morgan", "Exxon Wisconsin Ave", "BP 14th Street",
        "Shell Benning Rd", "Exxon H Street", "Chevron SE", "Sunoco Brookland", "Marathon Columbia Heights"
    ],
    "Hotel": [
        "Watergate Hotel", "Willard InterContinental", "Hamilton Crowne Plaza", "The LINE DC", "Marriott Marquis",
        "The Ritz-Carlton Georgetown", "Hotel Hive", "Sofitel Lafayette", "Dupont Circle Hotel", "Hyatt Place DC",
        "AC Hotel Navy Yard", "Conrad Washington DC", "The Darcy Hotel", "InterContinental Wharf", "Capitol Hill Hotel",
        "Hotel Washington", "The Madison Hotel", "Kimpton George Hotel", "Thompson DC", "YOTEL DC"
    ],
    "Massage Establishment": [
        "Spa World", "Capitol Massage", "Dupont Circle Thai Spa", "Unwind Wellness Center", "Massage Envy DC",
        "Tranquil Souls", "Deluca Massage & Bodywork", "Elements Massage DC", "U Thai Spa", "Massage Escape DC",
        "Bliss Spa Georgetown", "Georgetown Massage", "The Now Massage", "Body Harmony Spa", "Oasis Thai Spa",
        "Pure Bliss Spa", "Zensations DC", "Rejuvenation Lounge", "Serenity Massage", "Happy Feet Spa"
    ],
    "Motion Picture Theatre": [
        "AMC Georgetown", "Landmark E Street Cinema", "AFI Silver", "Regal Gallery Place", "Angelika Pop-Up",
        "ShowPlace ICON Theatres", "Alamo Drafthouse DC", "The Avalon Theatre", "Miracle Theatre", "West End Cinema",
        "Cinema Club DC", "District Movie House", "Union Market Drive-In", "Capitol Cinema", "Chinatown Theatres"
    ],
    "Clothing Store": [
        "Zara DC", "Uniqlo Georgetown", "Nordstrom Rack", "Banana Republic", "Madewell", "J.Crew", "H&M",
        "Anthropologie", "Lululemon", "Gap DC", "Reformation DC", "Urban Outfitters", "Everlane DC", "Patagonia DC",
        "Nike Store Georgetown", "Adidas Store", "Levi’s Store DC", "The North Face", "Aritzia", "Under Armour DC",
        "Frank And Oak", "Express DC", "Club Monaco", "Theory DC", "Rag & Bone", "Buckle DC", "Cotton On", "Athleta DC",
        "Free People DC", "Abercrombie DC"
    ],
    "Electronics": [
        "Apple Store Georgetown", "Best Buy DC", "Micro Center", "Target Tech DC", "uBreakiFix", "Microsoft Store DC",
        "Verizon Wireless", "T-Mobile DC", "AT&T Store", "GameStop", "B&H Express DC", "Camera Shop Georgetown",
        "Staples DC", "Office Depot", "DC Tech World", "Tech Corner", "Digital Haven", "Phone Repair Pros", "Geek Squad DC",
        "Electronic World DC", "CompuZone", "Tech Savvy", "Gadget Fixers", "ElectroMart", "Smart Solutions DC"
    ],
    "Fitness": [
        "Planet Fitness DC", "OrangeTheory Fitness", "Barry’s DC", "Solidcore", "CrossFit DC", "Gold’s Gym DC",
        "LA Fitness Columbia Heights", "SoulCycle Georgetown", "Equinox DC", "Vida Fitness", "F45 Training DC",
        "Crunch Fitness DC", "Yoga District", "CycleBar DC", "CorePower Yoga", "FitDC", "9Round Kickboxing", "TITLE Boxing Club",
        "Fit Lab DC", "Elite Performance DC", "Balance Gym", "Cut Seven", "Down Dog Yoga", "Zengo Cycle", "Washington Sports Club"
    ],
    "Education": ["George Washington University", "Georgetown University", "Howard University", "American University",
    "University of the District of Columbia", "Strayer University", "Trinity Washington University",
    "Gallaudet University", "Catholic University of America", "UDC Community College",
    "Kaplan Test Prep DC", "DC Public Schools", "District of Learning Center", "ELS Language Centers DC",
    "Princeton Review DC", "Code Fellows DC", "General Assembly DC", "Sylvan Learning Center",
    "Kumon of Capitol Hill", "Varsity Tutors DC", "Mathnasium DC", "Berlitz Language Center",],

    "Healthcare": ["MedStar Washington Hospital Center", "George Washington University Hospital", "Sibley Memorial Hospital",
    "Children's National Hospital", "Howard University Hospital", "Kaiser Permanente DC", "Unity Health Care",
    "Providence Health System", "DC Health & Wellness Center", "One Medical DC", "CVS MinuteClinic DC",
    "Walgreens Healthcare Clinic", "Georgetown University Hospital", "Medics USA", "MyDoc Urgent Care",
    "CityHealth Urgent Care", "CareFirst BlueCross DC", "Aetna Health DC", "Planned Parenthood DC", "Sunrise Medical Group"
    ],
}

def generate_dc_transactions(num_customers=50, transactions_per=2):
    """Generate realistic DC transaction data with temporal patterns"""
    np.random.seed(42)
    transactions = []
    customer_id = 1000

    for profession in PROFESSIONS:
        # Generate customer base with profession-specific patterns
        for _ in range(num_customers):
            cust_id = f"CUST{customer_id}"
            customer_id += 1

            # Generate multiple transactions per customer
            for _ in range(transactions_per):
                # DC-specific date patterns (weekdays vs weekends)
                date = generate_dc_date()

                # Category selection with DC-specific weighting
                category = np.random.choice(
                    list(CATEGORY_WEIGHTS[profession].keys()),
                    p=list(CATEGORY_WEIGHTS[profession].values())
                )

                # Merchant selection with DC landmarks
                merchant = np.random.choice(DC_MERCHANTS[category])

                # Amount generation with DC cost of living adjustments
                amount = generate_realistic_amount(profession, category, date)

                transactions.append({
                    "Date": date.strftime("%Y-%m-%d"),
                    "CustomerID": cust_id,
                    "Profession": profession,
                    "Merchant": merchant,
                    "Amount": round(amount, 2),
                    "Category": category,
                    "Location": "Washington DC"
                })

    return pd.DataFrame(transactions)


def generate_dc_date():
    """Generate dates with DC temporal patterns (e.g., government pay cycles)"""
    start_date = datetime.now() - timedelta(days=180)
    random_days = np.random.randint(0, 180)
    base_date = start_date + timedelta(days=random_days)

    # Adjust for DC payday patterns (1st/15th clustering)
    if np.random.rand() < 0.3:
        day = 1 if np.random.rand() < 0.5 else 15
        return base_date.replace(day=day)
    return base_date


def generate_realistic_amount(profession, category, date):
    """DC-specific amount generation with cost of living adjustments"""
    base_ranges = {
        "Student": {"Housing": (800, 1500), "Food": (8, 25), "Transportation": (20, 50)},
        "Federal Employee": {"Housing": (1200, 2500), "Food": (15, 75), "Transportation": (50, 150)},
        "Businessman": {"Housing": (2000, 4000), "Food": (30, 150), "Transportation": (75, 300)}
    }

    # Get base range
    min_val, max_val = base_ranges[profession].get(category, (10, 100))

    # Weekend/Holiday markups
    if date.weekday() >= 5:
        min_val *= 1.2
        max_val *= 1.5

    # Generate amount with normal distribution (μ at 40% of range)
    mu = min_val + (max_val - min_val) * 0.4
    sigma = (max_val - min_val) * 0.2
    amount = np.random.normal(mu, sigma)

    return np.clip(amount, min_val, max_val)


# Generate and save dataset
df = generate_dc_transactions(num_customers=50, transactions_per=2)
df.to_csv("dc_transactions_optimized.csv", index=False)
print(f"Generated {len(df)} DC transactions with realistic patterns")