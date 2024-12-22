import os
from pathlib import Path

def fmp_set_api_key(): # pragma: no cover
    """
    Set the Financial Modeling Prep API key.

    This function prompts the user to input their Financial Modeling Prep (FMP)
    API key and saves it to a `.Renviron` file, either in the project directory
    or the home directory. It also gives the user the option to add `.Renviron`
    to `.gitignore` for security purposes.
    """
    fmp_api_key = prompt_api_key()
    location_choice = prompt_location()

    if location_choice.lower() == "project":
        renviron_path = Path(os.getcwd()) / ".env"
        gitignore_path = Path(os.getcwd()) / ".gitignore"
    elif location_choice.lower() == "home":
        renviron_path = Path.home() / ".env"
        gitignore_path = Path.home() / ".gitignore"
    else:
        print("Invalid choice. Please start again and enter 'project' or 'home'.")

    if renviron_path.exists():
        with renviron_path.open("r") as file:
            env_lines = file.readlines()
    else:
        env_lines = []

    fmp_api_key_exists = any(line.startswith("FMP_API_KEY=") for line in env_lines)

    if fmp_api_key_exists:
        overwrite_choice = prompt_overwrite()
        if overwrite_choice.lower() != "yes":
            print("Aborted. API key already exists and is not overwritten.")

    if gitignore_path.exists():
        add_gitignore = prompt_gitignore()
        if add_gitignore.lower() == "yes":
            with gitignore_path.open("r") as file:
                gitignore_lines = file.readlines()
            if ".env\n" not in gitignore_lines:
                gitignore_lines.append(".env\n")
                with gitignore_path.open("w") as file:
                    file.writelines(gitignore_lines)
                print(".env added to .gitignore.")
        elif add_gitignore.lower() == "no":
            print(".env NOT added to .gitignore.")
        else:
            print("Invalid choice. Please start again and enter 'yes' or 'no'.")

    env_lines = [line for line in env_lines if not line.startswith("FMP_API_KEY=")]
    env_lines.append(f"FMP_API_KEY={fmp_api_key}\n")

    with renviron_path.open("w") as file:
        file.writelines(env_lines)

    print(
        f"FMP API key has been set and saved in {renviron_path} in your "
        f"{location_choice} directory. Please restart your session to load the new environment."
    )

def prompt_api_key(): # pragma: no cover
    return input("Enter your FMP API key: ")

def prompt_location(): # pragma: no cover
    return input(
        "Where do you want to store the .env file? "
        "Enter 'project' for project directory or 'home' for home directory: "
    )

def prompt_gitignore(): # pragma: no cover
    return input(
        "Do you want to add .env to .gitignore? "
        "It is highly recommended! Enter 'yes' or 'no': "
    )

def prompt_overwrite(): # pragma: no cover
    return input(
        "API key already exists. Do you want to overwrite it? Enter 'yes' or 'no': "
    )
