#!python3

from datetime import datetime
from io import StringIO
import json
from lxml import etree
from pathlib import Path
import pytz
import requests
import sys

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class PDFParser:

    def __init__(self, filepath):
        self.filepath = filepath
        self.docket = Docket()

    def parse_file(self):
        output = StringIO()
        with open(self.filepath, 'rb') as pdf_file:
            extract_text_to_fp(pdf_file, output, laparams=LAParams(), output_type='html', codec=None)
            self.tree = etree.parse(StringIO(output.getvalue()), etree.HTMLParser())

    def find_judge(self):
        judge_xpath = "//div/span[contains(text(),'Magisterial District Judge')]/text()"
        path_result = self.tree.xpath(judge_xpath)
        self.docket.judge = path_result[1].strip()

    def find_docket_number(self):
        docket_xpath = "//div/span[contains(text(),'Docket Number')]/text()"
        path_result = self.tree.xpath(docket_xpath)
        self.docket.docket_number = path_result[0].split(':')[1].strip()

    def find_file_date(self):
        tz = pytz.timezone('America/New_York')
        now = datetime.now(tz)
        today = now.strftime("%m/%d/%Y")
        self.docket.file_date = today
        #file_date_xpath = "//div/span[contains(text(),'File Date')]/following::span[4]/text()"
        #path_result = self.tree.xpath(file_date_xpath)
        #self.docket.file_date = path_result[0].strip()

    def find_sex(self):
        sex_xpath = "//div/span[contains(text(),'Sex')]/following::span[2]/text()"
        path_result = self.tree.xpath(sex_xpath)
        self.docket.sex = path_result[0].strip()

    def find_race(self):
        race_xpath = "//div/span[contains(text(),'Race')]/following::span[2]/text()"
        path_result = self.tree.xpath(race_xpath)
        self.docket.race = path_result[0].strip()

    def find_charges(self):
        charges_xpath = "//div/span[contains(text(),'Charge')]/text()[preceding-sibling::br and following-sibling::br] | //div/span[contains(text(),'§')]/text()"
        path_result = self.tree.xpath(charges_xpath)
        self.docket.charges = ';'.join([charge.strip() for charge in path_result])

    def find_bail_type(self):
        bail_type_xpath = "//div/span[contains(text(),'Bail Type')]/following::span/text()"
        path_result = self.tree.xpath(bail_type_xpath)
        self.docket.bail_type = path_result[0].strip()

    def find_bail_amount(self):
        bail_amount_xpath = "//div/span[contains(text(),'Amount')]/text()[preceding-sibling::br and following-sibling::br]|//div/span[contains(text(),'Amount')]/following::span/text()"
        path_result = self.tree.xpath(bail_amount_xpath)
        self.docket.bail_amount = path_result[0].strip()

    def set_url(self):
        url = f"https://ujsportal.pacourts.us/DocketSheets/{self.filepath.stem}"
        self.docket.url = url

    def find_data(self):
        self.find_judge()
        self.find_docket_number()
        self.find_file_date()
        self.find_sex()
        self.find_race()
        self.find_charges()
        self.find_bail_type()
        self.find_bail_amount()
        self.set_url()
        return self.docket



class Docket:
    def __init__(self):
        self.judge = ''
        self.docket_number = ''
        self.file_date = ''
        self.sex = ''
        self.race = ''
        self.charges = ''
        self.bail_type = ''
        self.bail_amount = ''
        self.url = ''

    def __str__(self):
        print_string = f"""
            Judge: {self.judge}
            Docket Number: {self.docket_number}
            File Date: {self.file_date}
            Sex: {self.sex}
            Race: {self.race}
            Charges: {self.charges}
            Bail Type: {self.bail_type}
            Bail Amount: {self.bail_amount}
            URL: {self.url}
        """
        return print_string

    def get_data_dict(self):
        return {    
            'Judge': self.judge,
            'Docket Number': self.docket_number,
            'File Date': self.file_date,
            'Sex': self.sex,
            'Race': self.race,
            'Charges': self.charges,
            'Bail Type': self.bail_type,
            'Bail Amount': self.bail_amount,
            'URL': self.url
            }

class DocketCloudWriter:

    def __init__(self, docket, creds):
        self.docket = docket
        self.url = creds['airtable_url']
        self.api = creds['airtable_api']

    def create_data_load(self):
        fields = self.docket.get_data_dict()
        return {'records': [{'fields':fields}]}
        
    def create_headers(self):
        return {'Authorization': f'Bearer {self.api}', 'Content-Type': 'application/json'}

    def send_request(self):
        data = self.create_data_load()
        headers = self.create_headers()
        response = requests.post(self.url, json=data, headers=headers)
        return response.status_code


if __name__ == "__main__":
    cred_file_path = Path("/home/jackwphillips/projects/bailfund/.creds/credentials.json")
    with open(cred_file_path, 'r') as f:
        creds = json.load(f)

    if len(sys.argv) < 2:
        print("Requires filename as argument")
        sys.exit(1)
    pdf = sys.argv[1]
    path = Path(pdf)
    if not path.is_file():
        print("Could not find file")
        sys.exit(1)

    parser = PDFParser(path)
    parser.parse_file()
    docket = parser.find_data()
    print(docket)
    writer = DocketCloudWriter(docket, creds)
    status = writer.send_request()
    if status != 200:
        print(f"Error uploading data: {status}")
        sys.exit(1)
