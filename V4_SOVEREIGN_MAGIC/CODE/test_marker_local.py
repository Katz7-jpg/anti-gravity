import os
import modal

def test_marker_remote():
    """Trigger the PredatorShredder on Modal to test Marker OCR and Embeddings."""
    predator = modal.Cls.from_name("v4-predator-shredder", "PredatorShredder")
    
    pdf_path = r"d:\V4_SOVEREIGN_MAGIC\DROP_ZONE\2030.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ ERROR: {pdf_path} not found.")
        return

    print(f"🚀 Testing Marker OCR on Modal for {pdf_path}...")
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    try:
        # We use shred_and_tag as defined in V4_CLOUD_PREDATOR.py
        # Note: This requires the app to be deployed already.
        # If not, we might need to use modal.Runner() or similar.
        result = predator().shred_and_tag.remote(pdf_bytes, "2030.pdf")
        
        if "⚠️ DUPLICATE DETECTED" in result:
             print(f"ℹ️ {result}")
        else:
            print(f"✅ SUCCESS: Markdown content generated ({len(result)} chars)")
            print(f"Preview: {result[:500]}...")
            
    except Exception as e:
        print(f"❌ FAILURE: {e}")

if __name__ == "__main__":
    test_marker_remote()
