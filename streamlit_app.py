import os
import time
import random
import logging
import streamlit as st
import pandas as pd
import altair as alt
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
@st.cache_resource
def load_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL
    )

# === Hardcoded price data ===
price_data = {
    "bitcoin": {"price": 43500.0, "change": 1.2, "symbol": "₿", "color": "#f7931a"},
    "ethereum": {"price": 3250.0, "change": -0.5, "symbol": "Ξ", "color": "#627eea"},
    "cardano": {"price": 0.62, "change": 0.8, "symbol": "₳", "color": "#0033ad"},
}

# Generate synthetic price history data for charts
def generate_price_history(coin):
    current_price = price_data[coin]["price"]
    # Generate 30 days of synthetic data with some randomness around the current price
    volatility = 0.02 if coin == "bitcoin" else 0.03 if coin == "ethereum" else 0.04
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
    prices = []
    price = current_price * (1 - price_data[coin]["change"]/100 * 30)  # Start from approximately 30 days ago
    
    for _ in range(30):
        change = random.normalvariate(0, volatility)
        price = price * (1 + change)
        prices.append(price)
    
    # Ensure the last price matches the current price
    prices[-1] = current_price
    
    return pd.DataFrame({
        "date": dates,
        "price": prices
    })

# === Helpers ===
def format_price(coin: str, include_chart=False) -> str:
    data = price_data.get(coin)
    if not data:
        return f"Sorry, I don't have data for that cryptocurrency. Try asking about Bitcoin, Ethereum, or Cardano."
    
    # Format with symbols that don't require HTML
    change_str = f"{data['change']:+.2f}%"
    if data['change'] > 0:
        change_formatted = f"🟢 {change_str}"
    else:
        change_formatted = f"🔴 {change_str}"
    
    symbol = data['symbol']
    result = f"The current price of {coin.title()} {symbol} is ${data['price']:,.2f} ({change_formatted} in 24h)."
    
    if include_chart:
        result += f"\n\n*Generating price chart for {coin.title()}...*"
    
    return result

def create_price_chart(coin):
    """Creates an interactive price chart for the specified cryptocurrency"""
    if coin not in price_data:
        return None
    
    # Get price history data
    df = generate_price_history(coin)
    
    # Format the data for better display
    df['date_str'] = df['date'].dt.strftime('%b %d')
    
    # Create the chart
    color = price_data[coin]['color']
    symbol = price_data[coin]['symbol']
    
    # Create a line chart with area
    chart = alt.Chart(df).mark_area(opacity=0.3, color=color).encode(
        x=alt.X('date:T', title='Date', axis=alt.Axis(format='%b %d', labelAngle=0)),
        y=alt.Y('price:Q', title='Price (USD)', scale=alt.Scale(zero=False))
    ).properties(
        title=f'{coin.title()} {symbol} Price (30 Days)',
        width='container',
        height=250
    )
    
    # Add a line on top of the area
    line = alt.Chart(df).mark_line(color=color, size=2).encode(
        x='date:T',
        y='price:Q'
    )
    
    # Add the last point with tooltip
    point = alt.Chart(df.iloc[[-1]]).mark_circle(size=80, color=color, opacity=0.7).encode(
        x='date:T',
        y='price:Q',
        tooltip=['date_str', alt.Tooltip('price:Q', format='$,.2f')]
    )
    
    # Combine the visualizations
    return (chart + line + point).configure_view(
        strokeWidth=0
    ).configure_axis(
        grid=False
    ).configure_title(
        fontSize=16,
        color='#e0e0e0'
    )

def handle_price_query(query: str) -> str:
    query = query.lower()
    for coin in price_data:
        if coin in query:
            return format_price(coin)
    return "Sorry, I don't have data for that cryptocurrency. Try asking about Bitcoin, Ethereum, or Cardano."

def build_prompt(user_input: str) -> str:
    # Create a more detailed system prompt for better cryptocurrency explanations
    system_message = f"""You are {BOT_NAME}, an expert cryptocurrency assistant with deep knowledge of blockchain technology.
    
    When explaining cryptocurrencies:
    - Provide detailed, informative explanations about blockchain concepts
    - Include information about the technology, history, and use cases
    - For Bitcoin questions, explain it's the first cryptocurrency, created by Satoshi Nakamoto in 2009
    - For Ethereum questions, explain it's a decentralized platform for smart contracts and applications
    - For Cardano questions, explain it's a proof-of-stake blockchain platform focused on sustainability
    - Format your response with bullet points for key features
    - Always be factual, educational and helpful
    
    Current crypto prices:
    - Bitcoin: ${price_data['bitcoin']['price']:,.2f} ({price_data['bitcoin']['change']:+.2f}%)
    - Ethereum: ${price_data['ethereum']['price']:,.2f} ({price_data['ethereum']['change']:+.2f}%)
    - Cardano: ${price_data['cardano']['price']:,.2f} ({price_data['cardano']['change']:+.2f}%)
    """
    
    return system_message + f"\n\nUser: {user_input}\nAssistant:"

