import sys
import datetime
from dateutil.relativedelta import relativedelta
import calendar
import requests
import os
from dotenv import load_dotenv
from collections import namedtuple

load_dotenv()

Holiday = namedtuple("Holiday", "month day")
HOLIDAYS = [
    Holiday(month=1, day=1),
    Holiday(month=1, day=6),
    Holiday(month=5, day=1),
    Holiday(month=5, day=3),
    Holiday(month=5, day=28),
    Holiday(month=6, day=8),
    Holiday(month=8, day=15),
    Holiday(month=11,day=1),
    Holiday(month=11,day=11),
    Holiday(month=12,day=25),
    Holiday(month=12,day=26),
]

# Set issue_date, payment_to, seller_name etc. automatically
# Make a constant salary based on 168 hours and if it's different than 168h calculate proper sallary for the month
# In short: Expect amount of hours as an argument
class LocalInvoiceGenerator:
    MONTHLY_SALARY = 15000
    HOURS_IN_MONTH = 168
    TAX_PERCENT = 23

    def __init__(self):
        pass

    def _get_api_token(self):
        return os.environ["API_TOKEN"]

    def _get_api_url(self):
        return os.environ["API_URL"]

    def _get_workdays_this_month(self, today=datetime.date.today()):
        """Return amount of workdays in current month"""
        _, last_day = calendar.monthrange(today.year, today.month)

        month_workdays = 0
        # Go through all days in the month
        for day in range(last_day, 0, -1):
            date = datetime.date(today.year, today.month, day)
            if self._is_weekday(date) and not self._is_holiday(date):
                month_workdays += 1

        return month_workdays

    def read_amount_of_hours(self):
        """
        Return amount of hours for this month.
        It might be explicitly passed as the first argument.
        Otherwise the script has to calculate the amount of working days this month.
        """
        script_argument = sys.argv[1]
        if script_argument.isdigit():
            return int(script_argument)
        elif script_argument == "--auto":
            workdays = self._get_workdays_this_month()
            return 8*workdays
        else:
            raise ValueError(
                "Script argument can be either a positive number or '--auto' flag!\n\nExample: python3 main.py 100"
            )

    def _is_weekday(self, date):
        """Checks if date of datetime.date is day of the week (0-4)"""
        return datetime.date.weekday(date) < 5

    def _is_holiday(self, date):
        for holiday in HOLIDAYS:
            if holiday.month == date.month and holiday.day == date.day:
                return True
        return False

    def _get_yesterday(self, date):
        """Returns the date of yesterday"""
        return date - relativedelta(days=1)

    def _get_last_working_day_of_this_month(self, date=datetime.date.today()):
        """Returns datetime.date object with a date of last working day of this month"""

        today = datetime.date.today() if not date else date
        _, last_day = calendar.monthrange(today.year, today.month)
        date_of_last_day = datetime.date(today.year, today.month, last_day)

        while not self._is_weekday(date_of_last_day):
            date_of_last_day = self._get_yesterday(date_of_last_day)

        return date_of_last_day

    def _get_payment_deadline_date(self, days_to_pay=21, date=None):
        if days_to_pay < 7:
            raise ValueError(
                "You should give the buyer at least 7 days to pay. Come on, have some feelings! :)"
            )
        
        if not date:
            date = self._get_last_working_day_of_this_month()

        return date + relativedelta(days=days_to_pay)

    def _format_date_properly(self, date):
        return date.strftime("%Y-%m-%d")

    def _print_help(self):
        print(
            """ 
LOCAL INVOICE GENERATOR

Usage: python3 main.py [WORKED_HOURS | '--auto']
Examples: 

python3 main.py 168 # Create an invoice with 168 hours worked this month
python3 main.py --auto # Create an invoice with automatically calculated hours for this month (all workdays)
        """
        )

    def _return_salary_based_on_hours(self, hours: int):
        return (
            self.MONTHLY_SALARY
            if hours == self.HOURS_IN_MONTH
            else round((self.MONTHLY_SALARY / self.HOURS_IN_MONTH) * hours, 0)
        )

    def _generate_json_payload_for_api(self, amount: float):
        """
        Method returns json with proper payload with filled fields to be sent to the API.
        API docs: https://app.fakturownia.pl/api
        """
        payload = {
            "api_token": self._get_api_token(),
            "invoice": {
                "kind": "vat",
                "number": None,
                "sell_date": self._format_date_properly(
                    self._get_last_working_day_of_this_month()
                ),
                "issue_date": self._format_date_properly(
                    self._get_last_working_day_of_this_month()
                ),
                "payment_to": self._format_date_properly(
                    self._get_payment_deadline_date(days_to_pay=21)
                ),
                "seller_name": os.environ['SELLER_NAME'],
                "seller_tax_no": os.environ['SELLER_TAX_NUMBER'],
                "buyer_name": os.environ['BUYER_NAME'],
                "buyer_tax_no": os.environ['BUYER_TAX_NUMBER'],
                "positions": [
                    {
                        "name": os.environ['PRODUCT_NAME'],
                        "tax": self.TAX_PERCENT,
                        "total_price_gross": amount,
                        "quantity": 1,
                    },
                ],
            },
        }

        return payload

    def create_new_invoice(self, invoice_data):
        """Connect to the API and create a new invoice"""
        response = requests.post(self._get_api_url(), json=invoice_data)
        return response.json()

    def process(self):
        if len(sys.argv) < 2:
            self._print_help()
            return
        
        hours = self.read_amount_of_hours()
        amount = self._return_salary_based_on_hours(hours)
        invoice_data = self._generate_json_payload_for_api(amount)
        response = self.create_new_invoice(invoice_data)
        print(response)
