import asyncio
import os
import sys
import aiohttp
from colorama import Fore, Style, init

init(autoreset=True)

PURPLE = Fore.MAGENTA + Style.BRIGHT
DARK_GRAY = Fore.BLACK + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
RED = Fore.RED + Style.BRIGHT
RESET = Style.RESET_ALL

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{PURPLE}==================================================")
    print(f"{PURPLE}                 WEBHOOK SPAMMER                  ")
    print(f"{PURPLE}==================================================")
    print(f"{DARK_GRAY} Status: Ready | Theme: Dark-Purple\n")

async def send_to_webhook(session, webhook_url, message, index, msg_num):
    payload = {"content": message}
    while True:
        try:
            async with session.post(webhook_url, json=payload) as response:
                if response.status in (200, 204):
                    print(f"{GREEN}[+] SUCCESS: Webhook #{index} (Msg {msg_num}) sent successfully.")
                    return True
                elif response.status == 429:
                    response_json = await response.json()
                    retry_after = response_json.get("retry_after", 1.0)
                    print(f"{RED}[-] RATELIMIT: Webhook #{index} (Msg {msg_num}) ratelimited. Retrying in {retry_after}s.")
                    await asyncio.sleep(retry_after)
                else:
                    print(f"{RED}[-] ERROR: Webhook #{index} (Msg {msg_num}) returned status {response.status}. Retrying in 2s.")
                    await asyncio.sleep(2)
        except Exception as e:
            print(f"{RED}[!] FAILURE: Connection error on Webhook #{index} ({type(e).__name__}). Retrying in 3s.")
            await asyncio.sleep(3)

async def main():
    print_banner()

    file_path = "webhooks.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            pass
        print(f"{RED}[!] '{file_path}' was not found. An empty file has been created.")
        print(f"{DARK_GRAY}Paste your webhook URLs line-by-line into '{file_path}'.")
        input(f"\n{PURPLE}Press ENTER to exit..."); return

    with open(file_path, "r", encoding="utf-8") as f:
        webhooks = [line.strip() for line in f if line.strip().startswith("http")]

    if not webhooks:
        print(f"{RED}[!] No valid webhook URLs found in '{file_path}'.")
        input(f"\n{PURPLE}Press ENTER to exit..."); return

    print(f"{PURPLE}[*] Successfully loaded {len(webhooks)} webhooks.\n")

    print(f"{PURPLE}message:")
    message = input(f"{DARK_GRAY}> {RESET}")

    if not message.strip():
        print(f"{RED}[!] Message content cannot be empty.")
        input(f"\n{PURPLE}Press ENTER to exit..."); return

    print(f"\n{PURPLE}messages per webhook:")
    try:
        msg_count = int(input(f"{DARK_GRAY}> {RESET}"))
        if msg_count <= 0:
            raise ValueError
    except ValueError:
        print(f"{RED}[!] invalid number entered.")
        input(f"\n{PURPLE}Press ENTER to exit..."); return

    print(f"\n{PURPLE}[*] cooking...\n")

    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, url in enumerate(webhooks, start=1):
            for msg_num in range(1, msg_count + 1):
                tasks.append(send_to_webhook(session, url, message, index, msg_num))
        
        await asyncio.gather(*tasks)

    print(f"\n{PURPLE}==================================================")
    print(f"{GREEN}[._.] done")
    print(f"{PURPLE}==================================================")
    input(f"\n{PURPLE}Press ENTER to close...")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
