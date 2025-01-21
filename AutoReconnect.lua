import os
import time
import json
import subprocess
from rich.console import Console

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

def get_signed_in_accounts():
    """Retrieve signed-in accounts from Roblox app's data directory."""
    data_dir = f"/data/data/{ROBLOX_PACKAGE}/shared_prefs/"
    accounts = []

    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        for file in files:
            if file.startswith("roblox_account"):
                try:
                    file_path = os.path.join(data_dir, file)
                    with open(file_path, "r") as f:
                        account_data = json.load(f)
                        username = account_data.get("username", "Unknown")
                        user_id = account_data.get("userId", "Unknown")
                        accounts.append({"username": username, "user_id": user_id})
                except Exception as e:
                    console.log(f"[red]Error reading account file {file}: {e}")
    else:
        console.log("[red]Roblox data directory not accessible. Grant Termux root permissions.")

    return accounts

def view_info():
    """View signed-in Roblox account info."""
    accounts = get_signed_in_accounts()
    if accounts:
        console.print("[bold cyan]Signed-In Accounts:")
        for i, account in enumerate(accounts, start=1):
            console.print(f"{i}. Username: {account['username']}, User ID: {account['user_id']}")
    else:
        console.log("[red]No accounts detected. Make sure Roblox is logged in.")

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
        console.print("2. View Info")
        console.print("3. Setup Auto Execute Script")
        console.print("4. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            start_auto_rejoin()
        elif choice == "2":
            view_info()
        elif choice == "3":
            setup_auto_execute()
        elif choice == "4":
            console.print("[bold red]Exiting...")
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.")

if __name__ == "__main__":
    console.print("[bold green]Starting Roblox Auto Rejoin System...")
    main_menu()
