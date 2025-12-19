import urllib.request
import json
import time

def test_server():
    print("STARTING TEST SERVER CONNECTIVITY...")
    try:
        url = "http://localhost:8000/api/v1/admin/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            print(f"Health Check Status: {response.getcode()}")
            print(response.read().decode('utf-8'))
            
        print("\nTesting Chat Endpoint...")
        chat_url = "http://localhost:8000/api/v1/chat"
        data = {
            "user_id": "test_user",
            "message": "Hello, is this working?",
            "session_id": "test_session"
        }
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(chat_url, data=json_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            print(f"Chat Response Status: {response.getcode()}")
            print(response.read().decode('utf-8'))
            
    except Exception as e:
        print(f"FAILED TO CONNECT: {e}")
        print("Please ensure the server is running on localhost:8000")

if __name__ == "__main__":
    test_server()
