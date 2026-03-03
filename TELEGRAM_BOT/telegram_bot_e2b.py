"""
Telegram Bot - E2B Sandbox Version (ELITE_UI Mode)
====================================================
PRIMARY LISTENER - This is the single source of truth for Telegram bot operations.

This bot runs in E2B sandbox, polls Telegram for updates, and processes commands.

Features:
- ELITE_UI mode with Neural Bridge Interface
- Deletes existing webhook before polling
- Polls for 60 seconds (configurable)
- Processes commands: /start, /ping, /status, /list, /delete, /help
- /ping command with Supabase latency testing
- Handles document uploads
- Sends appropriate responses

NOTE: This file is the PRIMARY listener. Do not run other bot instances simultaneously.
"""

import os
import sys
import requests
import time
import logging
from datetime import datetime

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - Use environment variables or defaults
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8662713589:AAFdXNP_QqYlIGpu-55BomT7zzneTJgUVX8')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ukqycwqzopyxbhkiaorr.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVrcXljd3F6b3B5eGJoa2lhb3JyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTMxMDM0NCwiZXhwIjoyMDg2ODg2MzQ0fQ.Ilq9MxJAcabL2Fa5_xe4yIXk2_3EHr6cy4XgPAmbEVw')
PDF_BUCKET = 'pdf-uploads'

# Polling duration (seconds)
POLL_DURATION = int(os.getenv('POLL_DURATION', '60'))

# Telegram API URL
TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# Track last update ID to avoid duplicate processing
last_update_id = 0

# =============================================================================
# SCALPEL_PRECISION_V2 - File List Cache
# Cache for mapping list numbers to file names (persists between commands)
# =============================================================================
file_list_cache = {}  # {chat_id: [file_name1, file_name2, ...]}

# =============================================================================
# ELITE_UI MODE CONFIGURATION
# =============================================================================

ELITE_BANNER = """
╔══════════════════════════════════════╗
║     🧠 NEURAL BRIDGE INTERFACE 🧠     ║
║          ELITE_UI MODE               ║
╚══════════════════════════════════════╝
"""

