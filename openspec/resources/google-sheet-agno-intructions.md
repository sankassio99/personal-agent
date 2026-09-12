# Google Sheets (/tools/toolkits/others/google-sheets)



**GoogleSheetsTools** enable an Agent to interact with Google Sheets API for reading, creating, updating, and duplicating spreadsheets.

## Prerequisites [#prerequisites]

You need to install the required Google API client libraries:

```bash
uv pip install agno google-api-python-client google-auth-httplib2 google-auth-oauthlib openai
```

Set up the following environment variables:

```bash
export GOOGLE_CLIENT_ID=your_client_id_here
export GOOGLE_CLIENT_SECRET=your_client_secret_here
export GOOGLE_PROJECT_ID=your_project_id_here
```

## How to Get Credentials [#how-to-get-credentials]

1. Go to Google Cloud Console ([https://console.cloud.google.com](https://console.cloud.google.com))

2. Create a new project or select an existing one

3. Enable the Google Sheets API:
   * Go to "APIs & Services" > "Enable APIs and Services"
   * Search for "Google Sheets API"
   * Click "Enable"

4. Create OAuth 2.0 credentials:
   * Go to "APIs & Services" > "Credentials"
   * Click "Create Credentials" > "OAuth client ID"
   * Go through the OAuth consent screen setup
   * Give it a name and click "Create"
   * You'll receive:
     * Client ID (GOOGLE\_CLIENT\_ID)
     * Client Secret (GOOGLE\_CLIENT\_SECRET)
   * The Project ID (GOOGLE\_PROJECT\_ID) is visible in the project dropdown at the top of the page

<include path="../../../../_snippets/set-openai-key.mdx" />

## Example [#example]

The following agent will use Google Sheets to read spreadsheet data.

```python title="cookbook/91_tools/googlesheets_tools.py"
from agno.agent import Agent
from agno.tools.google.sheets import GoogleSheetsTools

SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
SAMPLE_RANGE_NAME = "Class Data!A2:E"

google_sheets_tools = GoogleSheetsTools(
    spreadsheet_id=SAMPLE_SPREADSHEET_ID,
    spreadsheet_range=SAMPLE_RANGE_NAME,
    oauth_port=8080,  # or any other port
)

agent = Agent(
    tools=[google_sheets_tools],
    instructions=[
        "You help users interact with Google Sheets using tools that use the Google Sheets API",
        "Before asking for spreadsheet details, first attempt the operation as the user may have already configured the ID and range in the constructor",
    ],
)
agent.print_response("Please tell me about the contents of the spreadsheet")
```

## Toolkit Params [#toolkit-params]

| Parameter                | Type                    | Default | Description                                                                                                                            |
| ------------------------ | ----------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `scopes`                 | `Optional[List[str]]`   | `None`  | Custom OAuth scopes. If None, inferred from enabled tools: read scope for `read_sheet`, write scope added for create/update/duplicate. |
| `spreadsheet_id`         | `Optional[str]`         | `None`  | ID of the target spreadsheet.                                                                                                          |
| `spreadsheet_range`      | `Optional[str]`         | `None`  | Range within the spreadsheet.                                                                                                          |
| `creds`                  | `Optional[Credentials]` | `None`  | Pre-existing credentials.                                                                                                              |
| `credentials_path`       | `Optional[str]`         | `None`  | Path to credentials file.                                                                                                              |
| `token_path`             | `Optional[str]`         | `None`  | Path to token file.                                                                                                                    |
| `service_account_path`   | `Optional[str]`         | `None`  | Path to a service account JSON key file.                                                                                               |
| `oauth_port`             | `int`                   | `0`     | Port to use for OAuth authentication.                                                                                                  |
| `read_sheet`             | `bool`                  | `True`  | Enable reading from a sheet.                                                                                                           |
| `create_sheet`           | `bool`                  | `False` | Enable creating a sheet.                                                                                                               |
| `update_sheet`           | `bool`                  | `False` | Enable updating a sheet.                                                                                                               |
| `create_duplicate_sheet` | `bool`                  | `False` | Enable creating a duplicate sheet.                                                                                                     |
| `all`                    | `bool`                  | `False` | Enable all tools.                                                                                                                      |

## Toolkit Functions [#toolkit-functions]

| Function                 | Description                                                                                                                                                                                                                                                                                 |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `read_sheet`             | Read values from a Google Sheet. Parameters include `spreadsheet_id` (Optional\[str]) for fallback spreadsheet ID and `spreadsheet_range` (Optional\[str]) for fallback range. Returns JSON of list of rows.                                                                                |
| `create_sheet`           | Create a new Google Sheet. Parameters include `title` (str) for the title of the Google Sheet. Returns a link to the created spreadsheet.                                                                                                                                                   |
| `update_sheet`           | Update data in a Google Sheet. Parameters include `data` (List\[List\[Any]]) for the data to update, `spreadsheet_id` (Optional\[str]) for the ID of the Google Sheet, and `range_name` (Optional\[str]) for the range to update. Returns success or failure message.                       |
| `create_duplicate_sheet` | Create a duplicate of an existing Google Sheet. Parameters include `source_id` (str) for the ID of the source spreadsheet, `new_title` (Optional\[str]) for new title, and `copy_permissions` (bool, default=True) for whether to copy permissions. Returns link to duplicated spreadsheet. |

## Writing and duplication scopes [#writing-and-duplication-scopes]

`all=True` registers all four tools, but the current scope inference only considers the individual write flags. Set write flags explicitly or provide write scopes. To duplicate a sheet, enable the **Google Drive API** as well as Sheets and request both scopes before authenticating:

```python
from agno.tools.google.sheets import GoogleSheetsTools

tools = GoogleSheetsTools(
    create_duplicate_sheet=True,
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ],
)
```

Use credentials with access to the source spreadsheet and permission to copy it. Reauthorize if an existing cached token lacks these scopes. The adapter's attempt to add Drive scope during duplication does not update the shared auth scope registration, so request it at construction.

## Shared Google authentication [#shared-google-authentication]

The current Google Workspace toolkits accept `auth=AuthConfig(...)` through their shared base class. Reuse one config across Drive, Sheets, Slides, or Calendar toolkits to aggregate the scopes before the first authentication:

```python
from agno.tools.google.auth import AuthConfig

auth = AuthConfig(interactive=False, http_timeout=60)
```

Pass `auth=auth` to each toolkit constructor. This headless configuration requires existing usable credentials; it raises instead of opening a browser when interactive authorization would be needed. For an initial local OAuth sign-in, use `interactive=True` with the client credentials described above.

`AuthConfig` also accepts a supported `db` for token storage. Encryption is enabled by default and requires a `token_encryption_key` (or `GOOGLE_TOKEN_ENCRYPTION_KEY`). Its database token identity is shared for this Google configuration; it does not automatically select credentials by the agent's `user_id`. Put service-account and delegated-user settings on `AuthConfig` when using `auth=`, rather than mixing those legacy constructor arguments. Service accounts must have the target resources shared with them or appropriate delegated access.

See the [AuthConfig source](https://github.com/agno-agi/agno/blob/main/libs/agno/agno/tools/google/auth/credentials.py) for the full configuration.

## Developer Resources [#developer-resources]

* [Tools](https://github.com/agno-agi/agno/blob/main/libs/agno/agno/tools/google/sheets.py)
