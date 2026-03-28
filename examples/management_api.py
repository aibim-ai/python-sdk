"""Manage your AIBIM instance programmatically."""
import asyncio
from aibim import AibimClient

async def main():
    async with AibimClient(
        base_url="https://proxy.aibim.ai",
        api_key="aibim-your-api-key"
    ) as client:
        # Tenant info
        tenant = await client.tenant.me()
        print(f"Tenant: {tenant}")

        # Usage stats
        usage = await client.tenant.get_usage()
        print(f"Usage: {usage}")

        # List detection rules
        rules = await client.rules.list()
        print(f"Rules: {len(rules)} loaded")

        # Get real-time stats
        stats = await client.data.realtime_stats()
        print(f"Stats: {stats}")

        # List alerts
        alerts = await client.alerts.list()
        print(f"Alerts: {len(alerts)}")

asyncio.run(main())
