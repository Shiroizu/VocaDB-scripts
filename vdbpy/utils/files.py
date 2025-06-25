import os
import sys
from pathlib import Path

from vdbpy.utils.console import get_credentials_from_console, prompt_choice
from vdbpy.utils.logger import get_logger

logger = get_logger()


def get_lines(filename: str) -> list[str]:
    """Safely read lines from a file. Create file and return an empty list if necessary."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not os.path.isfile(filename):
        logger.debug(f"File '{filename}' not found. Creating an empty file.")
        with open(filename, "w") as f:
            f.write("")

    with open(filename, encoding="utf8") as f:
        return f.read().splitlines()


def get_credentials(credentials_path: str, account_name: str = "") -> tuple[str, str]:
    """Load credentials from the credentials file.

    -------- file start
    username
    password

    username2
    password2
    -------- file end

    Multiple credentials are separated by an empty line.
    """
    credentials = {}

    lines = get_lines(credentials_path)
    lines = [line.strip() for line in lines if line.strip()]

    if len(lines) % 2 != 0:
        logger.warning("Credentials file has an odd number of non-empty lines!")
        sys.exit()

    for i in range(0, len(lines), 2):
        account = lines[i]
        password = lines[i + 1]
        credentials[account] = password

    if not credentials:
        logger.warning("Credentials not found")
        logger.warning(
            "Create a 'credentials.env' to skip this step, with the following format:"
        )
        logger.warning("------------------------------")
        logger.warning("account_name")
        logger.warning("password")
        logger.warning("------------------------------\n")

        # get from console:
        return get_credentials_from_console()

    if account_name:
        if account_name in credentials:
            return (account_name, credentials[account_name])

        logger.warning(f"Credentials for '{account_name}' not found")
        sys.exit(0)

    if len(credentials) == 1:
        acc, pw = next(iter(credentials.items()))
        return (str(acc), str(pw))

    selected_account = prompt_choice(list(credentials.keys()))
    return (selected_account, credentials[selected_account])


def save_file(filepath: str, content: str | list, append=False) -> None:
    """Safely writes content to a file, creating necessary directories."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w"
    if append:
        mode = "a"

    with path.open(mode, encoding="utf-8") as f:
        if isinstance(content, list):
            content = list(map(str, content))
            f.write("\n".join(content))
        else:
            f.write(str(content))
        if append:
            f.write("\n")


def clear_file(filepath: str):
    """Clear file if it exists."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        _ = input(f"Clearing file '{filepath}'. Press enter to continue.'")

    with path.open("w", encoding="utf-8") as f:
        f.write("")