ELITE_COMMANDS = [
    ("start", "Initialize Neural Bridge"),
    ("ping", "Test connection latency"),
    ("status", "System status"),
    ("list", "List synced documents"),
    ("summary", "Get storytelling summary [number]"),
    ("delete", "Remove a document [number]"),
    ("search", "Search vault content [query]"),
    ("purge", "Nuclear purge - Delete all documents"),
    ("help", "Show all commands"),
]


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def delete_webhook():
    """Delete any existing webhook to enable polling mode"""
    try:
        response = requests.get(
            f"{TELEGRAM_API}/deleteWebhook",
            params={"drop_pending_updates": True},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info("✅ Webhook deleted successfully - polling mode enabled")
                return True
            else:
                logger.warning(f"⚠️ Webhook deletion returned: {result}")
        else:
            logger.error(f"❌ Failed to delete webhook: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error deleting webhook: {e}")
    return False


def get_bot_info():
    """Get bot information to verify connection"""
    try:
        response = requests.get(f"{TELEGRAM_API}/getMe", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                bot_info = result.get('result', {})
                logger.info(f"🤖 Bot: @{bot_info.get('username', 'unknown')} ({bot_info.get('first_name', 'Unknown')})")
                return bot_info
        logger.error("❌ Failed to get bot info")
    except Exception as e:
        logger.error(f"❌ Error getting bot info: {e}")
    return None


def register_commands():
    """Register bot commands with Telegram API"""
    try:
        commands_payload = [{"command": cmd, "description": desc} for cmd, desc in ELITE_COMMANDS]
        response = requests.post(
            f"{TELEGRAM_API}/setMyCommands",
            json={"commands": commands_payload},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info("✅ Commands registered successfully")
                return True
            else:
                logger.warning(f"⚠️ Command registration returned: {result}")
        else:
            logger.error(f"❌ Failed to register commands: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error registering commands: {e}")
    return False


def send_message(chat_id, text):
    """Send message to Telegram chat with Markdown formatting"""
    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"✅ Message sent to chat {chat_id}")
            return True
        else:
            logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
    return False


def get_updates(offset=None, timeout=30):
    """Get updates from Telegram using long polling"""
    try:
        params = {"timeout": timeout}
        if offset:
            params["offset"] = offset
        
        response = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params=params,
            timeout=timeout + 5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                return result.get("result", [])
        else:
            logger.error(f"❌ Failed to get updates: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error getting updates: {e}")
    return []


def list_pdfs():
    """List all PDFs from Supabase storage"""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/list/{PDF_BUCKET}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={"prefix": "", "limit": 100},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        logger.error(f"❌ Failed to list PDFs: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error listing PDFs: {e}")
    return []


def delete_pdf(filename):
    """Delete a PDF from Supabase storage"""
    try:
        response = requests.delete(
            f"{SUPABASE_URL}/storage/v1/object/{PDF_BUCKET}/{filename}",
            headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=10
        )
        return response.status_code in [200, 204]
    except Exception as e:
        logger.error(f"❌ Error deleting PDF: {e}")
    return False


# =============================================================================
# SUPABASE LATENCY TESTING
# =============================================================================

def test_supabase_latency():
    """
    Test Supabase connection and measure latency.
    
    Returns:
        tuple: (latency_ms, success, error_message)
    """
    start_time = time.time()
    
    try:
        # Test connection by querying the documents table
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            params={"select": "id", "limit": "1"},
            timeout=10
        )
        
        end_time = time.time()
        latency_ms = round((end_time - start_time) * 1000, 2)
        
        if response.status_code in [200, 206]:
            return (latency_ms, True, None)
        else:
            return (latency_ms, False, f"HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        end_time = time.time()
        latency_ms = round((end_time - start_time) * 1000, 2)
        return (latency_ms, False, "Connection timeout")
        
    except Exception as e:
        end_time = time.time()
        latency_ms = round((end_time - start_time) * 1000, 2)
        return (latency_ms, False, str(e)[:50])


def check_supabase_status():
    """Check Supabase connection status"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            timeout=5
        )
        return "✅" if response.status_code in [200, 404] else "❌"
    except:
        return "❌"


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def handle_start(chat_id):
    """Handle /start command with ELITE_UI banner"""
    send_message(chat_id, f"""```
{ELITE_BANNER}
```
Welcome to the Neural Bridge, Operator.

*Available Commands:*
• /ping - Test connection latency
• /status - System status
• /list - List synced documents
• /summary \[number] - Get document summary
• /delete \[number] - Remove a document
• /search \[query] - Search vault content
• /help - Show all commands

_Ready to sync your neurons..._""")


def handle_ping(chat_id):
    """Handle /ping command with Supabase latency testing"""
    send_message(chat_id, "🏓 Testing connection...")
    
    latency_ms, success, error = test_supabase_latency()
    
    if success:
        send_message(chat_id, f"""🏓 *PONG*

Latent Latency: `{latency_ms}ms`
Status: ✅ Connected
Database: ✅ Responding

_Neural bridge stable._""")
    else:
        send_message(chat_id, f"""🏓 *PONG*

Latent Latency: `{latency_ms}ms`
Status: ❌ Error
Message: `{error}`

_Check Supabase configuration._""")


def handle_status(chat_id):
    """Handle /status command"""
    supabase_status = check_supabase_status()
    
    # Get bot uptime info
    latency_ms, _, _ = test_supabase_latency()
    
    send_message(chat_id, f"""*System Status*

☁️ Supabase: {supabase_status}
🤖 Telegram: ✅
📊 Latency: `{latency_ms}ms`

_Mode: ELITE_UI_
_All systems operational._""")


def list_unique_documents():
    """
    Query Supabase for DISTINCT metadata->>file_name from documents table.
    
    Returns:
        list: List of unique file names
    """
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            params={"select": "metadata->>file_name"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            # Extract unique file names
            unique_files = list(set(
                item.get('file_name') for item in data
                if item.get('file_name')
            ))
            unique_files.sort()  # Sort alphabetically
            return unique_files
        else:
            logger.error(f"❌ Failed to list documents: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"❌ Error listing documents: {e}")
        return []


def handle_list(chat_id):
    """Handle /list command - Lists unique PDFs from documents table"""
    global file_list_cache
    
    send_message(chat_id, "📋 Fetching your documents...")
    
    unique_files = list_unique_documents()
    
    if unique_files:
        # Cache the file list for this chat
        file_list_cache[chat_id] = unique_files
        
        msg = "*📚 Your Document Vault*\n\n"
        for i, filename in enumerate(unique_files, 1):
            # Truncate long filenames
            display_name = filename if len(filename) <= 30 else filename[:27] + "..."
            msg += f"{i}. `{display_name}`\n"
        
        msg += f"\n📊 *Total:* {len(unique_files)} documents"
        msg += "\n\n_Use /summary [number] for details._"
        msg += "\n_Use /delete [number] to remove._"
        send_message(chat_id, msg)
    else:
        send_message(chat_id, "📭 No documents in your Vault yet.\n\nSend me a PDF to get started!")


def get_document_summary(file_name):
    """
    Retrieve storytelling_summary from metadata for a specific file.
    
    Args:
        file_name: The file name to search for
        
    Returns:
        dict: Summary data or None if not found
    """
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            params={
                "select": "metadata->>storytelling_summary,metadata->>file_name,created_at",
                "metadata->>file_name": f"eq.{file_name}",
                "limit": "1"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
        return None
    except Exception as e:
        logger.error(f"❌ Error getting summary: {e}")
        return None


def handle_summary(chat_id, args):
    """Handle /summary command - Get storytelling summary of a specific PDF"""
    global file_list_cache
    
    if not args:
        send_message(chat_id, "❌ Usage: /summary [number]\n\nUse /list to see document numbers.")
        return
    
    try:
        index = int(args) - 1
        
        # Check if we have cached files for this chat
        if chat_id not in file_list_cache or not file_list_cache[chat_id]:
            send_message(chat_id, "❌ No cached file list. Use /list first to refresh.")
            return
        
        cached_files = file_list_cache[chat_id]
        
        if 0 <= index < len(cached_files):
            filename = cached_files[index]
            send_message(chat_id, f"📖 Fetching summary for: `{filename}`...")
            
            summary_data = get_document_summary(filename)
            
            if summary_data and summary_data.get('storytelling_summary'):
                summary = summary_data['storytelling_summary']
                created = summary_data.get('created_at', 'Unknown')
                
                # Truncate long summaries
                if len(summary) > 3000:
                    summary = summary[:2997] + "..."
                
                send_message(chat_id, f"""📖 *Document Summary*

*File:* `{filename}`
*Added:* `{created}`

*Storytelling Summary:*
{summary}

_Use /delete {args} to remove this document._""")
            else:
                send_message(chat_id, f"⚠️ No summary available for `{filename}`.\n\n_The document may still be processing._")
        else:
            send_message(chat_id, "❌ Invalid number. Use /list to see documents.")
    except ValueError:
        send_message(chat_id, "❌ Invalid number. Use /list to see documents.")


def delete_document_by_filename(file_name):
    """
    Delete all documents with matching file_name from documents table.
    
    Args:
        file_name: The file name to delete
        
    Returns:
        tuple: (success, count_deleted, error_message)
    """
    try:
        # First count how many will be deleted
        count_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "count=exact"
            },
            params={
                "select": "id",
                "metadata->>file_name": f"eq.{file_name}"
            },
            timeout=10
        )
        
        doc_count = 0
        if count_response.status_code == 200:
            doc_count = len(count_response.json())
        
        # Delete the documents
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            params={
                "metadata->>file_name": f"eq.{file_name}"
            },
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            return (True, doc_count, None)
        else:
            return (False, 0, f"HTTP {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error deleting document: {e}")
        return (False, 0, str(e)[:50])


def handle_delete(chat_id, args):
    """Handle /delete command - Delete by file name from documents table"""
    global file_list_cache
    
    if not args:
        send_message(chat_id, "❌ Usage: /delete [number]\n\nUse /list to see document numbers.")
        return
    
    try:
        index = int(args) - 1
        
        # Check if we have cached files for this chat
        if chat_id not in file_list_cache or not file_list_cache[chat_id]:
            send_message(chat_id, "❌ No cached file list. Use /list first to refresh.")
            return
        
        cached_files = file_list_cache[chat_id]
        
        if 0 <= index < len(cached_files):
            filename = cached_files[index]
            send_message(chat_id, f"🗑️ Deleting: `{filename}`...")
            
            success, count, error = delete_document_by_filename(filename)
            
            if success:
                # Remove from cache
                file_list_cache[chat_id].pop(index)
                
                send_message(chat_id, f"""✅ *Deleted Successfully*

*File:* `{filename}`
*Chunks removed:* {count}

_The document has been purged from your Vault._""")
            else:
                send_message(chat_id, f"⚠️ Failed to delete `{filename}`\n\nError: `{error}`")
        else:
            send_message(chat_id, "❌ Invalid number. Use /list to see documents.")
    except ValueError:
        send_message(chat_id, "❌ Invalid number. Use /list to see documents.")


def search_documents(query, limit=3):
    """
    Perform vector search on documents table.
    
    Args:
        query: Search query string
        limit: Maximum number of results
        
    Returns:
        list: List of matching documents with storytelling snippets
    """
    try:
        # Try RPC function first (if available in Supabase)
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/search_documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "limit": limit
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()
        
        # Fallback: Simple text search on metadata->>storytelling_summary
        logger.info("📡 RPC not available, using fallback text search...")
        
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            params={
                "select": "metadata->>file_name,metadata->>storytelling_summary",
                "metadata->>storytelling_summary": f"ilike.%{query}%",
                "limit": str(limit)
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        
        return []
        
    except Exception as e:
        logger.error(f"❌ Error searching documents: {e}")
        return []


def handle_search(chat_id, args):
    """Handle /search command - Search for relevant content in the vault"""
    if not args:
        send_message(chat_id, "❌ Usage: /search [query]\n\nExample: /search artificial intelligence")
        return
    
    query = args.strip()
    send_message(chat_id, f"🔍 Searching for: `{query}`...")
    
    results = search_documents(query, limit=3)
    
    if results:
        msg = f"🔍 *Search Results*\n\n*Query:* `{query}`\n\n"
        
        for i, result in enumerate(results, 1):
            filename = result.get('file_name', 'Unknown')
            summary = result.get('storytelling_summary', '')
            
            # Truncate summary for display
            if len(summary) > 500:
                summary = summary[:497] + "..."
            
            msg += f"*{i}. {filename}*\n"
            msg += f"_{summary}_\n\n"
        
        msg += "_Use /list to see all documents._"
        send_message(chat_id, msg)
    else:
        send_message(chat_id, f"🔍 No results found for: `{query}`\n\n_Try different keywords or check if documents are indexed._")


def handle_help(chat_id):
    """Handle /help command"""
    send_message(chat_id, """📖 *Neural Bridge Guide*

*Commands:*
• /list - List all documents in vault
• /summary [number] - Get storytelling summary
• /delete [number] - Remove a document
• /search [query] - Search vault content
• /ping - Test connection latency
• /status - System status
• /purge - Delete ALL documents (danger!)

*DOs:*
✅ Send PDFs (max 20MB)
✅ Use /list to track your files
✅ Use /summary to preview content
✅ Use /search to find information

*DONTs:*
❌ Don't send encrypted PDFs
❌ Don't send password-protected files
❌ Don't send non-PDF files

*Processing:*
1. Upload PDF here
2. GitHub Actions extracts text
3. AI generates embeddings & summaries
4. You get notified

*Tips:*
• Smaller files process faster
• Clear scans work best
• English text preferred

_The Neural Bridge awaits your input._""")


# =============================================================================
# NUCLEAR PURGE FUNCTIONALITY
# =============================================================================

def send_message_with_keyboard(chat_id, text, keyboard):
    """Send message with inline keyboard to Telegram chat"""
    try:
        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": keyboard
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"✅ Message with keyboard sent to chat {chat_id}")
            return True
        else:
            logger.error(f"❌ Failed to send message with keyboard: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"❌ Error sending message with keyboard: {e}")
    return False


def edit_message(chat_id, message_id, text):
    """Edit an existing message"""
    try:
        response = requests.post(
            f"{TELEGRAM_API}/editMessageText",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text,
                "parse_mode": "Markdown"
            },
            timeout=10
        )
        if response.status_code == 200:
            logger.info(f"✅ Message {message_id} edited")
            return True
        else:
            logger.error(f"❌ Failed to edit message: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Error editing message: {e}")
    return False


def purge_all_documents():
    """
    Nuclear purge - Delete all documents from Supabase documents table.
    
    Returns:
        tuple: (success, count, error_message)
    """
    try:
        # First, count documents
        count_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "count=exact"
            },
            params={"select": "id"},
            timeout=10
        )
        
        doc_count = 0
        if count_response.status_code == 200:
            doc_count = len(count_response.json())
        
        # Execute nuclear purge - delete all rows where id != 0 (always true)
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            params={"id": "neq.0"},  # Delete all rows where id != 0
            timeout=30
        )
        
        if response.status_code in [200, 204]:
            logger.info(f"✅ NUCLEAR PURGE COMPLETE - {doc_count} documents deleted")
            return (True, doc_count, None)
        else:
            return (False, 0, f"HTTP {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Nuclear purge failed: {e}")
        return (False, 0, str(e)[:50])


def handle_purge(chat_id):
    """Handle /purge command with confirmation dialog"""
    keyboard = {
        "inline_keyboard": [
            [{"text": "⚠️ CONFIRM PURGE", "callback_data": "confirm_purge"}],
            [{"text": "❌ CANCEL", "callback_data": "cancel_purge"}]
        ]
    }
    
    send_message_with_keyboard(
        chat_id,
        "🔴 *NUCLEAR PURGE REQUESTED*\n\n"
        "This will delete ALL documents from the vault.\n"
        "This action cannot be undone.\n\n"
        "_Are you sure?_",
        keyboard
    )


def handle_callback_query(callback_query):
    """Handle callback queries from inline keyboards"""
    query_id = callback_query.get("id")
    query_data = callback_query.get("data", "")
    message = callback_query.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    
    # Answer the callback query to remove loading state
    try:
        requests.post(
            f"{TELEGRAM_API}/answerCallbackQuery",
            json={"callback_query_id": query_id},
            timeout=5
        )
    except:
        pass
    
    if query_data == "confirm_purge":
        logger.info(f"🔥 NUCLEAR PURGE INITIATED by chat {chat_id}")
        
        # Execute nuclear purge
        success, count, error = purge_all_documents()
        
        if success:
            edit_message(
                chat_id,
                message_id,
                f"✅ *VAULT PURGED*\n\n"
                f"All documents have been deleted.\n"
                f"Documents removed: `{count}`\n"
                f"The vault is now empty.\n\n"
                f"_Purged at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
            )
        else:
            edit_message(
                chat_id,
                message_id,
                f"❌ *PURGE FAILED*\n\n"
                f"Error: `{error}`\n\n"
                f"_Check Supabase configuration._"
            )
    
    elif query_data == "cancel_purge":
        edit_message(
            chat_id,
            message_id,
            "❌ *PURGE CANCELLED*\n\n"
            "The vault remains intact.\n"
            "_No documents were deleted._"
        )


def handle_document(chat_id, document):
    """Handle document upload"""
    filename = document.get('file_name', 'unknown.pdf')
    file_size = document.get('file_size', 0) / (1024 * 1024)  # Convert to MB
    
    send_message(chat_id, f"""📄 *Document Received*

*File:* `{filename}`
*Size:* {file_size:.2f} MB

🔄 Waking up GitHub Worker...

_Neural sync in progress..._""")


def process_update(update):
    """Process a single update from Telegram"""
    global last_update_id
    
    # Update last processed ID
    last_update_id = update["update_id"]
    
    # Handle callback queries (inline keyboard responses)
    if "callback_query" in update:
        handle_callback_query(update["callback_query"])
        return
    
    if "message" not in update:
        return
    
    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user = message.get("from", {}).get("first_name", "User")
    
    logger.info(f"📩 Message from {user} (chat {chat_id}): {text[:50] if text else '[document]'}...")
    
    # Handle commands
    if text == "/start":
        handle_start(chat_id)
    elif text == "/ping":
        handle_ping(chat_id)
    elif text == "/status":
        handle_status(chat_id)
    elif text == "/list":
        handle_list(chat_id)
    elif text.startswith("/summary"):
        args = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
        handle_summary(chat_id, args)
    elif text.startswith("/delete"):
        args = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
        handle_delete(chat_id, args)
    elif text.startswith("/search"):
        args = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
        handle_search(chat_id, args)
    elif text == "/purge":
        handle_purge(chat_id)
    elif text == "/help":
        handle_help(chat_id)
    elif message.get("document"):
        handle_document(chat_id, message["document"])
    elif text:
        send_message(chat_id, "⚠️ Unknown command. Use /help for available commands.")


def main():
    """Main bot execution - runs for POLL_DURATION seconds"""
    print("\n" + "=" * 60)
    print(f"{ELITE_BANNER}")
    print("=" * 60)
    print(f"📡 Bot Token: {TOKEN[:20]}...")
    print(f"☁️ Supabase: {SUPABASE_URL}")
    print(f"⏱️ Poll Duration: {POLL_DURATION} seconds")
    print(f"🎯 Mode: ELITE_UI")
    print("=" * 60 + "\n")
    
    # Step 1: Delete any existing webhook
    logger.info("🔧 Step 1: Deleting existing webhook...")
    if not delete_webhook():
        logger.warning("⚠️ Webhook deletion failed, continuing anyway...")
    
    # Step 2: Verify bot connection
    logger.info("🔧 Step 2: Verifying bot connection...")
    bot_info = get_bot_info()
    if not bot_info:
        logger.error("❌ Failed to connect to bot. Exiting.")
        return {"status": "error", "message": "Failed to connect to bot"}
    
    # Step 3: Register commands
    logger.info("🔧 Step 3: Registering ELITE_UI commands...")
    register_commands()
    
    # Step 4: Test Supabase latency
    logger.info("🔧 Step 4: Testing Supabase connection...")
    latency_ms, success, _ = test_supabase_latency()
    if success:
        logger.info(f"✅ Supabase connected ({latency_ms}ms)")
    else:
        logger.warning(f"⚠️ Supabase connection issue ({latency_ms}ms)")
    
    # Step 5: Poll for updates
    logger.info(f"🔧 Step 5: Starting polling for {POLL_DURATION} seconds...")
    
    start_time = time.time()
    messages_processed = 0
    
    while (time.time() - start_time) < POLL_DURATION:
        try:
            updates = get_updates(offset=last_update_id + 1 if last_update_id else None, timeout=5)
            
            for update in updates:
                process_update(update)
                messages_processed += 1
            
            # Small delay to prevent CPU overuse
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"❌ Error in polling loop: {e}")
            time.sleep(2)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("✅ Polling completed")
    print(f"   Duration: {elapsed:.1f} seconds")
    print(f"   Messages processed: {messages_processed}")
    print("=" * 60)
    
    return {
        "status": "success",
        "duration": elapsed,
        "messages_processed": messages_processed
    }


if __name__ == "__main__":
    result = main()
    print(f"\n📊 Result: {result}")
