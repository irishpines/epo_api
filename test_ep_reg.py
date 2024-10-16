import pytest
import json
from datetime import datetime

from reg_from_appln_no import (
    get_access_token,
    number_normalization,
    retrieve_one_extract,
)
from register_parser_functions import (
    get_application_numbers,
    get_filing_date,
    get_publication_number_and_date,
    get_grant_date,
    get_designated_states,
    is_granted,
    get_priority,
)


@pytest.fixture(
    params=[
        "3661357",
        "EP3661357",
        "18752141.4",
        "EP18752141.4",
        "18752141",
        "ep18752141",
        "00650114.2",
        "1505543",
    ],
)
def number(request):
    return request.param


@pytest.fixture(
    params=[
        "3661357",  # Michael Earls, pct-based, after opposition
        "00650114.2",  # Magna, direct ep, granted
        "1505543",  # Lockheed, deemed withdrawn, direct ep
        "EP3009828",  # TCD, without priority
        "EP2422227",  # Magna, two priorities
    ],
)
def register_data(request):
    number = request.param
    token = get_access_token()
    number_type, number = number_normalization(number)
    retrieve_one_extract(number_type, number, token)
    with open("output_files/test_register_extract.json", "r") as f:
        return json.loads(f.read())


def test_number_normalizer(number):
    """
    tests that number normalizer works correctly for the validly formatted numbers
    """
    number_type, number = number_normalization(number)
    assert number_type in ["publication", "application"]


def test_get_access_token():
    """
    tests that an access token can be retrieved from credentials
    """
    token = get_access_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_retrieve_one_extract(number):
    """
    tests a series of valid numbers for the same case and verifies that register extract is retrieved correctly
    """
    token = get_access_token()
    number_type, normalized_number = number_normalization(number)
    extract = retrieve_one_extract(number_type, normalized_number, token)
    assert (
        extract["ops:world-patent-data"]["ops:register-search"]["@total-result-count"]
        == "1"
    )
    assert (
        "reg:bibliographic-data"
        in extract["ops:world-patent-data"]["ops:register-search"][
            "reg:register-documents"
        ]["reg:register-document"]
    )
    biblio = extract["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]
    assert biblio["@status"] in [
        "No opposition filed within time limit",
        "The patent has been granted",
        "The application is deemed to be withdrawn",
    ]
    assert biblio["@id"] in ["EP18752141P", "EP00650114P", "EP04018554P"]


def test_get_application_numbers(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    application_numbers = get_application_numbers(biblio)
    if biblio["@id"] in ["EP18752141P", "EP10767749P"]:
        assert len(application_numbers) == 2
    else:
        assert application_numbers[0][1] in ["00650114", "14188853", "04018554"]


def test_get_publication_number_and_date(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    publication_details = get_publication_number_and_date(biblio)
    assert publication_details["EP"]["number"] in [
        "3661357",
        "1097848",
        "1505543",
        "3009828",
        "2422227",
    ]
    assert publication_details["EP"]["date"] in [
        "20200610",
        "20010509",
        "20050209",
        "20160420",
        "20120229",
    ]
    if "WO" in publication_details:
        assert publication_details["WO"]["number"] in [
            "2019025638",
            "2010124064",
        ]
        assert publication_details["WO"]["date"] in ["20190207", "20101028"]


def test_get_filing_date(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    filing_date = get_filing_date(biblio)
    print(biblio["@id"], filing_date)
    assert filing_date in [
        datetime(2018, 8, 6, 0, 0),
        datetime(2000, 8, 24, 0, 0),
        datetime(2004, 8, 5, 0, 0),
        datetime(2014, 10, 14, 0, 0),
        datetime(2010, 4, 22, 0, 0),
    ]


def test_get_grant_date(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    grant_date = get_grant_date(biblio)
    if biblio["@id"] in ["EP04018554P", "EP14188853P"]:
        assert grant_date == ""
    else:
        assert grant_date in [
            datetime(2021, 3, 17, 0, 0),
            datetime(2007, 3, 21, 0, 0),
            datetime(2014, 5, 14, 0, 0),
        ]


def test_get_designated_states(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    states = get_designated_states(biblio)
    assert "GB" in states


def test_is_granted(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    granted = is_granted(biblio)
    if biblio["@id"] in ["EP04018554P", "EP14188853P"]:
        assert not granted
    else:
        assert granted


def test_get_priority(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    priority_list = get_priority(biblio)
    if biblio["@id"] == "EP14188853P":
        assert len(priority_list) == 0
    elif biblio["@id"] == "EP10767749P":
        assert len(priority_list) == 2
    else:
        assert len(priority_list) == 1
