"""Wrap an Anthropic client to route through AIBIM proxy."""
from anthropic import Anthropic
from aibim import wrap, unwrap, AibimBlockedError

# Create your Anthropic client as usual
client = Anthropic(api_key="sk-ant-your-anthropic-key")

# One line to add AIBIM security
wrap(client,
    aibim_url="https://proxy.aibim.ai",
    aibim_api_key="aibim-your-api-key"
)

# Use exactly as before -- all traffic is now secured
try:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
    )
    print(message.content[0].text)
except AibimBlockedError as e:
    print(f"Request blocked! Risk score: {e.risk_score}")
    print(f"Matched rules: {e.matched_rules}")
finally:
    # Restore original client if needed
    unwrap(client)
