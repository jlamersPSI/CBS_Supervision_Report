import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import Chw  # Assuming this is a custom module

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
    file_path = './Data/org_hierarchy.csv'
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    org_hierarchy = pd.read_csv(file_path)

    if not any(chc_name in clinic_name for clinic_name in org_hierarchy["Clinic"]):
        raise ValueError(f"{chc_name} is not a valid clinic name in DHIS2.")

    return org_hierarchy.loc[org_hierarchy["Clinic"] == chc_name, ["Organisation unit", "CHW"]].to_dict('records')

class Chc:
    """Represents a CHC (Community Health Center) with associated CHW information."""

    def __init__(self, chc_name: str):
        """
        Initializes a new CHC object.

        Args:
            chc_name (str): The name of the CHC.
        """
        self.chc_name = chc_name
        self.chw_names = get_dict_of_chws(self.chc_name)
        self.chw_list = [Chw.Chw(chw_name["Organisation unit"], chw_name["CHW"]) for chw_name in self.chw_names]

    def gen_chc_rr_plot(self, soup):
        """
        Generates a reporting rate plot for the CHC and updates the HTML.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML.

        Returns:
            BeautifulSoup: The updated BeautifulSoup object.
        """
        # Calculate date range for the last 12 months
        current_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_date = (current_date - timedelta(days=1)).replace(day=1) - timedelta(days=30 * 11)
        date_list = [(start_date + timedelta(days=30 * i)).replace(day=1) for i in range(12)]

        # Initialize DataFrame for reporting rates
        datetime_index = pd.DatetimeIndex(date_list)

        # Initialize DataFrame for reporting rates
        rr_df = pd.DataFrame(index=datetime_index, columns=["Actual_Reports", "Actual_Reports_On_Time", "Expected_Reports"])
        rr_df[["Actual_Reports", "Actual_Reports_On_Time", "Expected_Reports"]] = 0

        # Aggregate data from all CHWs
        for chw in self.chw_list:
            rr_df["Actual_Reports"] += chw.get_actual_reports()["ACTUAL_REPORTS"]
            rr_df["Actual_Reports_On_Time"] += chw.get_actual_reports_on_time()["ACTUAL_REPORTS_ON_TIME"]
            rr_df["Expected_Reports"] += chw.get_expected_reports()["EXPECTED_REPORTS"]

        # Calculate reporting rates
        rr_df["Reporting_Rate"] = (rr_df["Actual_Reports"] / rr_df["Expected_Reports"]) * 100
        rr_df["On_Time_Reporting_Rate"] = (rr_df["Actual_Reports_On_Time"] / rr_df["Expected_Reports"]) * 100

        # Create the plot
        fig, ax = plt.subplots()
        rr_df["Reporting_Rate"].plot(ax=ax, label="RR")
        rr_df["On_Time_Reporting_Rate"].plot(ax=ax, label="OTRR")

        # Customize the plot
        ax.set_title(f'Reporting Rate for {self.chc_name}')
        ax.set_yticks(np.arange(0, 101, 20))
        ax.set_ylabel('% Reporting Rate')
        ax.set_xticks(rr_df.index, [i.strftime('%m/%Y') for i in rr_df.index], rotation=45)
        ax.legend()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        plt.tight_layout()

        # Save the plot
        output_filename = f'./Output/{self.chc_name.replace(" ", "_")}_RR_plot.jpg'
        plt.savefig(output_filename)

        # Update the HTML
        image_element = soup.find('img', id='reporting-plot')
        if image_element:
            image_element['src'] = os.path.abspath(output_filename)
            image_element['alt'] = "Reporting Rate Plot"

        return soup

    def gen_excutive_summary(self, soup):

        element = soup.find('div',id='District')
        if element:
            element.string = self.chw_list[0].get_indicator('District')['District'].unique()[0]
        else:
            print('Element for District not found in gen_excutive_summary()')

        element = soup.find('div', id='Chiefdom')
        if element:
            element.string = self.chw_list[0].get_indicator('Chiefdom')['Chiefdom'].unique()[0]
        else:
            print('Element for Chiefdom not found in gen_excutive_summary()')

        element = soup.find('div', id='Number_of_CHWs')
        if element:
            element.string = str(len(self.chw_list))
        else:
            print('Element for Number of CHWs not found in gen_excutive_summary()')

        element = soup.find('div', id="Number_of_CHW's_Passing_Data_Validation_Checks_title")
        if element:
            element.string = element.string.replace(':', f" {self.chw_list[0].get_indicator('District').index[-1].strftime('%B')}:")
        else:
            print('Element for Number of CHWs not found in gen_excutive_summary()')

        element = soup.find('div', id='Average_Number_of_Households_Registered_in_CHW_Areas')
        if element:
            HH_list = []

            for chw in self.chw_list:
                HH_df = chw.get_indicator('Total_HH_in_CHW_area')
                HH_list.append(HH_df.loc[HH_df.index[-1],'Total_HH_in_CHW_area'])

            HH_list = np.array(HH_list)

            element.string = str(np.round(np.nanmean(HH_list),0))
        else:
            print('Element for Number of CHWs not found in gen_excutive_summary()')

        element = soup.find('h3', id='Most_recent_reporting_period_rr_data')
        if element:
            element.string = element.string.replace('for',f"for {self.chw_list[0].get_indicator('District').index[-1].strftime('%B')}")

            rr_summary_df = pd.DataFrame(columns=["CHW","CHW/PS_name/code","ACTUAL_REPORTS", "ACTUAL_REPORTS_ON_TIME", "EXPECTED_REPORTS", "REPORTING_RATE","REPORTING_RATE_ON_TIME"])

            for chw in self.chw_list:
                row = []

                for column in rr_summary_df.columns:
                    indicator_df = chw.get_indicator(column)

                    if not indicator_df.empty:
                        row.append(indicator_df.iloc[-1][column])

                    else:
                        row.append(None)

                rr_summary_df.loc[len(rr_summary_df)] = row

            rr_summary_df["CHW"] = [CHW.replace(f'{self.chc_name} - ', '') for CHW in rr_summary_df["CHW"]]

            # Convert DataFrame to HTML and insert after the element
            html_table = rr_summary_df.to_html(index=False, classes='table table-striped')
            element.insert_after(BeautifulSoup(html_table, 'html.parser'))
        else:
            print('Element for Executive summary not found in gen_excutive_summary()')

        return soup

    def gen_rr_data_table(self, soup):
        return soup

    def gen_chc_summary(self):
        """
        Generates a summary HTML for the CHC.

        Returns:
            str: The HTML string containing the CHC summary.
        """
        with open("./Form_Templates/Front_Page.html", "r") as f:
            soup = BeautifulSoup(f, "lxml")

        soup = self.gen_chc_rr_plot(soup)
        soup = self.gen_excutive_summary(soup)
        soup = self.gen_rr_data_table(soup)

        return str(soup)

    def __str__(self):
        """
        Returns a string representation of the CHC object.

        Returns:
            str: A string containing the CHC name and a list of CHW names.
        """
        return f"Name: {self.chc_name}, CHW's: {[chw['CHW'] for chw in self.chw_names]}"