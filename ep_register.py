from abc import get_cache_token
from config import c_key, c_s_key
import base64
import requests
import json
import pprint
import pandas as pd
from datetime import datetime

CRED = base64.b64encode(f"{c_key}:{c_s_key}".encode("utf-8"))
print(CRED)
AUTH_URL = "https://ops.epo.org/3.2/auth/accesstoken"


def get_access_token():
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    DATA = {"grant_type": "client_credentials"}
    resp = requests.post(AUTH_URL, auth=(c_key, c_s_key), headers=HEADERS, data=DATA)
    resp_string = str(resp.content, encoding="utf-8")
    resp_dict = json.loads(resp_string)
    print(resp_dict)
    token = resp_dict["access_token"]
    return token


def retrieve_one_extract(
    number_type, number, token
):  # publication or application or priority
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"http://ops.epo.org/rest-services/register/{number_type}/epodoc/{number}/biblio"

    resp = requests.get(url, headers=headers)
    resp_string = str(resp.content, encoding="utf-8")
    resp_dict = json.loads(resp_string)
    return resp_dict


def retrieve_applicant_cases(
    applicant_name, token
):  # publication or application or priority
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"http://ops.epo.org/rest-services/register/search/?q=pa%3D{applicant_name}"

    resp = requests.get(url, headers=headers)
    resp_string = str(resp.content, encoding="utf-8")
    print(resp_string)
    resp_dict = json.loads(resp_string)
    return resp.json()


def get_filing_date(bibliographic_data):
    filing_info = bibliographic_data["reg:application-reference"]
    # print(filing_info)
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


def retrieve_representative_cases(
    representative_name, token
):  # publication or application or priority
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"http://ops.epo.org/rest-services/register/search/?q=re%3D{representative_name}"

    resp = requests.get(url, headers=headers)
    resp_string = str(resp.content, encoding="utf-8")
    print(resp_string)
    resp_dict = json.loads(resp_string)
    return resp.json()


if __name__ == "__main__":
    token = get_access_token()

    ## read csv with patent nos to Pandas, convert ints to str, leftpad to 7 chars with zero
    # df = pd.read_csv(r"C:\Users\remoteuser\Google Drive\opt-outs\Kerry\Book1.csv")
    # numbers_dates = {"Patent_No": [], "Filing_Date": [], "Grant_Date": []}
    # for row in df.iloc[:, 0]:  # first to last row, column 0
    #     number = str(row)
    #     if len(number) < 7:
    #         number = number.rjust(7, "0")
    #     extract = retrieve_one_extract("publication", f"EP{number}", token)
    #     with open("sample_extracts.json", "a") as f:
    #         f.write(json.dumps(extract, indent=4))
    #     data = extract["ops:world-patent-data"]["ops:register-search"][
    #         "reg:register-documents"
    #     ]["reg:register-document"]["reg:bibliographic-data"]
    #     filing_date = get_filing_date(data).strftime("%d %b %Y")
    #     print(filing_date)
    #     grant_date = get_grant_date(data)
    #     if grant_date:
    #         grant_date = grant_date.strftime("%d %b %Y")
    #     numbers_dates["Patent_No"].append(number)
    #     numbers_dates["Filing_Date"].append(filing_date)
    #     numbers_dates["Grant_Date"].append(grant_date)
    # new_df = pd.DataFrame.from_dict(numbers_dates)
    # new_df.to_excel("output.xlsx", sheet_name="Sheet_name_1")


# print(token)
# extract = retrieve_one_extract("publication", "EP3401400", token)

# with open("sample_extract.json", "w") as f:
#     f.write(json.dumps(extract, indent=4))

# data = extract["ops:world-patent-data"]["ops:register-search"][
#     "reg:register-documents"
# ]["reg:register-document"]["reg:bibliographic-data"]
# priority_data = data["reg:priority-claims"]["reg:priority-claim"]  # list
# print("Priority claims:")
# for priority in priority_data:
#     print(
#         f'{priority["@sequence"]}: {priority["reg:country"]["$"]} {priority["reg:doc-number"]["$"]} filed {priority["reg:date"]["$"]}'
#     )

# applicant_name = "N.V. Muller"
# all_case_data = retrieve_applicant_cases(applicant_name, token)
# with open(
#     r"C:\Users\remoteuser\Google Drive\Pythonscripts\epo_api\venv\logs\retrieved_data.log",
#     "a",
# ) as f:
#     f.write(json.dumps(all_case_data, indent=4))

representative_name = "frkelly"
all_case_data = retrieve_representative_cases(representative_name, token)
with open(
    r"C:\Users\remoteuser\Google Drive\Pythonscripts\epo_api\logs\retrieved_rep_data.log",
    "w",
) as f:
    f.write(json.dumps(all_case_data, indent=4))
