import pytest
import json

from reg_from_appln_no import (
    get_access_token,
    number_normalization,
    retrieve_one_extract,
)
from register_parser_functions import (
    get_filing_date,
    get_grant_date,
)


@pytest.fixture(
    params=[
        "3661357",
        "EP3661357",
        "18752141.4",
        "EP18752141.4",
        "18752141",
        "ep18752141",
    ],
)
def number(request):
    return request.param


@pytest.fixture()
def register_data():
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


def test_retrieve_one_extract_from_publication_seven_digits(number):
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
    assert biblio["@status"] == "No opposition filed within time limit"
    assert biblio["@id"] == "EP18752141P"


def test_get_filing_date(register_data):
    biblio = register_data["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]

    filing_date = get_filing_date(biblio)
    print(filing_date)
    assert True
