import random
from datetime import datetime
from dataclasses import dataclass, field
from helpers.epo_checksum import add_check_digit


@dataclass
class Party:
    unique_id: str = field(
        compare=False, default_factory=lambda: str(random.random())[-8:]
    )
    # To be used to match a case on CASE_DATA sheet with a party on the NAME_DATA sheet
    # Default factory generates a different unique_id each time a new object is created
    # compare=false allows new party to be matched with an existing party where the unique_id is different
    # but all other fields are identical
    is_legal_entity: bool = False
    is_applicant: bool = False
    is_inventor: bool = False
    company_name: str = ""
    applicant_sequence_number: int = 0
    inventor_sequence_number: int = 0
    first_name: str = ""
    last_name: str = ""
    address_1: str = ""
    address_2: str = ""
    address_3: str = ""
    address_4: str = ""
    address_5: str = ""
    address_country: str = ""
    nationality: str = ""
    residence_country: str = ""


@dataclass
class Priority:
    country: str = ""
    date: datetime = ""
    number: str = ""


@dataclass
class Patent:
    ref: str = ""
    title: str = ""
    ep_application_number: str = ""
    wo_application_number: str = ""
    filing_date: datetime = None
    publication_number: str = ""
    publication_date: datetime = None
    is_granted: bool = False
    grant_date: datetime = None
    priority: list[Priority] = None
    designated_states: list[str] = None
    applicants: list[Party] = None
    inventors: list[Party] = None


all_parties_found = []  # Used to avoid creating duplicate parties on Patricia import


def get_application_numbers(bibliographic_data: dict) -> dict[str, str]:
    """
    Takes the bibliographic data and returns a tuple of the EP and WO applications numbers if present
    """
    application_numbers = {}
    if isinstance(bibliographic_data["reg:application-reference"], list):
        for entry in bibliographic_data["reg:application-reference"]:
            if entry["reg:document-id"]["reg:country"]["$"] == "EP":
                eight_digit_app_num = entry["reg:document-id"]["reg:doc-number"]["$"]
                application_numbers["EP"] = add_check_digit(eight_digit_app_num)
            else:
                application_numbers["WO"] = entry["reg:document-id"]["reg:doc-number"][
                    "$"
                ]
    else:
        eight_digit_app_num = bibliographic_data["reg:application-reference"][
            "reg:document-id"
        ]["reg:doc-number"]["$"]
        application_numbers["EP"] = add_check_digit(eight_digit_app_num)

    return application_numbers


def get_filing_date(bibliographic_data: dict) -> datetime:
    """
    Takes the bibliographic data and returns the filing date as a datetime object, or an empty string if no filing date is found
    """
    filing_info = bibliographic_data["reg:application-reference"]
    if isinstance(filing_info, list):
        for entry in filing_info:
            try:
                if entry["reg:document-id"]["reg:country"]["$"] == "EP":
                    raw_filing_date = entry["reg:document-id"]["reg:date"]["$"]
                    filing_date = datetime.strptime(raw_filing_date, "%Y%m%d")
                    break
            except KeyError:
                filing_date = ""
    else:
        try:
            raw_filing_date = filing_info["reg:document-id"]["reg:date"]["$"]
            filing_date = datetime.strptime(raw_filing_date, "%Y%m%d")
        except KeyError:
            filing_date = ""
    return filing_date


def get_publication_number_and_date(bibliographic_data: dict) -> dict:
    """
    Takes the bibliographic data and returns a dictionary of EP and WO (if present) publication numbers and dates
    such as {"EP": {"number": "3661357", "date": "20120229"}, "WO": {"number": "1097848", "date": "20120229"}}
    """
    publication_details = {}
    publication_section = bibliographic_data["reg:publication-reference"]
    if isinstance(publication_section, list):
        for pub in publication_section:
            if pub["reg:document-id"]["reg:country"]["$"] == "EP" and pub[
                "reg:document-id"
            ]["reg:kind"]["$"] in ["A1", "A2"]:
                publication_details["EP"] = {
                    "number": pub["reg:document-id"]["reg:doc-number"]["$"],
                    "date": pub["reg:document-id"]["reg:date"]["$"],
                }
            elif pub["reg:document-id"]["reg:country"]["$"] == "WO" and pub[
                "reg:document-id"
            ]["reg:kind"]["$"] in ["A1", "A2"]:
                publication_details["WO"] = {
                    "number": pub["reg:document-id"]["reg:doc-number"]["$"],
                    "date": pub["reg:document-id"]["reg:date"]["$"],
                }
    else:
        publication_details["EP"] = {
            "number": publication_section["reg:document-id"]["reg:doc-number"]["$"],
            "date": publication_section["reg:document-id"]["reg:date"]["$"],
        }

    return publication_details


