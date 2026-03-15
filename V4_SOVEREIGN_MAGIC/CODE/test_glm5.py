import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(r"d:\AI_FACTORY\.env")

def test_glm5():
    api_key = os.environ.get("MODAL_API_KEY")
    if not api_key:
        api_key = "modalresearch_NbBfy7r1X1kmx3HSC8oiDo48BYVmDC1lfjKDrvnRZjM" # From opencode.json
    
    base_url = os.environ.get("GLM_BASE_URL", "https://api.us-west-2.modal.direct/v1")
    model_name = os.environ.get("GLM_MODEL", "zai-org/GLM-5-FP8")

    print(f"🚀 Testing GLM-5 via {base_url}...")
    client = OpenAI(api_key=api_key, base_url=base_url)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Analyze the significance of the year 2030 in global strategy in one sentence."}],
            temperature=0.3,
            timeout=30.0
        )
        print(f"✅ SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ FAILURE: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_glm5()
