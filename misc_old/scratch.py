import json
import requests
from src.helpers.register_access_download import get_access_token

token = get_access_token()


def retrieve_one_extract(number_type: str, number: str, token: str) -> dict:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    url = f"http://ops.epo.org/rest-services/register/{number_type}/epodoc/{number}/biblio"
    resp = requests.get(url, headers=headers)
    print(resp.status_code, type(resp.status_code))
    # for k, v in resp.headers.items():
    #     print(k, v)
    print(f"{type(resp.content)=}")
    # print(f"{resp.content=}")
    assert "The request was invalid" in str(resp.content)
    if type(resp.content) == "json":
        resp_dict = json.loads(resp.content)
        print("dict loaded")
    with open(r"output_files/test_register_extract.json", "w") as f:
        f.write(str(resp.content, encoding="utf-8"))
    return


for number in (
    "EP3661357",
    "EP18752141",
    "ep28752141",
):
    response = retrieve_one_extract("application", number, token)
    # for k, v in response.items():
    #     print(k, v)
    print(response)
