# BitBot - Cryptocurrency Assistant Chatbot

<div align="center">

🤖 💰 📈 A stylish and interactive cryptocurrency chatbot powered by Groq LLM

</div>

## Overview

BitBot is an AI-powered cryptocurrency assistant chatbot that provides information about cryptocurrencies, their prices, and educational content about blockchain technology. The project features both a command-line interface (CLI) and a beautiful Streamlit web application with interactive price charts, crypto-themed UI, and responsive animations.

## Features

- **Cryptocurrency Price Information**: Get current prices for Bitcoin, Ethereum, and Cardano
- **Interactive Price Charts**: Visualize 30-day price trends with hoverable data points
- **Educational Content**: Ask questions about cryptocurrencies and blockchain technology
- **Multiple Interfaces**:
  - Command-line interface (CLI) for terminal use
  - Streamlit web application with a polished crypto-themed UI
- **Responsive UI**: Beautiful dark theme with animations, transitions, and crypto-brand colors
- **Quick Actions**: One-click buttons for common queries

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/wilson69-root/bitbot.git
   cd bitbot
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following variables:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   BOT_NAME=BitBot  # Optional, defaults to "BitBot"
   LLM_MODEL=llama3-8b-8192  # Optional, defaults to "llama3-8b-8192"
   ```

## Usage

### Streamlit Web App (Recommended)

Run the Streamlit web application for the full interactive experience:

```bash
python -m streamlit run streamlit_app.py
```

The web app will open in your default browser at `http://localhost:8501`.

### Command Line Interface

Alternatively, you can use the CLI version:

```bash
python app.py
```

## Using BitBot

### Commands and Queries

- **Price Information**:
  - "What's the price of Bitcoin?"
  - "How much is Ethereum worth?"
  - "Show me the value of Cardano"

- **Price Charts**:
  - "Show me Bitcoin chart"
  - "Display Ethereum graph"
  - "Cardano price history"

- **Educational Content**:
  - "What is blockchain?"
  - "Explain cryptocurrency mining"
  - "How do smart contracts work?"

- **Help and Commands**:
  - Type "help" or "commands" to see available options

## Technical Details

### Components

- **app.py**: Command-line interface implementation
- **streamlit_app.py**: Streamlit web application with enhanced UI
- **requirements.txt**: Project dependencies
- **.env**: Configuration for API keys and settings

### Key Technologies

- **LLM**: [Groq API](https://groq.com/) via LangChain integration
- **Frontend**: [Streamlit](https://streamlit.io/) for the web interface
- **Data Visualization**: [Altair](https://altair-viz.github.io/) for interactive charts
- **Data Processing**: [Pandas](https://pandas.pydata.org/) for data manipulation

### Architecture

1. **User Input Processing**:
   - Command detection for price queries, chart requests, and educational questions
   - Pattern matching for cryptocurrency references

2. **Response Generation**:
   - Price data retrieval from hardcoded data (future: API integration)
   - LLM-powered responses for educational content
   - Chart generation for price visualization

3. **UI Components**:
   - Sidebar with live price cards
   - Chat interface with message animation
   - Quick action buttons
   - Interactive price charts with statistics

## Future Enhancements

### Real-time Data Integration
- **Cryptocurrency API Integration**:
  - Connect to CoinGecko, CoinMarketCap, or Binance APIs for real-time price data
  - Implement websocket connections for live price updates without refreshing
  - Add historical data endpoints for more accurate and comprehensive charts

- **Market Sentiment Analysis**:
  - Integrate with Twitter/X API to analyze social media sentiment about cryptocurrencies
  - Implement news aggregation from crypto news sources
  - Create sentiment indicators to complement price data

- **Advanced Charting Features**:
  - Add technical indicators (Moving Averages, RSI, MACD)
  - Implement candlestick charts with volume indicators
  - Support for different timeframes (1h, 4h, 1d, 1w)

### Extended Functionality
- **Support for 50+ cryptocurrencies** with detailed profiles and statistics
- **Price alerts and notifications** via email or browser notifications
- **User authentication system** with saved preferences and watchlists
- **Trading simulations** with paper trading functionality
- **Portfolio tracking** with performance analytics and visualizations
- **Mobile app version** using Flutter or React Native

### AI and ML Enhancements
- **Price prediction models** using machine learning
- **Personalized trading recommendations** based on risk profile
- **Enhanced conversation context** for more natural interactions
- **Voice interface** for hands-free operation
- **Multi-language support** for global accessibility

## Dependencies

- streamlit==1.45.1
- langchain-groq
- python-dotenv
- pandas
- altair
- colorama
- requests

## License

[MIT License](LICENSE)

---

Created with ❤️ for cryptocurrency enthusiasts
