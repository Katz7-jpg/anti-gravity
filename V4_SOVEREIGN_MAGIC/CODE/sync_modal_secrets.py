import os
import subprocess
from dotenv import load_dotenv

load_dotenv(r"d:\AI_FACTORY\.env")

secrets = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "SUPABASE_URL": os.getenv("SUPABASE_URL"),
    "SUPABASE_SERVICE_ROLE_KEY": os.getenv("SUPABASE_SERVICE_ROLE_KEY")
}

# Construct the modal secret command
cmd = ["modal", "secret", "create", "v4-predator-secrets"]
for key, value in secrets.items():
    cmd.append(f"{key}={value}")

# Add force flag if it exists (overwrite)
cmd.append("--force")

print(f"Executing: {' '.join(cmd[:4])} ... [HIDDEN SECRETS]")
subprocess.run(cmd, check=True)
print("SUCCESS: v4-predator-secrets updated in Modal.")
