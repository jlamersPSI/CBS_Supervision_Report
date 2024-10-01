import Chc  # Import the Chc class from the Chc module
import pdfkit
import io

from PyPDF2 import PdfMerger,  PdfWriter , PdfReader

class CbsReport:
    """
    Represents a CBS (Community-Based Supervision) report for a specific CHC (Community Health Center).
    """

    def __init__(self, chc_name_in: str):
        """
        Initializes a new CBS report object.

        Args:
            chc_name_in (str): The name of the CHC.
        """

        self.chc_name = chc_name_in  # Store the CHC name
        self.chc = Chc.Chc(chc_name)  # Create a Chc object for the specified CHC

        self.pages = []  # Initialize an empty list to store the generated pages

    def gen_front_page(self):
        """
        Generates the front page of the CBS report.
        """
        page_html = ""

        page_html = page_html + self.chc.gen_chc_summary()

        page_html = page_html.replace('CBS Report', f'CBS Report {self.chc_name}')

        self.pages.append(page_html)

    def gen_chw_pages(self):
        """
        Generates pages for each CHW associated with the CHC.
        """
        for chw in self.chc.chw_list:
            self.gen_chw_page(chw)

    def gen_chw_page(self, chw):
        """
        Generates a page for a specific CHW.

        Args:
            chw (Chw): The CHW object.
        """
        page_html = ""  # Initialize an empty string for the page HTML

        # Add the CHW's monthly summary table to the page HTML
        page_html = page_html + chw.gen_monthly_summary_table()

        self.pages.append(page_html)  # Add the generated page to the list of pages

    def to_pdf(self):
        path_to_wkhtmltopdf = r'C:\Users\JLamers.sl\PycharmProjects\CBS_Supervision\wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

        with open(f"./Output/{self.chc_name.replace(' ','_')}_report.pdf", 'wb') as output_file:
            writer =  PdfWriter()

            for page in self.pages:
                stream = io.BytesIO()
                stream.write(pdfkit.from_string(
                    page,
                    False,
                    configuration=config,
                    options={"enable-local-file-access": ""}
                ))
                # This line assumes the string html (or txt) is only 1 page.
                writer.add_page(PdfReader(stream).pages[0])

            writer.write(output_file)

    def gen_report(self):
        """
        Generates the entire CBS report.
        """
        self.gen_front_page()  # Generate the front page
        self.gen_chw_pages()  # Generate the CHW pages

        self.to_pdf()

    def __str__(self):
        """
        Returns a string representation of the CBS report.

        Returns:
            str: A string containing the CHC name and a list of pages.
        """
        return f"CHC: {self.chc}, Pages: {self.pages}"

# Ask the user to enter the CHC name
chc_name = input("Please enter the name of the Community Health Center (CHC): ")

# Store the result and print a confirmation message
print(f"CHC name '{chc_name}' has been stored.")

# Create a CBS report object
cbs_report = CbsReport(chc_name)

# Generate the report
cbs_report.gen_report()

# Print the CBS report
#print(cbs_report)