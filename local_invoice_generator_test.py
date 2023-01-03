import pytest
import datetime
import requests
import os
from unittest.mock import patch
from local_invoice_generator import LocalInvoiceGenerator


class ResponseCreateInvoiceMock(object):
    def json(self):
        return {"created": True}


@pytest.fixture(name="invoice_generator")
def fixture_invoice_generator():
    lig = LocalInvoiceGenerator()
    return lig


def test_invoice_generator_initialization(invoice_generator):
    assert invoice_generator


@pytest.mark.parametrize(
    "date, expected",
    (
        (datetime.date(2022, 12, 1), True),
        (datetime.date(2022, 12, 2), True),
        (datetime.date(2022, 12, 3), False),
        (datetime.date(2022, 12, 4), False),
        (datetime.date(2022, 12, 5), True),
        (datetime.date(2022, 12, 6), True),
        (datetime.date(2022, 12, 7), True),
    ),
)
def test_is_weekday(invoice_generator, date, expected):
    assert invoice_generator._is_weekday(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    (
        (datetime.date(2022, 12, 1), datetime.date(2022, 11, 30)),
        (datetime.date(2023, 1, 1), datetime.date(2022, 12, 31)),
        (datetime.date(2022, 10, 15), datetime.date(2022, 10, 14)),
    ),
)
def test_get_yesterday(invoice_generator, date, expected):
    assert invoice_generator._get_yesterday(date) == expected


@pytest.mark.parametrize(
    "date, expected",
    (
        (datetime.date(2022, 12, 1), datetime.date(2022, 12, 30)),
        (datetime.date(2022, 11, 10), datetime.date(2022, 11, 30)),
        (datetime.date(2022, 10, 31), datetime.date(2022, 10, 31)),
        (datetime.date(2022, 7, 10), datetime.date(2022, 7, 29)),
    ),
)
def test_get_last_working_day_of_this_month(invoice_generator, date, expected):
    assert invoice_generator._get_last_working_day_of_this_month(date) == expected


@pytest.mark.parametrize("hours, expected", ((168, 15000), (84, 7500)))
def test_return_salary_based_on_hours(invoice_generator, hours, expected):
    assert invoice_generator._return_salary_based_on_hours(hours) == expected


@pytest.mark.parametrize(
    "given_date, days_to_pay, expected",
    (
        (datetime.date(2022, 11, 30), 21, datetime.date(2022, 12, 21)),
        (datetime.date(2022, 12, 30), 21, datetime.date(2023, 1, 20)),
        (datetime.date(2022, 11, 5), 21, datetime.date(2022, 11, 26)),
    ),
)
def test_get_payment_deadline_date(
    invoice_generator, given_date, days_to_pay, expected
):
    assert (
        invoice_generator._get_payment_deadline_date(
            days_to_pay=days_to_pay, date=given_date
        )
        == expected
    )


@pytest.mark.parametrize("days", (-5, 0, 4))
def test_get_payment_deadline_date_wrong_days(invoice_generator, days):
    with pytest.raises(ValueError):
        invoice_generator._get_payment_deadline_date(days_to_pay=days)


@pytest.mark.parametrize(
    "date, expected",
    (
        (datetime.date(2022, 10, 10), "2022-10-10"),
        (datetime.date(2022, 5, 5), "2022-05-05"),
        (datetime.date(2022, 1, 11), "2022-01-11"),
    ),
)
def test_format_date_properly(invoice_generator, date, expected):
    assert invoice_generator._format_date_properly(date) == expected


@patch.object(requests, "post", return_value=ResponseCreateInvoiceMock())
def test_create_new_invoice(api_mock, invoice_generator):
    dummy_invoice_data = {"create_invoice": "OK"}
    invoice_generator.create_new_invoice(dummy_invoice_data)


@pytest.mark.parametrize(
    "date, expected",
    (
        (datetime.date(2023, 1, 1), True),
        (datetime.date(2023, 1, 2), False),
        (datetime.date(2023, 1, 6), True),
        (datetime.date(2023, 1, 8), False),
    ),
)
def test_is_holiday(invoice_generator, date, expected):
    assert invoice_generator._is_holiday(date) == expected

@pytest.mark.parametrize("date, expected", (
    (datetime.date(2023, 1, 1), 21),
    (datetime.date(2023, 2, 1), 20),
    (datetime.date(2023, 5, 1), 21),
    (datetime.date(2023, 12, 1), 19),
))
def test_get_workdays_this_month(invoice_generator, date, expected):
    assert invoice_generator._get_workdays_this_month(date) == expected

def test_generate_json_payload_for_api(invoice_generator):
    pytest.skip()
    # TODO 