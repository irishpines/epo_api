import pytest

from reg_from_appln_no import (
    get_access_token,
    retrieve_one_extract,
    retrieve_applicant_cases,
    get_filing_date,
    get_grant_date,
)


def test_get_access_token():
    token = get_access_token()
    assert isinstance(token, str)
    assert len(token) > 0

