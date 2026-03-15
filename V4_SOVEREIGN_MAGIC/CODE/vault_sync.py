"""
V5 Apex Protocol - Vault Intelligence Injector
===============================================
Pulls the latest intelligence from the Supabase Sovereign Vault
and injects it into the Kilo and OpenCode memory banks so they
are automatically context-aware at every session start.

Commands:
  python vault_sync.py --sync-all       # Full sync from Supabase to all targets
  python vault_sync.py --kilo-sync      # Sync to Kilo memory bank only
  python vault_sync.py --opencode-sync  # Sync to OpenCode instructions only
  python vault_sync.py --list-documents # List all documents with IDs
  python vault_sync.py --purge <id>     # Purge specific document (or 'all')
  python vault_sync.py --download <id>  # Export document soul to MD_EXPORTS
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(r"D:\AI_FACTORY\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

KILO_MEMORY_PATH = r"D:\AI_FACTORY\.kilocode\rules\memory-bank\activeContext.md"
OPENCODE_CONTEXT_PATH = r"D:\AI_FACTORY\opencode.json"

# ============================================================================
# SUPABASE OPERATIONS
# ============================================================================

from supabase import create_client, Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def query_supabase_sdk(table: str, select: str = "*", eq: dict = None, order: str = None, limit: int = None) -> list:
    """Query Supabase using the Python SDK."""
    try:
        query = supabase.table(table).select(select)
        if eq:
            for key, val in eq.items():
                query = query.eq(key, val)
        if order:
            # Format: "id.desc" -> col="id", desc=True
            col, direction = order.split('.')
            query = query.order(col, desc=(direction == 'desc'))
        if limit:
            query = query.limit(limit)
        
        res = query.execute()
        return res.data or []
    except Exception as e:
        print(f"  ❌ Supabase query failed: {e}")
        return []

def delete_from_supabase_sdk(table: str, eq: dict) -> bool:
    """Delete from Supabase using the Python SDK."""
    try:
        query = supabase.table(table).delete()
        for key, val in eq.items():
            query = query.eq(key, val)
        res = query.execute()
        return True
    except Exception as e:
        print(f"  ❌ Supabase delete failed: {e}")
        return False

# ============================================================================
# DOCUMENT OPERATIONS
# ============================================================================

def get_vault_documents() -> list:
    """Fetch all documents from Supabase with IDs and metadata."""
    print("🔄 Fetching documents from Sovereign Vault...")
    
    rows = query_supabase_sdk("v4_vault", select="id,filename", order="id.desc")
    
    if not rows:
        print("  ⚠️  No documents found in vault.")
        return []
    
    # Group by filename to get unique documents
    documents = {}
    for row in rows:
        fname = row.get('filename', 'Unknown')
        if fname not in documents:
            documents[fname] = {
                'id': row.get('id'),
                'filename': fname,
                'created_at': row.get('created_at', 'Unknown'),
                'chunk_count': 1
            }
        else:
            documents[fname]['chunk_count'] += 1
    
    doc_list = list(documents.values())
    print(f"  ✅ Found {len(doc_list)} unique documents ({len(rows)} total chunks)")
    return doc_list

def list_documents(interactive: bool = False) -> str:
    """List all documents and optionally return a selected ID."""
    documents = get_vault_documents()
    
    if not documents:
        print("\n  📭 Vault is empty. No documents to display.")
        return None
    
    print("\n" + "=" * 60)
    print("  📁 DOCUMENTS IN SOVEREIGN VAULT")
    print("=" * 60)
    print(f"  {'#':<4} {'ID':<6} {'Filename':<35} {'Chunks':<8}")
    print("-" * 60)
    
    doc_map = {}
    for i, doc in enumerate(documents, 1):
        doc_map[str(i)] = doc['id']
        print(f"  {i:<4} {doc['id']:<6} {doc['filename'][:33]:<35} {doc['chunk_count']:<8}")
    
    print("=" * 60)
    print(f"  Total: {len(documents)} documents")
    
    if interactive:
        choice = input("\n👉 Enter Number (#), ID, or 'all' to purge (Enter to cancel): ").strip()
        if not choice:
            return None
        if choice.lower() == 'all':
            return 'all'
        return doc_map.get(choice, choice)
    
    return None

def purge_document(doc_id: str) -> dict:
    """
    Remove specific document from ALL locations.
    Returns dict with purge results for each location.
    """
    results = {
        'supabase': False,
        'kilo': False,
        'opencode': False,
        'graph': False
    }
    
    print(f"\n🔥 PURGING DOCUMENT: {doc_id}")
    print("=" * 50)
    
    # 1. Get document info first
    if doc_id.lower() == 'all':
        print("  ⚠️  PURGING ALL DOCUMENTS FROM VAULT...")
    else:
        # Try to find by ID
        rows = query_supabase_sdk("v4_vault", select="id,filename", eq={"id": doc_id})
        if not rows:
            # Try by filename
            rows = query_supabase_sdk("v4_vault", select="id,filename", eq={"filename": doc_id})
        
        if not rows:
            print(f"  ❌ Document not found: {doc_id}")
            return results
        
        filename = rows[0].get('filename', '')
        actual_id = rows[0].get('id')
        print(f"  📄 Found document: {filename} (ID: {actual_id})")
    
    # 2. Purge from Supabase v4_vault
    print("  🗑️  Purging from Supabase v4_vault...")
    if doc_id.lower() == 'all':
        # Need to be careful with 'all', usually sdk handles with empty eq or specific logic
        # For safety, let's assume specific purges for now or implement 'all' via truncate if available
        # But SDK delete requires a filter.
        print("     ❌ 'all' purge not implemented via SDK for safety. Use specific IDs.")
        results['supabase'] = False
    else:
        results['supabase'] = delete_from_supabase_sdk("v4_vault", {"filename": filename})
    
    if results['supabase']:
        print("     ✅ Supabase vault purged")
    else:
        print("     ⚠️  Supabase purge may have failed")
    
    # 3. Purge from Supabase v4_graph (related entities)
    print("  🗑️  Purging from Supabase v4_graph...")
    if doc_id.lower() != 'all':
        results['graph'] = delete_from_supabase_sdk("v4_graph", {"doc_id": actual_id})
    
    if results['graph']:
        print("     ✅ Supabase graph purged")
    
    # 4. Purge from Kilo memory bank
    print("  🗑️  Purging from Kilo memory bank...")
    results['kilo'] = purge_from_kilo(doc_id)
    if results['kilo']:
        print("     ✅ Kilo memory purged")
    
    # 5. Purge from OpenCode
    print("  🗑️  Purging from OpenCode context...")
    results['opencode'] = purge_from_opencode(doc_id)
    if results['opencode']:
        print("     ✅ OpenCode context purged")
    
    return results

def purge_from_kilo(doc_id: str) -> bool:
    """Remove document references from Kilo memory bank."""
    try:
        if not os.path.exists(KILO_MEMORY_PATH):
            return True  # Nothing to purge
        
        with open(KILO_MEMORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove the entire vault block if it exists
        if "## 🧠 SOVEREIGN VAULT INDEX" in content:
            content = content.split("\n\n---\n## 🧠 SOVEREIGN VAULT INDEX")[0]
            
            with open(KILO_MEMORY_PATH, "w", encoding="utf-8") as f:
                f.write(content)
        
        return True
    except Exception as e:
        print(f"     ❌ Kilo purge error: {e}")
        return False

def purge_from_opencode(doc_id: str) -> bool:
    """Remove document references from OpenCode instructions."""
    try:
        if not os.path.exists(OPENCODE_CONTEXT_PATH):
            return True  # Nothing to purge
        
        with open(OPENCODE_CONTEXT_PATH, "r", encoding="utf-8") as f:
            oc_config = json.load(f)
        
        existing = oc_config.get("instructions", "")
        
        # Remove the vault block
        if "SOVEREIGN VAULT INDEX" in existing:
            existing = existing.split("\n\n---\n## 🧠 SOVEREIGN VAULT INDEX")[0]
            oc_config["instructions"] = existing
            
            with open(OPENCODE_CONTEXT_PATH, "w", encoding="utf-8") as f:
                json.dump(oc_config, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"     ❌ OpenCode purge error: {e}")
        return False

def download_document(doc_identifier: str) -> bool:
    """Download full Markdown content for a document to MD_EXPORTS."""
    print(f"\n📥 EXPORTING DOCUMENT SOUL: {doc_identifier}")
    print("=" * 50)
    
    # 1. Resolve Document
    rows = query_supabase_sdk("v4_vault", select="id,filename", eq={"id": doc_identifier})
    if not rows:
        rows = query_supabase_sdk("v4_vault", select="id,filename", eq={"filename": doc_identifier})
    
    if not rows:
        print(f"  ❌ Document not found in vault: {doc_identifier}")
        return False
        
    actual_filename = rows[0].get('filename', 'unknown.md')
    if not actual_filename.endswith('.md'):
        actual_filename += '.md'
        
    # 2. Fetch all chunks in order
    print(f"  🛰️  Retrieving neural fragments from cloud...")
    fragments = query_supabase_sdk("v4_vault", select="content", eq={"filename": rows[0]['filename']}, order="id.asc")
    
    if not fragments:
        print("  ❌ No content fragments found.")
        return False
        
    full_content = "\n".join([f.get('content', '') for f in fragments])
    
    # 3. Save locally
    export_dir = r"D:\V4_SOVEREIGN_MAGIC\MD_EXPORTS"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    export_path = os.path.join(export_dir, actual_filename)
    
    try:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"  ✅ EXPORT SUCCESSFUL!")
        print(f"  📍 Location: {export_path}")
        return True
    except Exception as e:
        print(f"  ❌ Export failed: {e}")
        return False

# ============================================================================
# SYNC OPERATIONS
# ============================================================================

def fetch_vault_intelligence():
    """Pull lightweight index from Sovereign Vault."""
    print("🔄 Pulling intelligence index from Sovereign Vault...")
    
    # 1. Get all documents and metadata
    rows = query_supabase_sdk("v4_vault", select="id, filename, metadata", order="id.desc")
    
    # Group by filename for unique document index
    documents = {}
    for r in (rows or []):
        fname = r.get('filename', 'Unknown')
        if fname not in documents:
            documents[fname] = {
                'id': r.get('id'),
                'filename': fname,
                'fragments': 1,
                'source': (r.get('metadata') or {}).get('source', 'unknown')
            }
        else:
            documents[fname]['fragments'] += 1
    
    # 2. Get Neural Map Centrality (Top connections)
    graph_rows = query_supabase_sdk("v4_graph", select="subject", limit=1000)
    counts = {}
    for r in (graph_rows or []):
        s = r.get('subject', '')
        counts[s] = counts.get(s, 0) + 1
    top_entities = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:15]
    
    return list(documents.values()), top_entities

def generate_context_block(doc_list: list, top_entities: list) -> str:
    """Generate lightweight index context block."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"\n\n---\n## 🧠 SOVEREIGN VAULT INDEX (Auto-Synced: {now})\n",
        f"> **VECTOR GAP CLOSED**: Souls are stored in Cloud Nodes. Agent will use direct retrieval for queries.\n",
        f"\n### 📁 Active Document Inventory ({len(doc_list)} total)\n",
    ]
    
    if not doc_list:
        lines.append("- *Vault is currently empty.*\n")
    else:
        for d in doc_list:
            lines.append(f"- `{d['filename']}` (ID: `{d['id'][:8]}`) — Fragments: {d['fragments']} | Source: {d['source']}\n")
    
    if top_entities:
        lines.append(f"\n### 🕸️ Neural Map Summary (Knowledge Nodes)\n")
        nodes = [f"**{e}**" for e, c in top_entities]
        lines.append(f"> {', '.join(nodes)}\n")
    
    lines.append("\n### 🛠️ AGENT COMMANDS:\n")
    lines.append("> To retrieve project-specific ground truth, run:\n")
    lines.append(f"> `python CODE\\vault_query.py \"[user question]\"`\n")
    lines.append("\n---\n")
    
    return "".join(lines)

