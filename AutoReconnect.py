import os
import time
import json
import subprocess
from rich.console import Console
from rich.prompt import Prompt

console = Console()

# File paths
ACCOUNT_INFO_FILE = "/sdcard/Download/account_info.json"
AUTO_EXECUTE_FILE = "/sdcard/Download/auto_execute.lua"

ROBLOX_PACKAGE = "com.roblox.client"

def is_roblox_running():
    """Check if Roblox is running."""
    try:
        result = subprocess.check_output(["pgrep", "-f", ROBLOX_PACKAGE], stderr=subprocess.DEVNULL)
        return bool(result.strip())
    except subprocess.CalledProcessError:
        return False

def get_accounts_from_executors(executors_dir):
    """Retrieve account information from Roblox executor files."""
    accounts = []
    if os.path.exists(executors_dir):
        for filename in os.listdir(executors_dir):
            if filename.endswith(".lua"):  # Assuming executor files are Lua scripts
                try:
                    with open(os.path.join(executors_dir, filename), "r") as f:
                        executor_content = f.read()
                        # Extract username and user ID from the executor file (adjust this based on your executor file format)
                        username = extract_username_from_executor(executor_content) 
                        user_id = extract_user_id_from_executor(executor_content)
                        accounts.append({"username": username, "user_id": user_id})
                except Exception as e:
                    console.log(f"[red]Error reading executor file {filename}: {e}")
    else:
        console.log(f"[red]Executor directory '{executors_dir}' not found.")
    return accounts

def extract_username_from_executor(executor_content):
    # Replace this with your actual logic to extract username from the executor content
    # For example:
    start_index = executor_content.find("username: ") + len("username: ")
    end_index = executor_content.find("'", start_index)
    return executor_content[start_index:end_index]

def extract_user_id_from_executor(executor_content):
    # Replace this with your actual logic to extract user ID from the executor content
    # For example:
    start_index = executor_content.find("userId: ") + len("userId: ")
    end_index = executor_content.find("'", start_index)
    return executor_content[start_index:end_index]

def view_info():
    """View signed-in Roblox account info and provide options."""
    accounts = get_signed_in_accounts()
    if accounts:
        console.print("[bold cyan]Signed-In Accounts:")
        for i, account in enumerate(accounts, start=1):
            console.print(f"{i}. Username: {account['username']}, User ID: {account['user_id']}")

        while True:
            choice = Prompt.ask("Enter account number to join (or 'q' to quit): ", choices=[str(i) for i in range(1, len(accounts) + 1)] + ["q"])

            if choice == "q":
                break
            else:
                try:
                    account_index = int(choice) - 1
                    selected_account = accounts[account_index]
                    game_id = Prompt.ask("Enter Game ID or leave blank for main menu: ")
                    reconnect_roblox(game_id=game_id)
                except (ValueError, IndexError):
                    console.log("[red]Invalid account number.")
    else:
        console.log("[red]No accounts detected. Make sure Roblox is logged in.")

def setup_accounts():
    """Set up account information with Game ID."""
    executors_dir = input("Enter the path to your executors directory: ")
    accounts = get_accounts_from_executors(executors_dir)

    if accounts:
        console.print("[bold cyan]Found accounts in executors:")
        for i, account in enumerate(accounts, start=1):
            console.print(f"{i}. Username: {account['username']}, User ID: {account['user_id']}")

        # Save account information to file (optional)
        account_data = {
            "accounts": accounts
        }
        with open(ACCOUNT_INFO_FILE, "w") as f:
            json.dump(account_data, f)
        console.log(f"[green]Account information saved to {ACCOUNT_INFO_FILE}")
    else:
        console.log("[red]No accounts found in the specified directory.")

def reconnect_roblox(game_id=None):
    """Reconnect Roblox by restarting the app."""
    console.log("[red]Reconnecting Roblox...")
    os.system(f"am force-stop {ROBLOX_PACKAGE}")
    time.sleep(2)
    if game_id:
        os.system(f"am start -a android.intent.action.VIEW -d roblox://placeID={game_id}")
        console.log(f"[green]Reconnected to game ID: {game_id}")
    else:
        os.system(f"am start -n {ROBLOX_PACKAGE}/com.roblox.client.startup.EntryActivity")
        console.log("[green]Reconnected to Roblox app!")

def setup_auto_execute():
    """Setup an auto-execute script."""
    console.print("[bold green]Paste the script below (type 'end' to finish):")
    script_lines = []
    while True:
        line = input()
        if line.strip().lower() == "end":
            break
        script_lines.append(line)
    with open(AUTO_EXECUTE_FILE, "w") as file:
        file.write("\n".join(script_lines))
    console.log(f"[green]Script saved to {AUTO_EXECUTE_FILE}")

def start_auto_rejoin():
    """Start the auto-rejoin process."""
    if os.path.exists(ACCOUNT_INFO_FILE):
        with open(ACCOUNT_INFO_FILE, "r") as file:
            account_data = json.load(file)
        game_id = account_data.get("game_id")
        while True:
            if not is_roblox_running():
                reconnect_roblox(game_id=game_id)
            else:
                console.log("[blue]Roblox is running.")
            time.sleep(60)
    else:
        console.log("[red]No account information found. Please set up accounts first.")

def main_menu():
    """Main menu for user options."""
    while True:
        console.print("[bold cyan]\n--- Auto Rejoin Menu ---")
        console.print("1. Start Auto Rejoin")
        console.print("2. Setup Accounts")
        console.print("3. View Info & Join")
        console.print("4. Setup Auto Execute Script")
        console.print("5. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            start_auto_rejoin()
        elif choice == "2":
            setup_accounts()
        elif choice == "3":
            view_info()
        elif choice == "4":
            setup_auto_execute()
        elif choice == "5":
            console.print("[bold red]Exiting...")
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.")

if __name__ == "__main__":
    console.print("[bold green]Starting Roblox Auto Rejoin System...")
    main_menu()
