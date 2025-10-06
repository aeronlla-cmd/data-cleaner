# This project handles a messy CSV file containing employee data and will clean it up by removing duplicates, handling missing values, validating emails, fix invalid entries on age and salaries, removing spaces and special characters, and standardizing formats including dates and gender values.

import pandas as pd
import re

# Loading the target CSV file
df = pd.read_csv('messy_employee_data.csv')

# Making sure the Employee ID trailing zeros are preserved
df['Employee_ID'] = df['Employee_ID'].astype(str).str.zfill(6)

# Removing duplicates 
df1= df.drop_duplicates()

# Removing all special characters except Hire Date and Email address columns
cols_to_clean = df1.columns.difference(['Hire_Date', 'Email'])
df1[cols_to_clean] = df1[cols_to_clean].replace(r'[^\w\s]', '', regex=True)

# Finding all missing values and replacing them wit "Not provided"
blanks = df1[df1.apply(lambda x: x.astype(str).str.strip().eq('').any(), axis=1)]
df1.fillna('Not provided', inplace=True)

# Proper Capitalization and Removal of trailing spaces of columns Full_Name, Department, and Position
df1['Full_Name'] = df1['Full_Name'].str.strip().str.title()
df1['Department'] = df1['Department'].str.strip().str.title()
df1['Position'] = df1['Position'].str.strip().str.title()

# Normalizing Gender values
for gender_row in df1.index:
    gender = str(df1.at[gender_row, 'Gender']).strip().lower()

    if gender in ['m', 'male', 'man', 'boy']:
        df1.at[gender_row, 'Gender'] = 'Male'
    elif gender in ['f', 'female', 'woman', 'girl']:
        df1.at[gender_row, 'Gender'] = 'Female'
    else:
        df1.at[gender_row, 'Gender'] = 'Not specified'

# Fixing Invalid Age and Salary entries
df1['Age'] = pd.to_numeric(df1['Age'], errors='coerce')
df1['Salary'] = pd.to_numeric(df1['Salary'], errors='coerce')
df1.loc[(df1['Age'] < 18) | (df1['Age'] > 65), 'Age'] = pd.NA
df1.loc[df1['Salary'] <= 0, 'Salary'] = pd.NA   
df1['Age'].fillna('Invalid Data', inplace=True)
df1['Salary'].fillna('Invalid Data', inplace=True)

# Removing Age and Salary Outliers using 0.01 and 0.99 quantiles and replacing them with Invalid Data
df1['Salary'] = pd.to_numeric(df1['Salary'], errors='coerce')
df1['Age'] = pd.to_numeric(df1['Age'], errors='coerce')

def remove_outliers (series, lower_quantile=0.01, upper_quantile=0.99):
     if pd.api.types.is_numeric_dtype(series):
        lower_bound = series.quantile(lower_quantile)
        upper_bound = series.quantile(upper_quantile)
        return series.apply(lambda x: x if lower_bound <= x <= upper_bound else pd.NA)
     return(series)

columns_to_clean = ['Age', 'Salary']

for col in columns_to_clean:
    df1[col] = remove_outliers(df1[col])
    df1[col].fillna('Invalid Data', inplace=True)

# Manually removing all 999999 entries in Salary Column
for col in df1['Salary']:
    for i, val in enumerate(df1['Salary']):
        if pd.api.types.is_numeric_dtype(type(val)) and val > 999_999:
            df1.at[i, 'Salary'] = 'Invalid Data'

# Transforming remaining salary values to USD currency format
def format_usd(value):
    if pd.api.types.is_numeric_dtype(type(value)):
        return "${:,.2f}".format(value)
    return value
df1['Salary'] = df1['Salary'].apply(format_usd)

# Remove trailing .0 if exists in Age column
df1['Age'] = df1['Age'].astype(str).str.rstrip('0').str.rstrip('.')

# Validating Email addresses
pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

df1['Email'] = df1['Email'].astype(str).str.strip().str.replace('"', '')
df1['Email'] = df1['Email'].where(df1['Email'].str.match(pattern), "Invalid email")

# Standardizing Hire Date to YYYY-MM-DD format
df1['Hire_Date'] = pd.to_datetime(df1['Hire_Date'], errors='coerce').dt.strftime('%Y-%m-%d')
df1['Hire_Date'].fillna('Invalid date', inplace=True)

# Saving cleaned data to a new CSV file
df1.to_csv('cleaned_employee_data.csv', index=False)

# Final statements to indicate completion
print("Data cleaning complete.")
print(f"Removed {len(df) - len(df1)} duplicate rows.")