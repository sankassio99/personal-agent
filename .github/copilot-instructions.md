# Finance Assistant operational instructions

Run all operational commands from the repository root.

## Run the application

Use the VPS launcher so the application runs in the background with the project virtual environment:

```bash
chmod +x start_vps.sh
./start_vps.sh
```

The launcher writes its process ID to `finance-assistant.pid` and its output to `bot.log`. Do not start a second instance when that PID file identifies a running process.

## Check logs

Inspect recent logs with:

```bash
tail -n 100 bot.log
```

Follow new entries while diagnosing a running instance:

```bash
tail -f bot.log
```

Never copy credentials, access tokens, user identifiers, spreadsheet IDs, or other sensitive data from logs into issues, pull requests, commits, or chat responses.

## Stop the application

Stop only the process registered by the project launcher:

```bash
chmod +x stop_vps.sh
./stop_vps.sh
```

The stop script validates the PID, sends the termination signal to that specific process, and removes `finance-assistant.pid`. Do not use process-name-based termination commands.

## OpenSpec workflow

Use the installed OpenSpec CLI for specification-driven changes:

```bash
openspec status --change "<change-name>" --json
openspec instructions apply --change "<change-name>" --json
```

Read every context file named by `instructions apply`, implement pending tasks, update their checkboxes, and validate before archiving:

```bash
openspec validate "<change-name>" --strict
openspec archive "<change-name>" --yes
```

Run the relevant tests with the project environment, for example:

```bash
.venv/bin/python3 -m pytest -q tests/unit
```
