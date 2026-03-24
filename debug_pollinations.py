import requests

endpoints = [
    "https://pollinations.ai/p/apple?width=100",
    "https://gen.pollinations.ai/image/apple",
    "https://image.pollinations.ai/prompt/apple",
    "https://pollinations.ai/prompt/apple",
    "https://pollinations.ai/apple"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "image/*"
}

for url in endpoints:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Length: {len(response.content)}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")
