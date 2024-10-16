from datetime import datetime


def get_application_numbers(bibliographic_data: dict) -> list[tuple[str, str]]:
    """
    Takes the bibliographic data and returns a tuple of the EP and WO applications numbers if present
    """
    application_numbers = []
    if isinstance(bibliographic_data["reg:application-reference"], list):
        for entry in bibliographic_data["reg:application-reference"]:
            if entry["reg:document-id"]["reg:country"]["$"] == "EP":
                application_numbers.append(
                    (
                        "EP",
                        entry["reg:document-id"]["reg:doc-number"]["$"],
                    )
                )
            else:
                application_numbers.append(
                    (
                        "WO",
                        entry["reg:document-id"]["reg:doc-number"]["$"],
                    )
                )
    else:
        application_numbers.append(
            (
                "EP",
                bibliographic_data["reg:application-reference"]["reg:document-id"][
                    "reg:doc-number"
                ]["$"],
            )
        )

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
                print(f"exception for {bibliographic_data}\n{e}")
                grant_date = ""
        else:
            grant_date = ""
    else:
        grant_date = ""
    print(grant_date)
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
    print(designated_states)
    return designated_states


def is_granted(bibliographic_data: dict) -> bool:
    """
    Takes the bibliographic data and returns True if the patent is granted, False otherwise
    """
    if get_grant_date(bibliographic_data) != "":
        return True
    else:
        return False


def get_priority(bibliographic_data: dict) -> list[tuple]:
    """
    Takes the bibliographic data and returns a list of tuples of priority information
    in the form [(country, date as "yyyymmdd", number)], or an empty list if no priority information is found
    """
    priority = []
    if "reg:priority-claims" not in bibliographic_data:
        return priority
    priority_section = bibliographic_data["reg:priority-claims"]
    if isinstance(
        priority_section, list
    ):  # republication so there are >= two gazette entries
        priority_section = priority_section[0]
    if isinstance(
        priority_section["reg:priority-claim"], list
    ):  # multiple priority claims
        for entry in priority_section["reg:priority-claim"]:
            priority_country = entry["reg:country"]["$"]
            priority_date = entry["reg:date"]["$"]
            priority_number = entry["reg:doc-number"]["$"]
            priority.append((priority_country, priority_date, priority_number))
        return priority
    else:  # single priority claim
        priority_country = priority_section["reg:priority-claim"]["reg:country"]["$"]
        priority_date = priority_section["reg:priority-claim"]["reg:date"]["$"]
        priority_number = priority_section["reg:priority-claim"]["reg:doc-number"]["$"]
        priority.append((priority_country, priority_date, priority_number))
        return priority
