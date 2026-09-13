"""Main application entrypoint."""
import logging

from finance_assistant.adapters.telegram.bot import run_bot

logging.basicConfig(level=logging.INFO)

def main() -> None:
    """Main execution entrypoint."""
    run_bot()

if __name__ == "__main__":
    main()
