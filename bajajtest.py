import json
import pandas as pd
from datetime import datetime

# Load the JSON data
with open('/content/DataEngineeringQ2.json', 'r') as f:
    data = json.load(f)

# Convert JSON data into a DataFrame
df = pd.json_normalize(data, max_level=1)

# patientDetails columns
df['firstName'] = df['patientDetails.firstName'].fillna('')
df['lastName'] = df['patientDetails.lastName'].fillna('')
df['birthDate'] = pd.to_datetime(df['patientDetails.birthDate'], errors='coerce')
df['gender'] = df['patientDetails.gender'].fillna('')

# Extract medicines
# Each record has a list of medicines under consultationData.medicines
# We can count how many medicines each patient has
df['medicines'] = df['consultationData.medicines'].apply(lambda x: x if isinstance(x, list) else [])
df['medicine_count'] = df['medicines'].apply(len)

# ---------------------------
# QUESTION 10:
# Check if phone numbers are valid Indian phone numbers
# Conditions:
# - Valid format: optional +91 or 91 prefix
# - After removing prefix, must be a 10-digit number between 6000000000 and 9999999999

def is_valid_phone(num_str):
    if not isinstance(num_str, str) or num_str.strip() == '':
        return False
    num_str = num_str.strip()
    # Remove +91 or 91 prefix if present
    if num_str.startswith('+91'):
        num_str = num_str[3:]
    elif num_str.startswith('91') and len(num_str) > 2:
        num_str = num_str[2:]
    
    # Now num_str should be 10 digits
    if len(num_str) != 10 or not num_str.isdigit():
        return False
    
    # Check range
    num_val = int(num_str)
    if 6000000000 <= num_val <= 9999999999:
        return True
    return False

df['phoneNumber'] = df['phoneNumber'].fillna('')
df['isValidMobile'] = df['phoneNumber'].apply(is_valid_phone)

valid_count = df['isValidMobile'].sum()
print("Answer Q10 - Count of valid phone numbers:", valid_count)

# ---------------------------
# QUESTION 11:
# Pearson correlation between number of prescribed medicines and patient's age
# Age calculation: Use year 2023 as reference (or current year). Only consider rows with valid DOB.
current_year = 2023
df['age'] = df['birthDate'].apply(lambda d: current_year - d.year if pd.notnull(d) else None)

# Filter to have both age and medicine_count
valid_df = df.dropna(subset=['age'])
# Compute correlation
corr = valid_df['medicine_count'].corr(valid_df['age'])
# Round to 2 decimals
corr_rounded = round(corr, 2)
print("Answer Q11 - Pearson correlation between medicines count and age:", corr_rounded)

# ---------------------------
# For completeness, if you needed previous answers as code (not requested now, but included for reference):

# Q4 - Percentage of missing values for firstName, lastName, DOB
total = len(df)
missing_firstName = sum(df['firstName'] == '')
missing_lastName = sum(df['lastName'] == '')
missing_birthDate = sum(df['birthDate'].isna())
perc_firstName = (missing_firstName/total)*100
perc_lastName = (missing_lastName/total)*100
perc_birthDate = (missing_birthDate/total)*100
print("Q4:", f"{perc_firstName:.2f},{perc_lastName:.2f},{perc_birthDate:.2f}")

# Q5 - Percentage of female after imputing missing genders with mode
# mode gender
non_empty_genders = df.loc[df['gender'] != '', 'gender']
if len(non_empty_genders) > 0:
    mode_gender = non_empty_genders.mode()[0]
else:
    mode_gender = 'M' # default if none present
df['gender_imputed'] = df['gender'].apply(lambda g: g if g != '' else mode_gender)
female_count = sum(df['gender_imputed'] == 'F')
perc_female = (female_count/total)*100
print("Q5:", f"{perc_female:.2f}")

# Q6 - Count of Adults (20–59)
adults = sum((df['age'] >= 20) & (df['age'] <= 59))
print("Q6 (Count of Adults):", adults)

# Q7 - Average number of medicines
avg_meds = df['medicine_count'].mean()
print("Q7:", f"{avg_meds:.2f}")

# Q8 - 3rd most frequently prescribed medicineName
# Flatten out all medicines and count
all_meds = []
for row in df['medicines']:
    for med in row:
        all_meds.append(med.get('medicineName', ''))

from collections import Counter
med_counter = Counter(all_meds)
# Sort by frequency
freq = med_counter.most_common()
# freq is a list of tuples (medicine, count)
# Determine the 3rd most frequent:
# If there's a tie, handle accordingly. For simplicity, just pick the third in sorted order.
# If the tie scenario from previous logic is needed, implement it. For demonstration:
third_most = freq[2][0] if len(freq) > 2 else None
print("Q8:", third_most)

# Q9 - Percentage distribution of total active and inactive medicines
active_count = 0
inactive_count = 0
for row in df['medicines']:
    for med in row:
        if med.get('isActive', False):
            active_count += 1
        else:
            inactive_count += 1
if (active_count + inactive_count) > 0:
    perc_active = (active_count/(active_count+inactive_count))*100
    perc_inactive = (inactive_count/(active_count+inactive_count))*100
    print("Q9:", f"{perc_active:.2f},{perc_inactive:.2f}")
else:
    print("Q9: No medicines found")

