import requests
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

# === Configuration ===
BOT_NAME = os.getenv("BOT_NAME", "BitBot")
BOT_TONE = os.getenv("BOT_TONE", "friendly")
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
MODEL_ID = os.getenv("MODEL_ID", "google/google/flan-t5-large")

# === Hugging Face LLM ===
# Get your Hugging Face API key from: https://huggingface.co/settings/tokens
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HF_TOKEN:
    raise ValueError("Please set HUGGINGFACE_TOKEN in your .env file")

llm_client = InferenceClient(MODEL_ID, token=HF_TOKEN)

def get_llm_response(prompt: str) -> str:
    try:
        response = llm_client.text_generation(prompt, max_new_tokens=100, stream=False, details=True)
        print("LLM raw output:", response)
        return response.generated_text.strip()
    except Exception as e:
        print(f"Error from LLM: {e}")
        return "I'm having trouble thinking right now. Try again shortly."

# === Static knowledge base ===
crypto_db = {
    "Bitcoin": {"price_trend": "rising", "market_cap": "high", "energy_use": "high", "sustainability_score": 3},
    "Ethereum": {"price_trend": "stable", "market_cap": "high", "energy_use": "medium", "sustainability_score": 6},
    "Cardano": {"price_trend": "rising", "market_cap": "medium", "energy_use": "low", "sustainability_score": 8}
}

# === CoinGecko API ===
def get_crypto_data(coin_id: str) -> Dict:
    try:
        response = requests.get(f"{COINGECKO_API_URL}/simple/price",
                                params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"})
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

def format_price(price: float) -> str:
    return f"${price:,.2f}"

# === Chat History Buffer ===
chat_history = []

def build_prompt(user_input: str) -> str:
    return f"Q: {user_input}\nA:"

def respond_to_query(user_query: str) -> str:
    user_query = user_query.lower()
    btc_data = get_crypto_data("bitcoin")
    eth_data = get_crypto_data("ethereum")

    price_info = ""
    if btc_data and eth_data:
        btc_price = btc_data.get("bitcoin", {}).get("usd", 0)
        eth_price = eth_data.get("ethereum", {}).get("usd", 0)
        price_info = f"\nCurrent prices:\nBitcoin: {format_price(btc_price)}\nEthereum: {format_price(eth_price)}"

    if "sustainable" in user_query:
        recommend = max(crypto_db, key=lambda x: crypto_db[x]["sustainability_score"])
        return f"{recommend} 🌱 is one of the most eco-friendly coins!{price_info}"

    elif "trending" in user_query or "up" in user_query:
        trending = [coin for coin in crypto_db if crypto_db[coin]["price_trend"] == "rising"]
        return f"These coins are trending up 📈: {', '.join(trending)}{price_info}"

    elif "profitable" in user_query or "invest" in user_query:
        profitable = [coin for coin in crypto_db if crypto_db[coin]["price_trend"] == "rising" and crypto_db[coin]["market_cap"] == "high"]
        return f"{profitable[0]} 🚀 looks promising for investment!{price_info}" if profitable else "No hot picks at the moment. 🧐"

    # Else: use LLM
    prompt = build_prompt(user_query)
    response = get_llm_response(prompt)
    chat_history.append(f"User: {user_query}\nAssistant: {response}")
    return f"{response}{price_info}"

# === CLI Main Loop ===
def main():
    print(f"{BOT_NAME}: Hey! I'm {BOT_NAME}, your crypto sidekick. Ask me anything about the market or sustainability. Type 'exit' to leave.")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"{BOT_NAME}: Catch you later! 👋")
            break
        else:
            response = respond_to_query(user_input)
            print(f"{BOT_NAME}: {response}")

if __name__ == "__main__":
    main()
