from ep_register_2024 import (
    get_access_token,
    number_normalization,
    retrieve_one_extract,
)

from register_parser_functions import (
    get_filing_date,
    get_grant_date,
    get_designated_states,
    is_granted,
)

from ep_register_2024 import CRED, AUTH_URL, CONSUMER_KEY, CONSUMER_SECRET_KEY

if __name__ == "__main__":
    token = get_access_token()
