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

## Getting Started

1. Create and activate a Python virtual environment:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
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
