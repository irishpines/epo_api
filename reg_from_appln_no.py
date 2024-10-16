from ep_register_2024 import (
    get_access_token,
    number_normalization,
    retrieve_one_extract,
    retrieve_applicant_cases,
    get_filing_date,
    get_grant_date,
)
from ep_register_2024 import CRED, AUTH_URL, CONSUMER_KEY, CONSUMER_SECRET_KEY

if __name__ == "__main__":
    token = get_access_token()