def get_grant_date(bibliographic_data: dict) -> datetime:
    """'
    Takes the bibliographic data and returns the grant date as a datetime object, or an empty string if no grant date is found
    """
    publn_info = bibliographic_data["reg:publication-reference"]
    if isinstance(publn_info, list):
        for entry in publn_info:
            try:
                if entry["reg:document-id"]["reg:kind"]["$"] == "B1":
                    raw_grant_date = entry["reg:document-id"]["reg:date"]["$"]
                    grant_date = datetime.strptime(raw_grant_date, "%Y%m%d")
                    break
            except Exception as e:
                grant_date = ""
        else:
            grant_date = ""
    else:
        grant_date = ""
    return grant_date


def get_designated_states(bibliographic_data: dict) -> list[str]:
    """
    Takes the bibliographic data and returns a list of designated states as two letter country code strings
    """
    designated_states = []
    designated_state_section = bibliographic_data["reg:designation-of-states"]
    if isinstance(
        designated_state_section, list
    ):  # Change in designated states between publications
        designated_state_section = designated_state_section[0]
    if "reg:designation-pct" in designated_state_section:
        designated_state_raw_list = designated_state_section["reg:designation-pct"][
            "reg:regional"
        ]["reg:country"]
    for entry in designated_state_raw_list:
        designated_states.append(entry["$"])
    return designated_states


def is_granted(bibliographic_data: dict) -> bool:
    """
    Takes the bibliographic data and returns True if the patent is granted, False otherwise
    """
    if get_grant_date(bibliographic_data) != "":
        return True
    else:
        return False


def get_priority(bibliographic_data: dict) -> list[Priority]:
    """
    Takes the bibliographic data and returns a list of tuples of Priority objects, or an empty list if no priority information is found
    """
    priorities = []
    if "reg:priority-claims" not in bibliographic_data:
        return priorities
    priority_section = bibliographic_data["reg:priority-claims"]
    if isinstance(
        priority_section, list
    ):  # republication so there are >= two gazette entries
        priority_section = priority_section[0]
    if isinstance(
        priority_section["reg:priority-claim"], list
    ):  # multiple priority claims
        for entry in priority_section["reg:priority-claim"]:
            this_priority = Priority()
            this_priority.country = entry["reg:country"]["$"]
            this_priority.date = datetime.strptime(entry["reg:date"]["$"], "%Y%m%d")
            this_priority.number = entry["reg:doc-number"]["$"]
            priorities.append(this_priority)
        return priorities
    else:  # single priority claim
        this_priority = Priority()
        this_priority.country = priority_section["reg:priority-claim"]["reg:country"][
            "$"
        ]
        this_priority.date = datetime.strptime(
            priority_section["reg:priority-claim"]["reg:date"]["$"], "%Y%m%d"
        )
        this_priority.number = priority_section["reg:priority-claim"]["reg:doc-number"][
            "$"
        ]
        priorities.append(this_priority)
        return priorities


def get_one_applicant(party_data: dict) -> Party:
    """
    Takes the section of bibliographic data for a specific party and returns a Party object
    """
    party = Party()
    party.is_legal_entity = True  # assumption, not sure how to distinguish other than with an undependable Regex; assume for now that it's a legal entity
    party.is_applicant = True
    party.company_name = party_data["reg:addressbook"]["reg:name"]["$"]
    party.applicant_sequence_number = int(party_data["@sequence"])
    party.address_1 = party_data["reg:addressbook"]["reg:address"]["reg:address-1"]["$"]
    if "reg:address-2" in party_data["reg:addressbook"]["reg:address"]:
        party.address_2 = party_data["reg:addressbook"]["reg:address"]["reg:address-2"][
            "$"
        ]
    if "reg:address-3" in party_data["reg:addressbook"]["reg:address"]:
        party.address_3 = party_data["reg:addressbook"]["reg:address"]["reg:address-3"][
            "$"
        ]
    if "reg:address-4" in party_data["reg:addressbook"]["reg:address"]:
        party.address_4 = party_data["reg:addressbook"]["reg:address"]["reg:address-4"][
            "$"
        ]
    if "reg:address-5" in party_data["reg:addressbook"]["reg:address"]:
        party.address_5 = party_data["reg:addressbook"]["reg:address"]["reg:address-5"][
            "$"
        ]
    party.address_country = party_data["reg:addressbook"]["reg:address"]["reg:country"][
        "$"
    ]
    party.nationality = party_data["reg:nationality"]["reg:country"]["$"]
    party.residence_country = party_data["reg:residence"]["reg:country"]["$"]
    for existing_party in all_parties_found:
        if party == existing_party:  # identical except unique_id
            return existing_party
    all_parties_found.append(party)
    return party


