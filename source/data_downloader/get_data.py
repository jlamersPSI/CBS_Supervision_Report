import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
import json

from io import StringIO
from datetime import datetime
from dhis2 import Api
from get_credentials import get_credentials

def query_api(
    api,
    period,
    indicator_id,
    level
):
    # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
    query_string = (
        f'analytics.csv?dimension=pe:{period}'  # Add period dimension
        f'&dimension=dx:{indicator_id}'  # Add data element group dimension
        f'&dimension=ou:{level};'  # Add organizational unit dimension
    )

    # Step 5: Fetch the data from DHIS2 API using the constructed query string
    response = api.get(query_string)

    # Step 6: Load the API response into a pandas DataFrame
    # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
    df = pd.read_csv(StringIO(response.text))

    return df

# Step 1: Get credentials (username and password) to authenticate the API connection
username, password = get_credentials()

# Step 2: Initialize the API connection to DHIS2 using the given credentials
api = Api('https://sl.dhis2.org/hmis23', username, password)

# Open and read the JSON file
with open('HF04_indicators.json', 'r') as file:
    indicator_ids = json.load(file)

# Dictionary to store DataFrames for each organization unit
org_unit_dfs = {}

# Counter for iterations
i = 0

# Iterate through the dictionary of data elements
for key, id in tqdm(indicator_ids.items()):
    if len(id) < 1:
        pass

    print(key)

    # Fetch data for the current data element
    df = query_api(
        api,
        "LAST_12_MONTHS",
        id,
        "LEVEL-6"
    )

    # Group the DataFrame by 'Organisation unit'
    grouped = df.groupby('Organisation unit')

    # First iteration: Set up the index for all DataFrames
    if i == 0:
        # Get the date from 30 days ago
        current_date = datetime.now() - timedelta(days=30)

        # Create a list of the last 12 months
        last_12_months = [current_date - timedelta(days=30 * i) for i in range(12)]
        last_12_months.sort()

        # Create the index using the month and year of each date
        index = [date.strftime("%Y%m") for date in last_12_months]

        # Initialize DataFrames for each organization unit
        for org_unit, _ in tqdm(grouped):
            org_unit_dfs[org_unit] = pd.DataFrame(index=index)

    i += 1

    # Process data for each organization unit
    for org_unit, group_data in tqdm(grouped):
        try:
            group_data.reset_index(inplace=True)

            # Initialize the column for the current data element with NaN
            org_unit_dfs[org_unit][key] = np.nan

            # Convert Period to datetime index
            group_data.index = pd.to_datetime([datetime.strptime(str(i), "%Y%m") for i in group_data["Period"]], format="%Y-%m-%d").strftime("%Y%m")

            # Update the DataFrame with values from the current data element
            org_unit_dfs[org_unit][key] = org_unit_dfs[org_unit][key].astype(object)
            org_unit_dfs[org_unit].loc[group_data.index, key] = group_data["Value"]

        except Exception as e:
            print(f"Error processing {org_unit}: {e}")

# Ensure all data elements are present in all DataFrames
for org_unit, group_data in org_unit_dfs.items():
    for key in indicator_ids:
        if key not in group_data.columns:
            org_unit_dfs[org_unit][key] = np.nan

# Print information about the resulting DataFrames
for org_unit, df in org_unit_dfs.items():
    print(f"Organization Unit: {org_unit}")
    print(df)
    print(f"Shape: {df.shape}")
    break  # Remove this line to print all DataFrames

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def dataframe_to_dict(df):
    """Converts a pandas DataFrame to a dictionary."""
    try:
        # Convert datetime columns and index to strings
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        df[datetime_cols] = df[datetime_cols].astype(str)
        df.index = df.index.astype(str)

        return {
            'index': df.index.tolist(),
            'columns': df.columns.tolist(),
            'data': df.reset_index().to_dict(orient='records')
        }
    except Exception as e:
        print(f"Error converting DataFrame to dictionary: {e}")
        return None

# Convert each DataFrame in the dictionary to a JSON-serializable format
json_dict = {key: dataframe_to_dict(df) for key, df in org_unit_dfs.items()}

# Save the dictionary as a JSON file
with open('dataframes.json', 'w') as f:
    json.dump(json_dict, f)

#for key, id in indicator_ids.items():
