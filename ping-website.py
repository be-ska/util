#!/usr/bin/env python3

import hashlib
import time
import requests
import subprocess
import platform
import webbrowser

URL = "https://www.dpss.unipd.it/esame-di-stato-2026-II-commissione"
CHECK_INTERVAL = 60  # seconds


def get_page_hash():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    # Hash webpage content
    return hashlib.sha256(response.text.encode()).hexdigest()


def notify(title, message):
    system = platform.system()

    if system == "Darwin":  # macOS
        subprocess.run([
            "osascript",
            "-e",
            f'display notification "{message}" with title "{title}"'
        ])

    elif system == "Linux":
        subprocess.run([
            "notify-send",
            title,
            message
        ])

    else:
        print(f"[NOTIFICATION] {title}: {message}")


def main():
    print(f"Monitoring: {URL}")

    old_hash = get_page_hash()

    while True:
        try:
            time.sleep(CHECK_INTERVAL)

            new_hash = get_page_hash()

            if new_hash != old_hash:
                print("Webpage changed!")
                webbrowser.open(URL)
                notify("Webpage Changed", URL)
                return

            else:
                print("No change.")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