def sync_kilo(context_block: str = None) -> bool:
    """Sync to Kilo memory bank."""
    print("🔄 Syncing to Kilo memory bank...")
    
    if context_block is None:
        doc_list, top_entities = fetch_vault_intelligence()
        context_block = generate_context_block(doc_list, top_entities)
    
    try:
        with open(KILO_MEMORY_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove old vault block if it exists
        if "## 🧠 SOVEREIGN VAULT INDEX" in content:
            content = content.split("\n\n---\n## 🧠 SOVEREIGN VAULT INDEX")[0]
        
        content += context_block
        with open(KILO_MEMORY_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✅ Kilo memory bank updated!")
        return True
    except Exception as e:
        print(f"  ❌ Kilo sync failed: {e}")
        return False

def sync_opencode(context_block: str = None) -> bool:
    """Sync to OpenCode instructions field."""
    print("🔄 Syncing to OpenCode context...")
    
    if not os.path.exists(OPENCODE_CONTEXT_PATH):
        print("  ⚠️  opencode.json not found, skipping.")
        return False
    
    if context_block is None:
        doc_list, top_entities = fetch_vault_intelligence()
        context_block = generate_context_block(doc_list, top_entities)
    
    try:
        with open(OPENCODE_CONTEXT_PATH, "r", encoding="utf-8") as f:
            oc_config = json.load(f)
        
        # Inject into the instructions field or create one
        existing = oc_config.get("instructions", "")
        
        # Remove old vault block
        if "SOVEREIGN VAULT INDEX" in existing:
            existing = existing.split("\n\n---\n## 🧠 SOVEREIGN VAULT INDEX")[0]
        
        oc_config["instructions"] = existing + context_block
        
        with open(OPENCODE_CONTEXT_PATH, "w", encoding="utf-8") as f:
            json.dump(oc_config, f, indent=2, ensure_ascii=False)
        print("  ✅ OpenCode context updated!")
        return True
    except Exception as e:
        print(f"  ❌ OpenCode sync failed: {e}")
        return False

def sync_all() -> dict:
    """Full sync from Supabase to all targets."""
    print("=" * 50)
    print("🦾 V5 APEX - VAULT INTELLIGENCE SYNC")
    print("=" * 50)
    
    results = {
        'filenames': [],
        'souls': 0,
        'entities': 0,
        'kilo': False,
        'opencode': False
    }
    
    # 1. Fetch Cloud Index
    doc_list, top_entities = fetch_vault_intelligence()
    context_block = generate_context_block(doc_list, top_entities)
    
    results['filenames'] = [d['filename'] for d in doc_list]
    results['souls'] = len(doc_list)
    results['entities'] = len(top_entities)
    
    # 2. Sync to local memory banks
    results['kilo'] = sync_kilo(context_block)
    results['opencode'] = sync_opencode(context_block)
    
    # 3. Automated Local Export (v1.2 Feature)
    print("\n🔄 Checking for local MD exports...")
    export_dir = r"D:\V4_SOVEREIGN_MAGIC\MD_EXPORTS"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    for doc in doc_list:
        fname = doc['filename']
        if not fname.endswith('.md'): fname += '.md'
        local_path = os.path.join(export_dir, fname)
        
        if not os.path.exists(local_path):
            print(f"  ✨ Autoloading new intelligence: {doc['filename']}")
            download_document(doc['id'])
    
    return results

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="V5 Apex Vault Sync - Sync intelligence from Supabase to Kilo & OpenCode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vault_sync.py --list-documents List all documents with IDs
  python vault_sync.py --purge <id>     Purge specific document (or "all")
  python vault_sync.py --download <id>  Export document soul to MD_EXPORTS
        """
    )
    
    parser.add_argument('--sync-all', action='store_true', help='Full sync from Supabase to all targets')
    parser.add_argument('--kilo-sync', action='store_true', help='Sync to Kilo memory bank only')
    parser.add_argument('--opencode-sync', action='store_true', help='Sync to OpenCode instructions only')
    parser.add_argument('--list-documents', action='store_true', help='List all documents with IDs')
    parser.add_argument('--purge', type=str, nargs='?', const='all', help='Purge document by ID or filename (or "all")')
    parser.add_argument('--download', type=str, nargs='?', const='select', help='Export document soul to MD_EXPORTS')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.list_documents:
        list_documents()
    elif args.download is not None:
        target = args.download
        if target == 'select' or not target:
            target = list_documents(interactive=True)
            
        if target:
            download_document(target)
        else:
            print("🛑 Download cancelled.")
    elif args.purge is not None:
        target = args.purge
        if target == 'all' or not target:
            # If purge called without ID, show interactive list
            target = list_documents(interactive=True)
            
        if target:
            results = purge_document(target)
            print("\n" + "=" * 50)
            print("🔥 PURGE RESULTS:")
            print(f"   Supabase Vault: {'✅' if results['supabase'] else '❌'}")
            print(f"   Supabase Graph: {'✅' if results['graph'] else '❌'}")
            print(f"   Kilo Memory:    {'✅' if results['kilo'] else '❌'}")
            print(f"   OpenCode:       {'✅' if results['opencode'] else '❌'}")
            print("=" * 50)
            if all(results.values()):
                print("✅ PURGE COMPLETE. No ghost memory remains.")
            else:
                print("⚠️  Some locations may still contain traces.")
        else:
            print("🛑 Purge cancelled.")
    elif args.kilo_sync:
        sync_kilo()
    elif args.opencode_sync:
        sync_opencode()
    elif args.sync_all:
        results = sync_all()
        print()
        print("=" * 50)
        print(f"✅ SYNC COMPLETE!")
        print(f"   📁 {len(results['filenames'])} docs | 🧠 {results['souls']} souls | 📈 {results['entities']} top nodes")
        print("   Kilo & OpenCode are now fully vault-aware!")
        print("=" * 50)
    else:
        # Default: run full sync (backward compatibility)
        results = sync_all()
        print()
        print("=" * 50)
        print(f"✅ SYNC COMPLETE!")
        print(f"   📁 {len(results['filenames'])} docs | 🧠 {results['souls']} souls | 📈 {results['entities']} top nodes")
        print("   Kilo & OpenCode are now fully vault-aware!")
        print("=" * 50)

if __name__ == "__main__":
    main()
