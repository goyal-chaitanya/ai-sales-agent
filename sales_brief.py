# sales_brief.py

import os
from dotenv import load_dotenv
from openai import OpenAI


# 1. Import the scraper function we built earlier
from scraper import scrape_website_text

# 2. Load the hidden API keys from your .env vault
load_dotenv()

# 3. Initialize the OpenAI client (it automatically finds the key in your .env file)
client = OpenAI(
    api_key = os.getenv("GROQ_API_KEY"),
    base_url= "https://api.groq.com/openai/v1"
)

def generate_sales_brief(url):
    """
    Scrapes a website and uses OpenAI to generate a 3-bullet sales brief.
    """
    # Step A: Get the text from the website
    print(f"Scraping data from {url}...")
    website_text = scrape_website_text(url)
    
    # If the scraper failed, return the error
    if "Error scraping" in website_text:
        return website_text

    print("Analyzing data with OpenAI...")
    
    # Step B: Pass the text to OpenAI with specific instructions
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Fast, smart, and very cheap model
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a world-class B2B sales researcher. "
                        "I will provide you with scraped text from a company's website. "
                        "Based ONLY on this text, generate a tight, 3-bullet-point summary covering:\n"
                        "1. The Company's Industry\n"
                        "2. Their Core Product/Service\n"
                        "3. Their Likely Primary Bottlenecks or Pain Points (infer this based on what they do).\n\n"
                        "Keep it extremely concise, like a briefing document read right before a pitch."
                    )
                },
                {
                    "role": "user",
                    "content": f"Here is the website text:\n\n{website_text}"
                }
            ]
        )
        
        # Step C: Extract and return the AI's response
        brief = response.choices[0].message.content
        return brief
        
    except Exception as e:
        return f"Error connecting to OpenAI: {str(e)}"

# --- Quick Test ---
if __name__ == "__main__":
    # You can change this to any B2B company's URL to test it
    test_url = "https://stripe.com" 
    
    print("\n==================================")
    result = generate_sales_brief(test_url)
    print("\n--- 🎯 SALES BRIEF ---")
    print(result)
    print("==================================\n")