import matplotlib.pyplot as plt
import pandas as pd  # Import the Pandas library for data manipulation
import os  # Import the OS module for file system operations
import Chw
import numpy as np

from bs4 import BeautifulSoup  # Import the Beautiful Soup library for HTML parsing
from datetime import datetime, timedelta

def get_dict_of_chws(chc_name: str) -> list:
    """
    Retrieves a list of dictionaries containing CHW information for a given CHC.

    Args:
        chc_name (str): The name of the CHC.

    Returns:
        list: A list of dictionaries, each containing "Organisation unit" and "CHW" keys.

    Raises:
        FileNotFoundError: If the 'org_hierarchy.csv' file is not found.
        ValueError: If the provided CHC name is not valid in DHIS2.
    """

    # Check if the 'org_hierarchy.csv' file exists
    if not os.path.exists('./Data/org_hierarchy.csv'):
        raise FileNotFoundError("File 'org_hierarchy.csv' not found in the './Data' directory.")

    # Read the CSV file into a Pandas DataFrame
    org_hierarchy = pd.read_csv('./Data/org_hierarchy.csv')

    # Check if the provided CHC name exists in the DataFrame
    if not any(chc_name in clinic_name for clinic_name in org_hierarchy["Clinic"]):
        raise ValueError(f"{chc_name} is not a valid clinic name in DHIS2.")

    # Filter the DataFrame for the specified CHC and return the results as a list of dictionaries
    return org_hierarchy.loc[org_hierarchy["Clinic"] == chc_name, ["Organisation unit", "CHW"]].to_dict('records')

class Chc:
    """Represents a CHC (Community Health Center) with associated CHW information."""

    def __init__(self, chc_name: str):
        """
        Initializes a new CHC object.

        Args:
            chc_name (str): The name of the CHC.
        """

        self.chc_name = chc_name  # Store the CHC name

        # Retrieve the CHW information for the specified CHC
        self.chw_names = get_dict_of_chws(self.chc_name)

        self.chw_list = [Chw.Chw(chw_name["Organisation unit"], chw_name["CHW"]) for chw_name in self.chw_names]

    def gen_chc_summary(self):
        # Load the HTML template for the CHW page
        with open("./Form_Templates/Front_Page.html", "r") as f:
            soup = BeautifulSoup(f, "lxml")

        rr_df = pd.DataFrame()

        # Get the current date and find the start of the previous month
        current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = current_date - timedelta(days=1)
        start_date = last_month.replace(day=1)

        # Generate a list of dates for the last 12 months
        date_list = [(start_date - timedelta(days=30 * i)).replace(day=1) for i in range(11, -1, -1)]

        # Create a DatetimeIndex
        datetime_index = pd.DatetimeIndex(date_list)

        rr_df = pd.DataFrame(index=datetime_index)

        rr_df["Actual_Reports"] = 0
        rr_df["Actual_Reports_On_Time"] = 0
        rr_df["Expected_Reports"] = 0

        for chw in self.chw_list:
            rr_df["Actual_Reports"] = rr_df["Actual_Reports"] + chw.get_actual_reports()["ACTUAL_REPORTS"]
            rr_df["Actual_Reports_On_Time"] = rr_df["Actual_Reports_On_Time"] + chw.get_actual_reports_on_time()["ACTUAL_REPORTS_ON_TIME"]
            rr_df["Expected_Reports"] = rr_df["Expected_Reports"] + chw.get_expected_reports()["EXPECTED_REPORTS"]


        print(rr_df)

        rr_df["Reporting_Rate"] = rr_df["Actual_Reports"] / rr_df["Expected_Reports"]
        rr_df["On_Time_Reporting_Rate"] = rr_df["Actual_Reports_On_Time"] / rr_df["Expected_Reports"]

        fig, ax = plt.subplots()

        rr_df["Reporting_Rate"].plot(ax=ax, label="RR")
        rr_df["On_Time_Reporting_Rate"].plot(ax=ax, label="OTRR")

        plt.savefig(f'./Output/{self.chc_name.replace(" ", "_")}_RR_plot.jpg')

        image_element = soup.find('img', id='reporting-plot')

        # If the image element exists, update its src attribute
        if image_element:
            print(f'{os.getcwd()}/Output/{self.chc_name.replace(" ", "_")}_RR_plot.jpg')
            new_src = f'{os.getcwd()}/Output/{self.chc_name.replace(" ", "_")}_RR_plot.jpg'  # Replace with the desired new image URL
            image_element['src'] = new_src
            image_element['alt'] = "Reporting Rate Plot"

        return str(soup)

    def __str__(self):
        """
        Returns a string representation of the CHC object.

        Returns:
            str: A string containing the CHC name and a list of CHW names.
        """

        return f"Name: {self.chc_name}, CHW's: {[chw['CHW'] for chw in self.chw_names]}"