import pandas as pd
import random
from faker import Faker


# Initialize faker
Faker = Faker()

# Helper functions for random choices
def random_choice(options):
    return random.choice(options)


def random_number(min_val, max_val):
    return random.randint(min_val, max_val)


def generate_investors(num_records):
    data = []
    domains = ["Tech", "Healthcare", "Finance", "Education", "E-commerce"]
    credibility_levels = ["High", "Medium", "Low"]
    risk_appetites = ["High", "Medium", "Low"]

    for _ in range(num_records):
        record = {
            "Record ID": Faker.uuid4(),
            "Investor_Group_Name": Faker.company(),
            "Credibility": random_choice(credibility_levels),
            "Domain": random_choice(domains),
            "Fund_Available": random_number(100000, 10000000),
            "Risk_Appetite": random_choice(risk_appetites)
        }
        data.append(record)

    return pd.DataFrame(data)


def generate_startups(num_records):
    data = []
    domains = ["Tech", "Healthcare", "Finance", "Education", "E-commerce"]
    growth_potentials = ["High", "Medium", "Low"]
    risk_assessments = ["High", "Medium", "Low"]
    investment_stages = ["Seed", "Series A", "Series B", "Growth"]

    for _ in range(num_records):
        record = {
            "Record ID": Faker.uuid4(),
            "Company_Name": Faker.company(),
            "MOAT": Faker.sentence(nb_words=6),
            "Unique_Selling_Proposition": Faker.sentence(nb_words=10),
            "Growth_Potential": random_choice(growth_potentials),
            "Market_Size": random_number(1000000, 100000000),
            "Scalability": random_choice(["High", "Medium", "Low"]),
            "ROI": random_number(5, 100),
            "Revenues_Streams": Faker.sentence(nb_words=4),
            "Exit_Strategy": Faker.sentence(nb_words=8),
            "Domain": random_choice(domains),
            "Valuation": random_number(100000, 50000000),
            "Deal": random_number(10000, 1000000),
            "Fund_Raised": random_number(10000, 1000000),
            "Financials": random_number(10000, 5000000),
            "Marketing_Strategy": Faker.sentence(nb_words=6),
            "Target_Audience": Faker.sentence(nb_words=5),
            "Risk_Assessment": random_choice(risk_assessments),
            "Location": Faker.city(),
            "Investment_Stage": random_choice(investment_stages)
        }
        data.append(record)

    return pd.DataFrame(data)

def scoring_logic(investors, startups):
    relationships = []

    for investor_idx, investor in investors.iterrows():
        for startup_idx, startup in startups.iterrows():
            compatible = (
                    investor['Domain'] == startup['Domain'] and
                    investor['Fund_Available'] >= startup['Valuation'] and
                    investor['Risk_Appetite'] == startup['Risk_Assessment']
            )
            relationships.append({
                "Investor": investor['Investor_Group_Name'],
                "Startup": startup['Company_Name'],
                "Compatible": "Yes" if compatible else "No"
            })

    return pd.DataFrame(relationships)


def create_relationships(investors, startups):
    relationships = []

    for investor_idx, investor in investors.iterrows():
        for startup_idx, startup in startups.iterrows():
            compatible = (
                    investor['Domain'] == startup['Domain'] and
                    investor['Fund_Available'] >= startup['Valuation'] and
                    investor['Risk_Appetite'] == startup['Risk_Assessment']
            )
            relationships.append({
                "Investor": investor['Investor_Group_Name'],
                "Startup": startup['Company_Name'],
                "Compatible": "Yes" if compatible else "No"
            })

    return pd.DataFrame(relationships)


# Generate data
num_records = 50
investors = generate_investors(num_records)
startups = generate_startups(num_records)
relationships = create_relationships(investors, startups)

# Save to CSV
investors.to_csv("investors.csv", index=False)
startups.to_csv("startups.csv", index=False)
relationships.to_csv("relationships.csv", index=False)

print("Data generated and saved successfully!")
