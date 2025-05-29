BOT_NAME = "BitBot"
BOT_TONE = "friendly"
     #static data
crypto_db = {  
    "Bitcoin": {  
        "price_trend": "rising",  
        "market_cap": "high",  
        "energy_use": "high",  
        "sustainability_score": 3/10  
    },  
    "Ethereum": {  
        "price_trend": "stable",  
        "market_cap": "high",  
        "energy_use": "medium",  
        "sustainability_score": 6/10  
    },  
    "Cardano": {  
        "price_trend": "rising",  
        "market_cap": "medium",  
        "energy_use": "low",  
        "sustainability_score": 8/10  
    }  
}  

def respond_to_query(user_query):
    user_query = user_query.lower()

    if "sustainable" in user_query:
        recommend = max(crypto_db, key=lambda x: crypto_db[x]["sustainability_score"])
        return f"{recommend} 🌱 is eco-friendly and has long-term potential!"

    elif "trending" in user_query or "up" in user_query:
        trending = [coin for coin in crypto_db if crypto_db[coin]["price_trend"] == "rising"]
        return f"These coins are trending up 📈: {', '.join(trending)}"

    elif "profitable" in user_query or "invest" in user_query:
        profitable = [
            coin for coin in crypto_db
            if crypto_db[coin]["price_trend"] == "rising" and crypto_db[coin]["market_cap"] == "high"
        ]
        if profitable:
            return f"{profitable[0]} 🚀 is showing strong growth potential!"
        else:
            return "Hmm, none look very profitable right now. 🧐"

    else:
        return "I'm not sure how to help with that. Try asking about 'sustainable' or 'profitable' coins!"
    

while True:
    user_input = input("You: ")
    if user_input.lower() in ["hi", "hello", "hey"]:
        print(f"{BOT_NAME}: Hey there! 🖐 I'm {BOT_NAME}, your crypto sidekick! Ready to help you choose smart, sustainable investments.")
    else:
        print(f"{BOT_NAME}: {respond_to_query(user_input)}")

    
    
    