def get_one_inventor(party_data: dict) -> Party:
    """
    Takes the section of bibliographic data for a specific party and returns a Party object
    """
    party = Party()
    party.is_legal_entity = False
    party.is_inventor = True
    party.inventor_sequence_number = int(party_data["@sequence"])
    full_name = party_data["reg:addressbook"]["reg:name"]["$"]
    party.last_name, party.first_name = full_name.split(",", 1)
    party.address_1 = party_data["reg:addressbook"]["reg:address"]["reg:address-1"]["$"]
    if "reg:address-2" in party_data["reg:addressbook"]["reg:address"]:
        party.address_2 = party_data["reg:addressbook"]["reg:address"]["reg:address-2"][
            "$"
        ]
    if "reg:address-3" in party_data["reg:addressbook"]["reg:address"]:
        party.address_3 = party_data["reg:addressbook"]["reg:address"]["reg:address-3"][
            "$"
        ]
    if "reg:address-4" in party_data["reg:addressbook"]["reg:address"]:
        party.address_4 = party_data["reg:addressbook"]["reg:address"]["reg:address-4"][
            "$"
        ]
    if "reg:address-5" in party_data["reg:addressbook"]["reg:address"]:
        party.address_5 = party_data["reg:addressbook"]["reg:address"]["reg:address-5"][
            "$"
        ]
    party.address_country = party_data["reg:addressbook"]["reg:address"]["reg:country"][
        "$"
    ]
    for existing_party in all_parties_found:
        if party == existing_party:  # identical except unique_id
            return existing_party
    all_parties_found.append(party)
    return party


def get_all_applicants(bibliographic_data: dict) -> list[Party]:
    """
    Finds the applicants in the bibliographic data and returns a list of Party objects
    """
    applicants = []
    # find the latest or only record of the applicants on the case
    if not isinstance(bibliographic_data["reg:parties"]["reg:applicants"], list):
        latest_applicant_raw_data = bibliographic_data["reg:parties"]["reg:applicants"][
            "reg:applicant"
        ]
    else:
        latest_applicant_raw_data = bibliographic_data["reg:parties"]["reg:applicants"][
            0
        ]["reg:applicant"]
    # Loop through the list of applicants, taking account of single applicant cases where there is no list
    if not isinstance(latest_applicant_raw_data, list):
        latest_applicant_raw_data = [latest_applicant_raw_data]
    for entry in latest_applicant_raw_data:
        applicant = get_one_applicant(entry)
        applicants.append(applicant)
    return applicants


def get_all_inventors(bibliographic_data: dict) -> list[Party]:
    """
    Finds the inventors in the bibliographic data and returns a list of Party objects
    """
    inventors = []
    # find the latest or only record of the inventors on the case
    if not isinstance(bibliographic_data["reg:parties"]["reg:inventors"], list):
        latest_inventor_raw_data = bibliographic_data["reg:parties"]["reg:inventors"][
            "reg:inventor"
        ]
    else:
        latest_inventor_raw_data = bibliographic_data["reg:parties"]["reg:inventors"][
            0
        ]["reg:inventor"]
    # Loop through the list of inventors, taking account of single inventor cases where there is no list
    if not isinstance(latest_inventor_raw_data, list):
        latest_inventor_raw_data = [latest_inventor_raw_data]

    for entry in latest_inventor_raw_data:
        inventor = get_one_inventor(entry)
        inventors.append(inventor)
    return inventors


def get_title(bibliographic_data: dict) -> str:
    """
    Takes the bibliographic data and returns the title
    """
    title_section = bibliographic_data["reg:invention-title"]
    for entry in title_section:
        if entry["@lang"] == "en":
            return entry["$"]
