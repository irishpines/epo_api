from datetime import datetime


def get_filing_date(bibliographic_data):
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


def get_grant_date(bibliographic_data):
    publn_info = bibliographic_data["reg:publication-reference"]
    # print(filing_info)
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
    return grant_date
