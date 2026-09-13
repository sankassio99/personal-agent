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

   pip install -r requirements.txt  
   ```

2. Install the project in editable mode:

   ```bash
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

The package exposes a minimal Telegram bot entrypoint and MCP/server scaffolding that can be expanded in later development steps.

## Running tests

Install the project in editable mode, install the dependency requirements, then run the unit tests with Python directly:

```bash
python -m pip install -e .
python -m pip install -r requirements.txt
python -m pytest -q tests/unit/test_agno_gemini_base_agent.py --import-mode=importlib
```

This project uses a `src/` layout, so the import-mode flag avoids test collection issues when the repository is not installed into the active interpreter.

# VPS instructions
This happens because you are starting the application from within the shell session. When you close the SSH window, Linux ends that session and may send a signal (`SIGHUP`) to the processes attached to it — so your bot also stops.

### To keep it running after closing the terminal

For a quick test, use `nohup`:

Bash

```
cd /path/to/your/project
nohup .venv/bin/python -m your_package.main > bot.log 2>&1 < /dev/null &
```

Replace `your_package.main` with the real module of your application. To check:

Bash

```
tail -f bot.log
```

To stop it, find the process:

Bash

```
pgrep -af your_package
```

And terminate it using the correct PID:

Bash

```
kill PID
```

### To keep the bot running reliably

Use systemd. It keeps the process in the background, can restart it if it fails, and starts the service after VPS reboots. It is the option I recommend for your bot.

If you have already created the `finance-assistant` service, use:

Bash

```
sudo systemctl status finance-assistant
sudo systemctl enable --now finance-assistant
```

Monitor the logs:

Bash

```
sudo journalctl -u finance-assistant -f
```

If you have not created the service yet, send me the command you use to start the bot and the path to the project folder — without including tokens or `.env` content — and I will put together the `systemd` file with the correct paths.
