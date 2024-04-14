# Prerequisites
- Python 3.10 or later

# Installation
1. If you have poetry installed, run the following command:
```bash
poetry update
```

2. If not, run the following command:
```bash
pip install -r requirements.txt
```

# Run Server
- run following command:
```bash
make gunicorn-v1
```

# Run Locust(Stress Test)
- run following command:
```bash
make locust
```

# Try Streaming API
- run following code:
```python
import httpx
import asyncio


async def fetch_streaming_response():
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://127.0.0.1:8000/v1/agent/clova/stream") as response:
            async for chunk in response.aiter_text():
                for character in chunk:
                    print(character, end="", flush=True)


asyncio.run(fetch_streaming_response())

```