import os
import time
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import AIMessage

# Load environment variables
load_dotenv()

# === Configuration ===
BOT_NAME = os.getenv("BOT_NAME", "BitBot")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === LLM Setup ===
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name=LLM_MODEL
)

# === Hardcoded price data ===
price_data = {
    "bitcoin": {"price": 43500.0, "change": 1.2},
    "ethereum": {"price": 3250.0, "change": -0.5},
    "cardano": {"price": 0.62, "change": 0.8},
}

# === Helpers ===
def format_price(coin: str) -> str:
    data = price_data.get(coin)
    if not data:
        return f"Sorry, I don't have data for that cryptocurrency. Try asking about Bitcoin, Ethereum, or Cardano."
    change_str = f"{data['change']:+.2f}%"
    return f"The current price of {coin.title()} is ${data['price']:,.2f} ({change_str} in 24h)."

def handle_price_query(query: str) -> str:
    query = query.lower()
    for coin in price_data:
        if coin in query:
            return format_price(coin)
    return "Sorry, I don't have data for that cryptocurrency. Try asking about Bitcoin, Ethereum, or Cardano."

def build_prompt(user_input: str) -> str:
    return f"You are a helpful cryptocurrency assistant.\nUser: {user_input}\nAssistant:"

def get_llm_response(prompt: str) -> str:
    try:
        result = llm.invoke(prompt)
        if isinstance(result, AIMessage):
            return result.content.strip()
        return str(result).strip()
    except Exception as e:
        logger.error(f"Groq LLM error: {e}")
        return "I'm having trouble thinking right now. Try again shortly."

# === Main Chat Loop ===
def main():
    print("Welcome to BitBot! Your cryptocurrency assistant.")
    print("Type 'help' for available commands, 'clear' to reset screen, or 'exit' to quit.\n")

    while True:
        try:
            user_input = input(f"{BOT_NAME} > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            elif user_input.lower() in ["help", "commands"]:
                print("\nYou can ask questions like:")
                print("- What is Bitcoin?")
                print("- How much is Ethereum?")
                print("- What's the price of Cardano?\n")
                continue
            elif user_input.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            elif any(phrase in user_input.lower() for phrase in ["price", "how much", "value"]):
                print(handle_price_query(user_input))
            else:
                prompt = build_prompt(user_input)
                response = get_llm_response(prompt)
                print(f"{BOT_NAME}: {response}")

        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            print("Something went wrong. Please try again.")

if __name__ == "__main__":
    main()
