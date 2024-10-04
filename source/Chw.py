import pandas as pd  # Import the Pandas library for data manipulation
import json  # Import the JSON library for working with JSON data
import ValidationCheck as ValidationCheck
import os
import numpy as np

from bs4 import BeautifulSoup  # Import the Beautiful Soup library for HTML parsing
from collections import defaultdict

with open(rf'{os.getcwd().replace('\test','')}\Data\HF04_indicators.json', 'r') as file:
    HF04_indicators = json.load(file)

with open(rf'{os.getcwd().replace('\test','')}\Data\org_unit_name_to_dhis2_code.json', 'r') as file:
    org_unit_name_to_dhis2_code = json.load(file)

def parse_data(data_array):
    parsed_data = defaultdict(dict)
    for item in data_array:
        column_name = list(HF04_indicators.keys())[list(HF04_indicators.values()).index(item[0])]
        index = item[1] # Using the third item as index
        if item[3].isdigit():
            value = float(item[3])
        else:
            value = item[3]
        parsed_data[index][column_name] = value
    return parsed_data

def create_dataframe(parsed_data):
    df = pd.DataFrame.from_dict(parsed_data, orient='index')

    empty_columns_to_add = []

    for indicator in HF04_indicators.keys():
        if indicator not in df.columns:
            empty_columns_to_add.append(indicator)

    empty_columns_df = pd.DataFrame(columns=empty_columns_to_add,index=df.index)

    df = pd.concat([df,empty_columns_df],axis=1)

    return df

def decode_org_hierarchy(org_hierarchy_str):
    org_hierarchy_codes = org_hierarchy_str.split('/')
    org_hierarchy_names = []

    for org_code in org_hierarchy_codes:
        for org_unit in org_unit_name_to_dhis2_code["organisationUnits"]:
            if org_unit["id"] == org_code:
                org_hierarchy_names.append(org_unit["displayName"])

    return org_hierarchy_names


class Chw:
    """
    Represents a CHW (Community Health Worker) with associated data.
    """

    def __init__(self, org_unit: str, chw_id: str):
        """
        Initializes a new CHW object.

        Args:
            org_unit (str): The CHW's organization unit.
            chw_id (str): The CHW's ID.
        """

        self.organisation_unit = org_unit  # Store the organization unit
        self.chw_id = chw_id  # Store the CHW ID

        # Load the CBS data from the JSON file
        with open(rf'{os.getcwd().replace('\test','')}\Data\chw_data.json', 'r') as f:
            cbs_data_all_chws = json.load(f)

        # Check if the CHW's organization unit is valid
        if not any(self.organisation_unit in org_unit_key for org_unit_key in cbs_data_all_chws.keys()):
            raise ValueError(f"CHW {self.organisation_unit} is not a valid CHW org unit in DHIS2.")

        # Load the CHW's data into a Pandas DataFrame
        self.chw_data = create_dataframe(parse_data(cbs_data_all_chws[self.organisation_unit]["rows"]))

        self.chw_data[[
            "National",
            "District",
            "Council",
            "Chiefdom",
            "Clinic",
            "CHW"
        ]] = decode_org_hierarchy(f"{cbs_data_all_chws[self.organisation_unit]["metaData"]["ouHierarchy"][self.organisation_unit]}/{self.organisation_unit}")

        self.chw_data.index = pd.to_datetime(self.chw_data.index, format="%Y%m")
        self.chw_data.sort_index(inplace=True)

        self.validation_check = ValidationCheck.ValidationCheck(self.chw_data)


    def gen_monthly_summary_table(self) -> str:
        """
        Generates a monthly summary table for the CHW.

        Returns:
            str: The HTML content of the generated table.
        """

        # Load the HTML template for the CHW page
        with open(rf'{os.getcwd().replace('\test','')}\Form_Templates\CHW_PAGE_TEMPLATE.html', "r") as f:
            soup = BeautifulSoup(f, "lxml")

        # Iterate over the CHW's data and update the corresponding elements in the HTML
        for indicator in self.chw_data.columns:
            #if '&' in indicator:
            #    indicator = indicator.replace('&', 'and')
            #    print(indicator)

            element = soup.find('div', id=indicator)

            if element:
                element.parent['style'] = f"background-color: {self.validation_check.get_val_check_result_colors_df()[f"{indicator}_Validation_Check"][self.validation_check.get_val_check_result_colors_df().index[-1]]};"
                element.string = f"{element.text.strip()} {self.chw_data.loc[self.chw_data.index[-1], indicator]}"
            else:
                print(f"Element with ID '{indicator}' not found.")

        # Return the HTML content as a string
        return str(soup)

    def get_indicator(self, indicator):
        return self.chw_data[indicator]

    def get_val_check(self):
        return self.validation_check.get_val_check_one()

    def __str__(self):
        """
        Returns a string representation of the CHW object.

        Returns:
            str: A string containing the CHW's organization unit and ID.
        """
        return f"CHW: {self.organisation_unit} ({self.chw_id})"