import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
H1_GRAPHQL_URL = "https://hackerone.com/graphql"
STATE_FILE = "known_programs.json"

def send_discord_alert(program_name, program_url, offer_bounty):
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not found!")
        return

    data = {
        "username": "Bug Bounty Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [
            {
                "title": f"🆕 New Program Launched: {program_name}",
                "description": "A new bug bounty program has appeared on HackerOne!",
                "url": program_url,
                "color": 5814783,
                "fields": [
                    {
                        "name": "Bounty Offered?",
                        "value": "💰 YES" if offer_bounty else "❌ VDP Only",
                        "inline": True
                    },
                    {
                        "name": "Platform",
                        "value": "HackerOne",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }
        ]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"Alert sent for {program_name}")
    except Exception as e:
        print(f"Error sending webhook: {e}")

def get_h1_programs():
    query = """
    query DirectoryQuery($cursor: String) {
      teams(
        first: 10
        order_by: {field: launched_at, direction: DESC}
        secure_handling_enabled: true
      ) {
        edges {
          node {
            handle
            name
            offers_bounties
            launched_at
          }
        }
      }
    }
    """
    try:
        r = requests.post(H1_GRAPHQL_URL, json={'query': query}, headers={"Content-Type": "application/json"})
        return r.json()['data']['teams']['edges']
    except:
        return []

def main():
    known_programs = []
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            try:
                known_programs = json.load(f)
            except:
                known_programs = []

    latest_programs = get_h1_programs()
    new_discoveries = []
    current_handles = []

    for item in latest_programs:
        program = item['node']
        handle = program['handle']
        current_handles.append(handle)
        
        if handle not in known_programs:
            url = f"https://hackerone.com/{handle}"
            send_discord_alert(program['name'], url, program['offers_bounties'])
            new_discoveries.append(handle)
    
    updated_list = list(set(known_programs + new_discoveries))
    if len(updated_list) > 500: updated_list = updated_list[-500:]

    with open(STATE_FILE, "w") as f:
        json.dump(updated_list, f)

if __name__ == "__main__":
    main()
