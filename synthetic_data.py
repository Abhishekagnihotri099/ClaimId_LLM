import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Configurations
num_claims = 1000  
num_notes = 1500   
num_vehicles = 500 
num_transactions = 2000  
num_exposures = 800  
num_coverages = 600  
num_histories = 1200  
num_activities = 900  

# Generate Notes Data
def generate_accident_description():
    # Random accident details
    date = fake.date_this_year()  # Random date in this year
    time = fake.time()  # Random time
    location = fake.address()  # Random location (address)
    
    # Types of accidents
    accident_types = ['collision', 'head-on crash', 'rear-end collision', 'side-impact crash', 'slip and fall', 'rollover']
    accident_type = random.choice(accident_types)
    
    # Number of vehicles involved
    num_vehicles = random.randint(1, 4)
    
    # Casualties and injuries
    injuries = random.choice(['minor injuries', 'serious injuries', 'fatalities', 'no injuries'])
    
    # Weather conditions (optional)
    weather_conditions = random.choice(['sunny', 'rainy', 'foggy', 'snowy', 'stormy'])
    
    # Vehicle damage details
    damage_types = ['crushed front bumper', 'smashed windshield', 'damaged rear axle', 'broken headlights', 'scratched doors', 'severely dented hood']
    damage_severity = ['minor', 'moderate', 'severe']
    
    # Damage for each vehicle
    damages = []
    for _ in range(num_vehicles):
        damage_type = random.choice(damage_types)
        severity = random.choice(damage_severity)
        damages.append(f"{severity} damage to the {damage_type}")
    
    # Join the damages in a readable way
    damage_description = ", ".join(damages)
    
    # Formulate the full accident description
    description = f"On {date} at {time}, a {accident_type} occurred at {location}. The accident involved {num_vehicles} vehicles, and there were {injuries}. The weather was {weather_conditions} at the time of the accident. The vehicles sustained the following damage: {damage_description}."
    
    return description

# Generate Claims Table
claims = pd.DataFrame({
    "ClaimNumber": [f"CLM{str(i).zfill(6)}" for i in range(1, num_claims + 1)],
    "HowReported": random.choices(["Phone", "Email", "Online", "In-Person"], k=num_claims),
    "MainContactType": random.choices(["Policyholder", "Agent", "Broker"], k=num_claims),
    "ReportedDate": [fake.date_between(start_date='-3y', end_date='today') for _ in range(num_claims)],
    "PolicyLocations": [f"LOC{str(i).zfill(4)}" for i in random.choices(range(1000), k=num_claims)],
    "LossDate": [fake.date_between(start_date='-4y', end_date='today') for _ in range(num_claims)],
    "LossCause": random.choices(["Fire", "Theft", "Collision", "Natural Disaster"], k=num_claims),
    "LossLocationID": [f"LOC{str(i).zfill(4)}" for i in random.choices(range(1000), k=num_claims)],
    "Notes": random.choices([generate_accident_description(),fake.text(max_nb_chars=100)],  k=num_claims),
    # "Notes": [fake.text(max_nb_chars=100) for _ in range(num_claims)],
    "State": random.choices(["Open", "Closed", "Pending"], k=num_claims),
    "Assessment": random.choices(["YES", "NO"], k=num_claims),
    "LossCause_asper_PDS": random.choices(["YES", "NO"], k=num_claims),
})

# Generate Policies Table
policies = pd.DataFrame({
    "ClaimNumber": claims["ClaimNumber"],
    "PolicyNumber": [f"POL{str(i).zfill(6)}" for i in range(1, num_claims + 1)],
    "PolicySource": random.choices(["Online", "Agent", "Broker"], k=num_claims),
    "EffectiveDate": [fake.date_between(start_date='-5y', end_date='today') for _ in range(num_claims)],
    "ExpirationDate": [fake.date_between(start_date='today', end_date='+5y') for _ in range(num_claims)],
    "CancellationDate": [None if random.random() > 0.8 else fake.date_between(start_date='today', end_date='+5y') for _ in range(num_claims)],
    "LossLocationID": claims["LossLocationID"],  # Matching loss location
    "HIPaymentStatus_Ext": random.choices(["Paid", "Pending", "Not Paid"], k=num_claims),
    "Type": random.choices(["Nominated", "Not Nominated"], k=num_claims),
    "Driver": random.choices(["Nominated", "Not Nominated"], k=num_claims),
    "Vehicle": random.choices(["Active", "Not Active"], k=num_claims),
})

# Generate Contacts Table
contacts = pd.DataFrame({
    "ClaimNumber": claims["ClaimNumber"],
    "FirstName": [fake.first_name() for _ in range(num_claims)],
    "LastName": [fake.last_name() for _ in range(num_claims)],
})

