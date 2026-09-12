"""Main application entrypoint."""
from finance_assistant.telegram.bot import run_bot

def main() -> None:
    """Main execution entrypoint."""
    run_bot()

if __name__ == "__main__":
    main()
