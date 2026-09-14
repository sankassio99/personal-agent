from agno.tools import tool
from googleapiclient.discovery import build

# Get this value from TelegramAdapterService.resolve_spreadsheet_id
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"
SHEET_NAME = "Despesas"

# Initialize this using your existing Google credentials.
sheets = build("sheets", "v4")


@tool
def add_expense(
    date: str,
    amount: float,
    description: str,
    category: str,
) -> str:
    """
    Add a new expense to the Google Sheets Transactions sheet.

    The tool automatically appends the expense to the next
    available row. Never specify a row number.
    """

    values = [[date, amount, description, category]]

    result = (
        sheets.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:D",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        )
        .execute()
    )

    updated_range = result.get(
        "updates", {}
    ).get("updatedRange", "unknown")

    return (
        f"Expense added successfully. "
        f"Range: {updated_range}"
    )