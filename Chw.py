import pandas as pd  # Import the Pandas library for data manipulation
import json  # Import the JSON library for working with JSON data

from bs4 import BeautifulSoup  # Import the Beautiful Soup library for HTML parsing

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
        with open('./Data/clean_CBS_data.json', 'r') as f:
            cbs_data_all_chws = json.load(f)

        # Check if the CHW's organization unit is valid
        if not any(self.organisation_unit in org_unit_key for org_unit_key in cbs_data_all_chws.keys()):
            raise ValueError(f"CHW {self.organisation_unit} is not a valid CHW org unit in DHIS2.")

        # Load the CHW's data into a Pandas DataFrame
        self.chw_data = pd.DataFrame(cbs_data_all_chws[self.organisation_unit]["data"])

    def gen_monthly_summary_table(self) -> str:
        """
        Generates a monthly summary table for the CHW.

        Returns:
            str: The HTML content of the generated table.
        """

        # Load the HTML template for the CHW page
        with open("./Form_Templates/CHW_PAGE_TEMPLATE.html", "r") as f:
            soup = BeautifulSoup(f, "lxml")

        # Iterate over the CHW's data and update the corresponding elements in the HTML
        for indicator in self.chw_data.columns:
            #if '&' in indicator:
            #    indicator = indicator.replace('&', 'and')
            #    print(indicator)

            element = soup.find('div', id=indicator)

            if element:
                # Replace the text content of the element with the new value
                element.string = f"{element.text.strip()} {self.chw_data.loc[self.chw_data.index[-1], indicator]}"
            else:
                print(f"Element with ID '{indicator}' not found.")

        # Return the HTML content as a string
        return str(soup)

    def get_expected_reports(self):
        df = pd.DataFrame(self.chw_data["EXPECTED_REPORTS"])
        df.index = pd.to_datetime(self.chw_data["index"], format="%Y%m")
        return df

    def get_actual_reports(self):
        df = pd.DataFrame(self.chw_data["ACTUAL_REPORTS"])
        df.index = pd.to_datetime(self.chw_data["index"], format="%Y%m")
        return df

    def get_actual_reports_on_time(self):
        df = pd.DataFrame(self.chw_data["ACTUAL_REPORTS_ON_TIME"])
        df.index = pd.to_datetime(self.chw_data["index"], format="%Y%m")
        return df

    def __str__(self):
        """
        Returns a string representation of the CHW object.

        Returns:
            str: A string containing the CHW's organization unit and ID.
        """
        return f"CHW: {self.organisation_unit} ({self.chw_id})"