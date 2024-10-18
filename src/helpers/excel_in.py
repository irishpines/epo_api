from pathlib import Path
from openpyxl import Workbook, load_workbook


def get_excel_file() -> Workbook:
    print(
        "The Excel file should contain two columns on the first sheet, with the first column being \n"
        "a reference (e.g. client ref when creating new cases or Patricia number if cases exist) and \n"
        "the second column being the application or publication number. A header is expected for each row."
    )

    excel_file = Path(input("Enter Excel file path: "))
    wb = load_workbook(excel_file)
    return wb


def extract_excel_data(wb: Workbook) -> list[tuple[str, str]]:
    sheet = wb.active
    refs = [str(cell.value) for cell in sheet["A"]][1:]
    numbers = [str(cell.value) for cell in sheet["B"]][1:]
    return list(zip(refs, numbers))


# def create_excel_file(refs: list[str], numbers: list[str]):
