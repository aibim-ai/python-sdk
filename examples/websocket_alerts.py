"""Listen to real-time security alerts via WebSocket."""
import asyncio
from aibim import AlertsWebSocket

async def main():
    async with AlertsWebSocket(
        base_url="https://proxy.aibim.ai",
        api_key="aibim-your-api-key"
    ) as ws:
        print("Connected! Listening for alerts...")
        async for alert in ws.listen():
            print(f"[{alert.get('risk_level', 'unknown')}] {alert.get('action', 'N/A')}")
            print(f"  Score: {alert.get('risk_score')}")
            print(f"  Model: {alert.get('model')}")
            print(f"  Rules: {alert.get('matched_rules')}")
            print()

asyncio.run(main())