def get_llm_response(prompt: str) -> str:
    try:
        llm = load_llm()
        result = llm.invoke(prompt)
        if isinstance(result, AIMessage):
            return result.content.strip()
        return str(result).strip()
    except Exception as e:
        logger.error(f"Groq LLM error: {e}")
        return "I'm having trouble thinking right now. Try again shortly."

def process_message(user_input: str):
    if not user_input:
        return None
    
    # Check for command shortcuts
    if user_input.lower() in ["help", "commands"]:
        return {
            "role": "assistant",
            "content": """You can ask questions like:
- What is Bitcoin?
- How much is Ethereum?
- What's the price of Cardano?
- Show me Bitcoin chart

Or ask general questions about cryptocurrencies and blockchain technology."""
        }
    
    # Check for chart requests
    elif any(word in user_input.lower() for word in ["chart", "graph", "trend", "history"]) and any(coin in user_input.lower() for coin in price_data):
        # Find which coin is being requested
        requested_coin = next((coin for coin in price_data if coin in user_input.lower()), None)
        if requested_coin:
            return {
                "role": "assistant",
                "content": format_price(requested_coin, include_chart=True),
                "extra_data": {"show_chart": True, "coin": requested_coin}
            }
        
    # Check for price queries
    elif any(phrase in user_input.lower() for phrase in ["price", "how much", "value"]) and any(coin in user_input.lower() for coin in price_data):
        # Find which coin is being requested
        requested_coin = next((coin for coin in price_data if coin in user_input.lower()), None)
        if requested_coin:
            return {
                "role": "assistant",
                "content": format_price(requested_coin)
            }
        else:
            return {
                "role": "assistant", 
                "content": handle_price_query(user_input)
            }
    
    # For "What is" questions about specific cryptocurrencies
    elif "what is" in user_input.lower() or "what's" in user_input.lower() or "explain" in user_input.lower():
        # Send to LLM for a detailed explanation
        prompt = build_prompt(user_input)
        response = get_llm_response(prompt)
        return {
            "role": "assistant",
            "content": response
        }
    
    # General LLM query
    else:
        prompt = build_prompt(user_input)
        response = get_llm_response(prompt)
        return {
            "role": "assistant",
            "content": response
        }

