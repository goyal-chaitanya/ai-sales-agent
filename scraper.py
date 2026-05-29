# scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_website_text(url):
    """
    Fetches a URL and returns the clean, readable text from the homepage.
    """
    try:
        # 1. Add headers to act like a real browser (some sites block basic Python scripts)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # 2. Fetch the webpage content
        print(f"Scraping: {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        # Raise an error if the request failed (e.g., 404 Not Found)
        response.raise_for_status()

        # 3. Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # 4. Remove unwanted elements like scripts, styles, and navigation menus
        for unnecessary_element in soup(["script", "style", "nav", "footer", "header"]):
            unnecessary_element.decompose() # This deletes the tag and its contents

        # 5. Extract the readable text
        # separator=' ' ensures words don't get smashed together when tags are removed
        # strip=True removes extra whitespace at the beginning/end
        clean_text = soup.get_text(separator=' ', strip=True)

        return clean_text

    except Exception as e:
        return f"Error scraping the website: {str(e)}"


# --- Quick Test ---
# If you run this file directly, it will test the function. 
# (It won't run this part if you import it into another file later).
if __name__ == "__main__":
    test_url = "https://example.com"
    result = scrape_website_text(test_url)
    print("\n--- Scraped Text ---")
    print(result)