# Generate Vehicles Table
vehicles = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_vehicles),
    "ID": [f"VEH{str(i).zfill(5)}" for i in range(1, num_vehicles + 1)],
    "Vin": [fake.bothify(text='??#######??#######') for _ in range(num_vehicles)],
    "Make": random.choices(["Toyota", "Honda", "Ford", "Chevrolet"], k=num_vehicles),
    "Model": random.choices(["Camry", "Civic", "Focus", "Malibu"], k=num_vehicles),
    "Year": [random.randint(2000, 2023) for _ in range(num_vehicles)],
})

# Generate Incidents Table
incidents = pd.DataFrame({
    "ClaimNumber": claims["ClaimNumber"],
    "LossDesc": [fake.text(max_nb_chars=200) for _ in range(num_claims)],
})

# Generate Exposures Table
exposures = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_exposures),
    "ID": [f"EXP{str(i).zfill(5)}" for i in range(1, num_exposures + 1)],
    "HIFinancePayout_Ext": [round(random.uniform(1000, 50000), 2) for _ in range(num_exposures)],
    "CoverageID": [f"COV{str(i).zfill(5)}" for i in range(1, num_exposures + 1)],
    "State": random.choices(["Open", "Closed"], k=num_exposures),
    "RemainingReserves": [round(random.uniform(500, 30000), 2) for _ in range(num_exposures)],
    "AvailableReserves": [round(random.uniform(500, 30000), 2) for _ in range(num_exposures)],
    "Exposure": random.choices(["Correct", "Incorrect"], k=num_exposures),
})

# Generate Transactions Table
transactions = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_transactions),
    "PaymentType": random.choices(["Check", "Direct Deposit", "Credit Card"], k=num_transactions),
    "CostType": random.choices(["Medical", "Vehicle Repair", "Property Damage"], k=num_transactions),
    "CostCategory": random.choices(["Expense", "Indemnity"], k=num_transactions),
    "GrossAmount": [round(random.uniform(100, 50000), 2) for _ in range(num_transactions)],
    "PaymentJustifiedInNotes": random.choices(["YES", "NO"], k=num_transactions),
})

# Generate Notes Table
notes = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_notes),
    "ID": [f"NOTE{str(i).zfill(5)}" for i in range(1, num_notes + 1)],
    "CreateTime": [fake.date_time_between(start_date='-3y', end_date='now') for _ in range(num_notes)],
    "Subject": [fake.sentence(nb_words=6) for _ in range(num_notes)],
})

# Generate Coverage Table
coverages = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_coverages),
    "CoverageLineLimits": [round(random.uniform(10000, 100000), 2) for _ in range(num_coverages)],
    "Type": random.choices(["Liability", "Collision", "Comprehensive"], k=num_coverages),
    "ClaimAggLimit": [round(random.uniform(50000, 200000), 2) for _ in range(num_coverages)],
})

# Generate History Table
history = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_histories),
    "Type": random.choices(["Update", "Approval", "Rejection"], k=num_histories),
    "MatterID": [fake.uuid4() for _ in range(num_histories)],
    "User": [fake.user_name() for _ in range(num_histories)],
    "EventTimestamp": [fake.date_time_between(start_date='-3y', end_date='now') for _ in range(num_histories)],
    "Description": [fake.text(max_nb_chars=100) for _ in range(num_histories)],
})

# Generate Activities Table
activities = pd.DataFrame({
    "ClaimNumber": random.choices(claims["ClaimNumber"], k=num_activities),
    "CreateTime": [fake.date_time_between(start_date='-3y', end_date='now') for _ in range(num_activities)],
    "AssignmentStatus": random.choices(["Assigned", "Unassigned"], k=num_activities),
    "Subject": [fake.sentence(nb_words=6) for _ in range(num_activities)],
    "ExposureID": random.choices(exposures["ID"], k=num_activities),
    "AssignedByUserID": [fake.user_name() for _ in range(num_activities)],
    "AssignedUserID": [fake.user_name() for _ in range(num_activities)],
})

# Save to CSV
claims.to_csv('claims.csv', index=False)
policies.to_csv('policies.csv', index=False)
contacts.to_csv('contacts.csv', index=False)
vehicles.to_csv('vehicles.csv', index=False)
incidents.to_csv('incidents.csv', index=False)
exposures.to_csv('exposures.csv', index=False)
transactions.to_csv('transactions.csv', index=False)
notes.to_csv('notes.csv', index=False)
coverages.to_csv('coverages.csv', index=False)
history.to_csv('history.csv', index=False)
activities.to_csv('activities.csv', index=False)