# === Streamlit App ===
def main():
    # Set Streamlit page config for dark theme
    st.set_page_config(
        page_title=f"{BOT_NAME} - Crypto Assistant",
        page_icon="🪙",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS for dark theme with animations and enhanced crypto styling
    st.markdown("""
    <style>
        /* Dark theme with crypto styling and background pattern */
        .stApp {
            background-color: #0f1216;
            color: #e0e0e0;
            background-image: radial-gradient(circle at 10px 10px, #15182b 1px, transparent 0);
            background-size: 30px 30px;
        }
        
        /* Sidebar styling with gradient */
        .stSidebar {
            background: linear-gradient(to bottom, #121826, #0a0e14);
            border-right: 1px solid #2d3748;
        }
        
        /* Glowing accent for headings */
        h1, h2, h3 {
            color: #f7931a !important;
            text-shadow: 0 0 10px rgba(247, 147, 26, 0.3);
        }
        /* Card styling with hover effects and enhanced animations */
        .crypto-card {
            background-color: #1a202c;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            border: 1px solid #2d3748;
            position: relative;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }
        .crypto-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.5);
            border-color: #4a5568;
        }
        .crypto-card:hover .coin-symbol {
            animation-play-state: running;
        }
        .coin-symbol {
            font-size: 28px;
            margin-right: 15px;
            font-weight: bold;
            display: inline-block;
            animation: float 3s ease-in-out infinite;
            animation-play-state: paused;
        }
        .price {
            font-size: 18px;
            font-weight: bold;
            margin-top: 3px;
            transition: color 0.3s;
        }
        .crypto-card:hover .price {
            color: #f0f0f0;
        }
        .positive-change {
            color: #48bb78;
            font-weight: bold;
            transition: all 0.3s;
        }
        .negative-change {
            color: #f56565;
            font-weight: bold;
            transition: all 0.3s;
        }
        .crypto-card:hover .positive-change {
            color: #68d391;
        }
        .crypto-card:hover .negative-change {
            color: #fc8181;
        }
        
        /* Floating animation for crypto symbols */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        
        /* Subtle glow effect for cards on hover */
        .crypto-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.03) 50%, rgba(255,255,255,0) 100%);
            opacity: 0;
            transition: opacity 0.3s;
        }
        .crypto-card:hover::after {
            opacity: 1;
        }
        
        /* Input field */
        .stTextInput input {
            background-color: #2d3748;
            color: white;
            border: 1px solid #4a5568;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # App header with crypto styling - more compact layout
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://img.icons8.com/fluency/96/cryptocurrency.png", width=80)
    with col2:
        st.title(f"{BOT_NAME} 🪙")
        st.markdown("<p style='color: #a0aec0; margin-top: -15px; margin-bottom: 0px;'>Your intelligent cryptocurrency assistant powered by AI</p>", unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Welcome to {BOT_NAME}! I'm your crypto assistant. Ask me about Bitcoin, Ethereum, or Cardano prices, or any questions about cryptocurrencies."
        })
    
    # Cryptocurrency price display in sidebar with enhanced crypto-themed cards
    st.sidebar.markdown("<h2 style='margin-bottom: 20px;'>💹 Live Crypto Prices</h2>", unsafe_allow_html=True)
    
    # Bitcoin price card with enhanced animations
    bitcoin_change_class = "positive-change" if price_data["bitcoin"]["change"] > 0 else "negative-change"
    bitcoin_change_icon = "🟢" if price_data["bitcoin"]["change"] > 0 else "🔴"
    st.sidebar.markdown(f"""
    <div class="crypto-card" style="border-left: 4px solid {price_data['bitcoin']['color']};">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <span class="coin-symbol" style="color: {price_data['bitcoin']['color']}; animation-delay: 0.1s;">₿</span>
                <div>
                    <div style="font-weight: bold; font-size: 1.1em;">Bitcoin</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="price" style="font-size: 1.3em;">${price_data["bitcoin"]["price"]:,.2f}</div>
                <div class="{bitcoin_change_class}" style="display: flex; align-items: center; justify-content: flex-end; gap: 5px;">
                    <span>{bitcoin_change_icon}</span>
                    <span>{price_data["bitcoin"]["change"]:+.2f}%</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ethereum price card with enhanced animations
    ethereum_change_class = "positive-change" if price_data["ethereum"]["change"] > 0 else "negative-change"
    ethereum_change_icon = "🟢" if price_data["ethereum"]["change"] > 0 else "🔴"
    st.sidebar.markdown(f"""
    <div class="crypto-card" style="border-left: 4px solid {price_data['ethereum']['color']};">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <span class="coin-symbol" style="color: {price_data['ethereum']['color']}; animation-delay: 0.2s;">Ξ</span>
                <div>
                    <div style="font-weight: bold; font-size: 1.1em;">Ethereum</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="price" style="font-size: 1.3em;">${price_data["ethereum"]["price"]:,.2f}</div>
                <div class="{ethereum_change_class}" style="display: flex; align-items: center; justify-content: flex-end; gap: 5px;">
                    <span>{ethereum_change_icon}</span>
                    <span>{price_data["ethereum"]["change"]:+.2f}%</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Cardano price card with enhanced animations
    cardano_change_class = "positive-change" if price_data["cardano"]["change"] > 0 else "negative-change"
    cardano_change_icon = "🟢" if price_data["cardano"]["change"] > 0 else "🔴"
    st.sidebar.markdown(f"""
    <div class="crypto-card" style="border-left: 4px solid {price_data['cardano']['color']};">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <span class="coin-symbol" style="color: {price_data['cardano']['color']}; animation-delay: 0.3s;">₳</span>
                <div>
                    <div style="font-weight: bold; font-size: 1.1em;">Cardano</div>
                </div>
            </div>
            <div style="text-align: right;">
                <div class="price" style="font-size: 1.3em;">${price_data["cardano"]["price"]:,.2f}</div>
                <div class="{cardano_change_class}" style="display: flex; align-items: center; justify-content: flex-end; gap: 5px;">
                    <span>{cardano_change_icon}</span>
                    <span>{price_data["cardano"]["change"]:+.2f}%</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add data source and last updated info
    current_time = time.strftime("%H:%M:%S", time.localtime())
    st.sidebar.markdown(f"<div style='margin-top: 20px; text-align: center; color: #718096; font-size: 12px;'>Last updated: {current_time}</div>", unsafe_allow_html=True)
    
    # Add a divider between sidebar and chat - with reduced margins
    st.markdown("<hr style='height: 2px; background: linear-gradient(to right, #0f1216, #f7931a, #0f1216); border: none; margin: 10px 0 5px 0;'>", unsafe_allow_html=True)
    
    # Chat section header with reduced margins
    st.markdown("<h3 style='margin: 0 0 10px 0;'>💬 Chat with BitBot</h3>", unsafe_allow_html=True)
    
    # Container for chat messages with styling
    chat_container = st.container()
    
    # Style the chat messages with animations
    st.markdown("""
    <style>
        /* Chat message styling with animations */
        [data-testid="stChatMessage"] {
            background-color: #121826 !important;
            border-radius: 10px !important;
            border: 1px solid #2d3748 !important;
            margin-bottom: 10px !important;
            animation: fadeIn 0.5s ease-out;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
            opacity: 0;
            animation-fill-mode: forwards;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Apply different animation delays to messages */
        [data-testid="stChatMessage"]:nth-child(1) { animation-delay: 0.1s; }
        [data-testid="stChatMessage"]:nth-child(2) { animation-delay: 0.2s; }
        [data-testid="stChatMessage"]:nth-child(3) { animation-delay: 0.3s; }
        [data-testid="stChatMessage"]:nth-child(4) { animation-delay: 0.4s; }
        [data-testid="stChatMessage"]:nth-child(5) { animation-delay: 0.5s; }
        
        /* Hover effect for chat messages */
        [data-testid="stChatMessage"]:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            border-color: #4a5568;
        }
        
        /* User avatar with glow effect */
        [data-testid="stChatMessageAvatar-user"] {
            background-color: #2a4365 !important;
            box-shadow: 0 0 10px rgba(42, 67, 101, 0.5);
            transition: all 0.3s ease;
        }
        
        /* Assistant avatar with Bitcoin color and glow */
        [data-testid="stChatMessageAvatar-assistant"] {
            background-color: #f7931a !important;
            box-shadow: 0 0 10px rgba(247, 147, 26, 0.5);
            transition: all 0.3s ease;
        }
        
        /* Avatar hover effects */
        [data-testid="stChatMessageAvatar-user"]:hover,
        [data-testid="stChatMessageAvatar-assistant"]:hover {
            transform: scale(1.05);
        }
        
        /* Message content */
        [data-testid="stChatMessageContent"] {
            background-color: transparent !important;
            border: none !important;
            color: white !important;
            transition: all 0.3s ease;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Quick action buttons for common queries with reduced margins
    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💰 Bitcoin Price", use_container_width=True):
            query = "What's the price of Bitcoin?"
            st.session_state.messages.append({"role": "user", "content": query})
            response = process_message(query)
            if response:
                st.session_state.messages.append(response)
            st.rerun()
    with col2:
        if st.button("📊 All Prices", use_container_width=True):
            query = "Show me all cryptocurrency prices"
            st.session_state.messages.append({"role": "user", "content": query})
            response = process_message(query)
            if response:
                st.session_state.messages.append(response)
            st.rerun()
    with col3:
        if st.button("ℹ️ Help", use_container_width=True):
            query = "help"
            st.session_state.messages.append({"role": "user", "content": query})
            response = process_message(query)
            if response:
                st.session_state.messages.append(response)
            st.rerun()
    
    # Crypto-themed input box
    st.markdown("""
    <style>
        .stTextInput div[data-baseweb="input"] {
            background-color: #1a202c !important;
            border-radius: 20px !important;
            border: 1px solid #2d3748 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Input for new message with custom placeholder
    if prompt := st.chat_input("Ask BitBot about cryptocurrencies, prices, or trading..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process the message and get response
        response = process_message(prompt)
        if response:
            # Add assistant response to chat history
            st.session_state.messages.append(response)
            st.rerun()

    # Add some spacing control
    st.markdown("""<style>
    div[data-testid="stVerticalBlock"] > div:has([data-testid="stChatInput"]) {
        margin-top: -25px;
    }
    </style>""", unsafe_allow_html=True)
    
    # Display messages using Streamlit's built-in chat components
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)
                
                # Check if this message has chart data to display
                if "extra_data" in message and message["extra_data"].get("show_chart", False):
                    coin = message["extra_data"]["coin"]
                    with st.spinner(f"Loading {coin.title()} chart..."):
                        chart = create_price_chart(coin)
                        if chart:
                            st.altair_chart(chart, use_container_width=True)
                            
                            # Add price stats in a stylish container
                            data = price_data[coin]
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"<div style='background-color: #1a202c; padding: 10px; border-radius: 5px; border-left: 3px solid {data['color']}; margin-top: 10px;'>"
                                           f"<span style='font-weight: bold;'>Current Price:</span> ${data['price']:,.2f}" 
                                           f"</div>", unsafe_allow_html=True)
                            with col2:
                                change_color = "#48bb78" if data["change"] > 0 else "#f56565"
                                change_icon = "🟢" if data["change"] > 0 else "🔴"
                                st.markdown(f"<div style='background-color: #1a202c; padding: 10px; border-radius: 5px; border-left: 3px solid {change_color}; margin-top: 10px;'>"
                                           f"<span style='font-weight: bold;'>24h Change:</span> {change_icon} {data['change']:+.2f}%" 
                                           f"</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
