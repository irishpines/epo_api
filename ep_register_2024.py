import base64
import requests
import json
import os
import pandas as pd
import chardet
from dotenv import load_dotenv


load_dotenv()
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET_KEY = os.getenv("CONSUMER_SECRET_KEY")


CRED = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET_KEY}".encode("utf-8"))
AUTH_URL = "https://ops.epo.org/3.2/auth/accesstoken"


def get_access_token() -> str:
    HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}
    DATA = {"grant_type": "client_credentials"}
    resp = requests.post(
        AUTH_URL, auth=(CONSUMER_KEY, CONSUMER_SECRET_KEY), headers=HEADERS, data=DATA
    )
    resp_string = str(resp.content, encoding="utf-8")
    resp_dict = json.loads(resp_string)
    token = resp_dict["access_token"]
    return token


def number_normalization(number: str | int) -> tuple[str, str]:
    if isinstance(number, int):
        number = str(number)
    if number.lower().startswith("ep"):
        number = number[2:]
    if len(number) == 7:
        number = "EP" + number
        number_type = "publication"
    elif len(number) == 8:
        number = "EP" + number
        number_type = "application"
    elif len(number) == 10:
        number = "EP" + number[:8]
        number_type = "application"
    else:
        number = number
        number_type = "unknown"
    return number_type, number


def retrieve_one_extract(number_type: str, number: str, token: str) -> dict:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"http://ops.epo.org/rest-services/register/{number_type}/epodoc/{number}/biblio"
    resp = requests.get(url, headers=headers)
    resp_dict = json.loads(resp.content)
    with open(r"output_files/test_register_extract.json", "w") as f:
        f.write(str(resp.content, encoding="utf-8"))
    return resp_dict


# def retrieve_applicant_cases(applicant_name, token):
#     headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
#     url = f"http://ops.epo.org/rest-services/register/search/?q=pa%3D{applicant_name}"

#     resp = requests.get(url, headers=headers)
#     resp_string = str(resp.content, encoding="utf-8")
#     print(resp_string)
#     resp_dict = json.loads(resp_string)
#     return resp.json()


# def retrieve_representative_cases(
#     representative_name, token
# ):  # publication or application or priority
#     headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
#     url = f"http://ops.epo.org/rest-services/register/search/?q=re%3D{representative_name}"

#     resp = requests.get(url, headers=headers)
#     resp_string = str(resp.content, encoding="utf-8")
#     print(resp_string)
#     resp_dict = json.loads(resp_string)
#     return resp.json()


# if __name__ == "__main__":
#     token = get_access_token()

#     ## read csv with patent nos to Pandas, convert ints to str, leftpad to 7 chars with zero
#     # df = pd.read_csv(r"C:\Users\remoteuser\Google Drive\opt-outs\Kerry\Book1.csv")
#     # numbers_dates = {"Patent_No": [], "Filing_Date": [], "Grant_Date": []}
#     # for row in df.iloc[:, 0]:  # first to last row, column 0
#     #     number = str(row)
#     #     if len(number) < 7:
#     #         number = number.rjust(7, "0")
#     #     extract = retrieve_one_extract("publication", f"EP{number}", token)
#     #     with open("sample_extracts.json", "a") as f:
#     #         f.write(json.dumps(extract, indent=4))
#     #     data = extract["ops:world-patent-data"]["ops:register-search"][
#     #         "reg:register-documents"
#     #     ]["reg:register-document"]["reg:bibliographic-data"]
#     #     filing_date = get_filing_date(data).strftime("%d %b %Y")
#     #     print(filing_date)
#     #     grant_date = get_grant_date(data)
#     #     if grant_date:
#     #         grant_date = grant_date.strftime("%d %b %Y")
#     #     numbers_dates["Patent_No"].append(number)
#     #     numbers_dates["Filing_Date"].append(filing_date)
#     #     numbers_dates["Grant_Date"].append(grant_date)
#     # new_df = pd.DataFrame.from_dict(numbers_dates)
#     # new_df.to_excel("output.xlsx", sheet_name="Sheet_name_1")

#     # print(token)
#     # extract = retrieve_one_extract("publication", "EP3401400", token)

#     # with open("sample_extract.json", "w") as f:
#     #     f.write(json.dumps(extract, indent=4))

#     # data = extract["ops:world-patent-data"]["ops:register-search"][
#     #     "reg:register-documents"
#     # ]["reg:register-document"]["reg:bibliographic-data"]
#     # priority_data = data["reg:priority-claims"]["reg:priority-claim"]  # list
#     # print("Priority claims:")
#     # for priority in priority_data:
#     #     print(
#     #         f'{priority["@sequence"]}: {priority["reg:country"]["$"]} {priority["reg:doc-number"]["$"]} filed {priority["reg:date"]["$"]}'
#     #     )

#     # applicant_name = "N.V. Muller"
#     # all_case_data = retrieve_applicant_cases(applicant_name, token)
#     # with open(
#     #     r"C:\Users\remoteuser\Google Drive\Pythonscripts\epo_api\venv\logs\retrieved_data.log",
#     #     "a",
#     # ) as f:
#     #     f.write(json.dumps(all_case_data, indent=4))

#     representative_name = "frkelly"
#     all_case_data = retrieve_representative_cases(representative_name, token)
#     with open(
#         r"C:\Users\remoteuser\Google Drive\Pythonscripts\epo_api\logs\retrieved_rep_data.log",
#         "w",
#     ) as f:
#         f.write(json.dumps(all_case_data, indent=4))
