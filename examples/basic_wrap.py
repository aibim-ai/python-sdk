"""Basic example: Wrap an OpenAI client to route through AIBIM proxy."""
from openai import OpenAI
from aibim import wrap, AibimBlockedError

# Create your OpenAI client as usual
client = OpenAI(api_key="sk-your-openai-key")

# One line to add AIBIM security
wrap(client,
    aibim_url="https://proxy.aibim.ai",
    aibim_api_key="aibim-your-api-key"
)

# Use exactly as before -- all traffic is now secured
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is machine learning?"}
        ]
    )
    print(response.choices[0].message.content)
except AibimBlockedError as e:
    print(f"Request blocked! Risk score: {e.risk_score}")
    print(f"Matched rules: {e.matched_rules}")
