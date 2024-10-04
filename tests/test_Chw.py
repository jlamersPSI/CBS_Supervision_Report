import numpy as np
import source.Chw as chw
import pandas as pd
import os
import dhis2
import random
import json
import settings as settings

from io import StringIO
from datetime import datetime, timedelta

org_hierarchy = pd.read_csv(rf'{os.getcwd().replace('\test','')}\Data\org_hierarchy.csv')

username, password = settings.get_credentials()

# Initialize the API connection to DHIS2 using the given credentials
api = dhis2.Api('https://sl.dhis2.org/hmis23', str(username), str(password))

def test__init__data():
    chw_codes_to_test = [
        "QRARQZAjdOl",
        "AvYVcWhbYhK",
        "CRi219fh6Ul",
        "f8sJjvV7wrS",
        "RbC5NnISr7C"
    ]

    for chw_code in chw_codes_to_test:
        chw_id = org_hierarchy.loc[org_hierarchy["Organisation unit"] == chw_code,"CHW"]

        chw_to_test = chw.Chw(chw_code,chw_id)

        indicator_to_test = random.choice(chw_to_test.chw_data.columns)

        with open(rf'{os.getcwd().replace('\test','')}\Data\HF04_indicators.json', 'r') as file:
            indicator_to_code = json.load(file)

        # Get the current date
        current_date = datetime.now() - timedelta(days=30)

        # Create a list of the last 12 months
        last_12_months = [current_date - timedelta(days=30 * i) for i in range(12)]

        # Sort the list in ascending order
        last_12_months.sort()

        # Create the index using the month and year of each date
        index = [date.strftime("%Y%m") for date in last_12_months]

        dhis2_result = pd.DataFrame(index=pd.to_datetime(index, format="%Y%m"))

        dhis2_result["Value"] = np.nan

        data_element = indicator_to_code.get(indicator_to_test)

        period = 'LAST_12_MONTHS'  # Define the time period as the last month

        # Step 4: Build the query string for DHIS2 analytics API to retrieve the required data
        query_string = (
            f'analytics.csv?dimension=pe:{period}'  # Add period dimension
            f'&dimension=dx:{data_element}'  # Add data element group dimension
            f'&dimension=ou:{chw_code};'  # Add organizational unit dimension
        )

        # Step 5: Fetch the data from DHIS2 API using the constructed query string
        response = api.get(query_string)

        # Step 6: Load the API response into a pandas DataFrame
        # The response text is assumed to be in CSV format, so we use StringIO to treat it as a file-like object
        df_chc_RR = pd.read_csv(StringIO(response.text))

        df_chc_RR.index = pd.to_datetime(df_chc_RR["Period"], format="%Y%m")

        df_chw_data = pd.DataFrame(
            chw_to_test.chw_data[indicator_to_test],
            index=pd.to_datetime(chw_to_test.chw_data["index"], format="%Y%m")
        )

        dhis2_result.loc[dhis2_result.index.intersection(df_chc_RR.dropna().index),"Value"] = df_chc_RR.dropna()["Value"]

        print(dhis2_result)
        print(df_chw_data)

        assert dhis2_result["Value"].equals(df_chw_data)




def test_gen_monthly_summary_table():
    pass

def test_get_indicator():
    pass

def test_get_val_check():
    pass

def test__str__():
    pass