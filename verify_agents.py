import urllib.request
import json
import time

def send_chat(message):
    url = "http://localhost:8000/api/v1/chat"
    data = {
        "user_id": "verify_user",
        "message": message,
        "session_id": "verify_session"
    }
    json_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\nQUERY: {message}")
            print(f"RESPONSE: {result['response']}")
            print(f"AGENT USED: {result.get('classification', {}).get('primary_agent', 'Unknown')}")
            return result
    except Exception as e:
        print(f"Error sending message '{message}': {e}")
        return None

def verify_analytics():
    url = "http://localhost:8000/api/v1/analytics/concerns"
    try:
        with urllib.request.urlopen(url) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"\nANALYTICS (Top Concerns): {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error fetching analytics: {e}")

if __name__ == "__main__":
    print("=== VERIFYING NUA AGENTIC SYSTEM ===")
    
    # 1. Test Safety Agent (High Severity)
    send_chat("I have severe cramps and I fainted.")
    
    # 2. Test Product Agent
    send_chat("I need pads for heavy flow night usage.")
    
    # 3. Test Education Agent
    send_chat("Is it normal to have brown blood?")
    
    # 4. Test Reassurance Agent
    send_chat("I feel so anxious about leaking at work.")
    
    # 5. Verify Analytics recorded these
    time.sleep(1) # Give DB a moment
    verify_analytics()
