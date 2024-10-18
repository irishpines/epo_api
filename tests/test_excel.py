import pytest
from openpyxl import Workbook, load_workbook
from helpers.excel_in import extract_excel_data
from helpers.excel_out import (
    get_excel_from_template,
    initialize_wb,
    populate_excel_one_case,
)
from reg_from_appln_no import get_full_patent_data


@pytest.fixture
def wb():
    wb = load_workbook(
        filename=r"C:\Users\remoteuser\Google Drive\Pythonscripts\epo_api\input_files\magic_leap_cases.xlsx"
    )
    return wb


def test_extract_numbers(wb):
    numbers = extract_excel_data(wb)
    assert numbers[0][0] == "9512-20002.41.5 EPDIV5"
    assert numbers[0][1] == "24180270.1"
    assert numbers[36][0] == "PT06664EP"
    assert numbers[36][1] == "18744218.1"
    print(numbers[45:])
    assert len(numbers) == 47


def test_create_excel():
    wb = get_excel_from_template()
    wb = initialize_wb(wb)
    populate_excel_one_case(wb, get_full_patent_data("18752141", "testing1"))
