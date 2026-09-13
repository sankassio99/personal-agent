# Finance Assistant

A clean Python project skeleton for a Telegram-enabled finance assistant with MCP tools and Google Sheets infrastructure integration.

## Project Structure

```text
src/
  finance_assistant/
    telegram/
    application/
    agent/
    domain/
    mcp/
    infrastructure/
    config/
```

## Environment

Copy `.env.example` to `.env` and fill in the required values.

The Google Sheets capability is optional and expects the following environment values to be declared when the integration is enabled:

```bash
export GOOGLE_CLIENT_ID=your_client_id_here
export GOOGLE_CLIENT_SECRET=your_client_secret_here
export GOOGLE_PROJECT_ID=your_project_id_here
export GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json
```

## Getting Started

1. Create and activate a Python virtual environment:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install the project depedencies and in editable mode:

   ```bash
   pip install -r requirements.txt  

   pip install -e .
   ```

3. Copy the example environment file:

   ```bash
   copy .env.example .env
   ```

4. Add your Telegram token and Google Sheets credentials values in `.env`.

5. Run the application:

   ```bash
   python -m finance_assistant.main
   ```

### Linux VPS background launcher

A launcher script is included in the repository root to start the app in the same background style described in the VPS notes:

```bash
cd /path/to/your/project
chmod +x start_vps.sh
./start_vps.sh
```

The script uses the virtual environment Python when available, otherwise it falls back to `python3` or `python`, writes the process output to `bot.log`, and stores the background process PID in `finance-assistant.pid`.

## Running tests

```bash
python -m pytest -q tests/unit/test_agno_gemini_base_agent.py
```