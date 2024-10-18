from helpers.register_access_download import (
    get_access_token,
    number_normalization,
    retrieve_one_extract,
)

from helpers.register_parser_functions import (
    Patent,
    get_application_numbers,
    get_publication_number_and_date,
    get_filing_date,
    get_grant_date,
    get_designated_states,
    is_granted,
    get_priority,
    get_all_applicants,
    get_all_inventors,
    get_title,
)


def get_full_patent_data(number, ref) -> Patent:
    token = get_access_token()
    this_patent = Patent()
    this_patent.ref = ref
    number_type, number = number_normalization(number)
    extract = retrieve_one_extract(number_type, number, token)
    if "invalid_number" in extract:
        return Patent(title=f"not a valid number: {extract['invalid_number']}")
    biblio = extract["ops:world-patent-data"]["ops:register-search"][
        "reg:register-documents"
    ]["reg:register-document"]["reg:bibliographic-data"]
    application_numbers = get_application_numbers(biblio)
    this_patent.ep_application_number = application_numbers["EP"]
    if "WO" in application_numbers:
        this_patent.wo_application_number = application_numbers["WO"]
    publication_data = get_publication_number_and_date(biblio)
    this_patent.ep_publication_number = publication_data["EP"]["number"]
    this_patent.ep_publication_date = publication_data["EP"]["date"]
    if "WO" in publication_data:
        this_patent.wo_publication_number = publication_data["WO"]["number"]
        this_patent.wo_publication_date = publication_data["WO"]["date"]
    this_patent.filing_date = get_filing_date(biblio)
    this_patent.grant_date = get_grant_date(biblio)
    this_patent.is_granted = is_granted(biblio)
    this_patent.priority = get_priority(biblio)
    this_patent.designated_states = get_designated_states(biblio)
    this_patent.applicants = get_all_applicants(biblio)
    this_patent.inventors = get_all_inventors(biblio)
    this_patent.title = get_title(biblio)
    return this_patent


if __name__ == "__main__":
    pass
