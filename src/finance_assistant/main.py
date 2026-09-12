"""Main application entrypoint."""
from finance_assistant.telegram.bot import run_bot
import logging

logging.basicConfig(level=logging.INFO)

def main() -> None:
    """Main execution entrypoint."""
    run_bot()

if __name__ == "__main__":
    main()
