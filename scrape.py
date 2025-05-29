import streamlit as st
import os
import re
import requests
from dotenv import load_dotenv
from llama_index.llms.anthropic import Anthropic
from llama_index.core import Settings

load_dotenv()
Settings.llm = Anthropic(model="claude-3-haiku-20240307", api_key=os.getenv("ANTHROPIC_API_KEY"))


# Map destination to currency code (simplified)
CITY_TO_CURRENCY = {
    "tokyo": "JPY", "japan": "JPY",
    "london": "GBP", "uk": "GBP",
    "rome": "EUR", "italy": "EUR",
    "paris": "EUR", "france": "EUR",
    "sydney": "AUD", "australia": "AUD",
    "bangkok": "THB", "thailand": "THB"
}

def extract_trip_info(user_input):
    # Regex extract
    city_match = re.search(r"(to|in)\s+([A-Z][a-z]+)", user_input)
    budget_match = re.search(r"\$(\d+)", user_input)
    days_match = re.search(r"(\d+)\s+days", user_input)

    city = city_match.group(2).lower() if city_match else None
    budget = float(budget_match.group(1)) if budget_match else None
    days = int(days_match.group(1)) if days_match else None

    return city, budget, days

def get_exchange_rate(currency_code):
    API_KEY = os.getenv("EXCHANGERATE_API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/pair/USD/{currency_code}"
    res = requests.get(url)
    if res.status_code != 200:
        return None
    return res.json().get("conversion_rate")

def personalized_budget_answer(user_input):
    city, budget, days = extract_trip_info(user_input)
    if not (city and budget and days):
        return "Please specify your destination, budget (USD), and number of days. (ex: I'm going to Paris for 5 days on $200)"

    currency = CITY_TO_CURRENCY.get(city)
    if not currency:
        return f"Sorry, I don't know the currency for {city.title()}."

    rate = get_exchange_rate(currency)
    if not rate:
        return f"Failed to fetch exchange rate for USD → {currency}."

    local_amount = budget * rate
    daily = round(local_amount / days, 2)

    context = (
        f"You are going to {city.title()} for {days} days with a budget of ${budget} USD.\n"
           f"The exchange rate is 1 USD = {rate:.2f} {currency}, so you’ll have ~{local_amount:.2f} {currency} total.\n"
        f"That’s about {daily:.2f} {currency} per day.\n"
    )

    prompt = (
        context +
        "Based on this, what kind of trip can the user afford? Include lodging, food, transport tips, and budget constraints."
    )

    return Settings.llm.complete(prompt).text.strip()

# print(personalized_budget_answer("I'm going to Tokyo for 7 days on $600"))
