import json
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# -------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -------------------------------------------------------------------------
CACHE_FILENAME = "data/argus_news_cache.json"
START_URL = (
    "https://www.argusmedia.com/en/news-and-insights/latest-market-news"
    "?filters=%7B%22language%22%3A%22%27en-gb%27%22%2C%22commodity%22%3A"
    "%22%27Biofuels%27%2C%27Base+Oil%27%2C%27Oil+Products%27%22%2C%22market"
    "%22%3A%22%27Jet+Fuel-Kerosine%27%22%7D&page=1&filter_language=en-gb"
    "&filter_commodity=oil+products%3Abiofuels%2Cbase+oil%2Coil+products"
    "&filter_market=jet+fuels%3Ajet+fuel-kerosine"
)
DAYS_LIMIT = 90


# -------------------------------------------------------------------------
# SETUP DRIVER
# -------------------------------------------------------------------------
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"  # noqa E501
    )

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------
def parse_date(date_str):
    return datetime.strptime(date_str.strip(), "%d/%m/%y")


def is_recent(date_obj):
    if not date_obj:
        return False
    delta = datetime.now() - date_obj
    return delta.days <= DAYS_LIMIT


def save_to_cache(data):
    try:
        with open(CACHE_FILENAME, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"✅ Saved {len(data)} articles to {CACHE_FILENAME}")
    except Exception as e:
        print(f"❌ Error saving cache: {e}")


def load_from_cache():
    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# -------------------------------------------------------------------------
# SCRAPING LOGIC
# -------------------------------------------------------------------------
def scrape_article_body(driver, url):
    """Navigates to the article URL and scrapes the content body."""
    print(f"   -> navigating to: {url}")
    driver.get(url)

    try:
        # Wait for the dynamic container to load.
        # using CSS Selector partial match for class containing 'NewsPost_newsPost__'   # noqa E501
        wait = WebDriverWait(driver, 10)
        article_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='NewsPost_newsPost__']")
            )
        )

        # Extract text from p, ul, ol, table tags inside this container
        content_parts = []
        tags = article_container.find_elements(
            By.CSS_SELECTOR, "p, ul, ol, table"
        )

        for tag in tags:
            text = tag.text.strip()
            if text:
                content_parts.append(text)

        return "\n\n".join(content_parts)

    except Exception as e:
        print(f"   -> Failed to scrape body: {e}")
        return ""


def run_scraper():
    driver = setup_driver()
    scraped_data = []

    try:
        print("🚀 Loading main page...")
        driver.get(START_URL)

        # Wait specifically for the news items to appear
        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "qa-news-item")
            )
        )

        # Find all news item cards
        news_items = driver.find_elements(By.CLASS_NAME, "qa-news-item")
        print(f"🔎 Found {len(news_items)} items. Extracting metadata...")

        # STEP 1: Extract Metadata first (Title, Date, Link)
        # We do this first so we don't lose the page state by navigating away.
        pending_articles = []

        for item in news_items:
            try:
                title_elem = item.find_element(By.CLASS_NAME, "qa-item-title")
                summary_elem = item.find_element(
                    By.CLASS_NAME, "qa-item-summary"
                )
                link_elem = item.find_element(By.TAG_NAME, "a")
                date_elem = link_elem.find_element(
                    By.CLASS_NAME, "qa-item-date"
                )

                title = title_elem.text.strip()
                summary = summary_elem.text.strip()
                link = link_elem.get_attribute("href")
                date_str = date_elem.text.strip()

                date_obj = parse_date(date_str)

                if is_recent(date_obj):
                    pending_articles.append(
                        {
                            "title": title,
                            "summary": summary,
                            "link": link,
                            "date": date_str,
                        }
                    )
                else:
                    print(f"   - Skipping old article: {date_str}")

            except Exception as e:
                print(f"Error parsing item metadata: {e}")
                continue

        print(
            f"📝 Found {len(pending_articles)} recent articles to scrape details for."  # noqa E501
        )

        # STEP 2: Visit each link and scrape body
        for article in pending_articles:
            full_text = scrape_article_body(driver, article["link"])

            # Construct final data object
            record = {
                "display_card": {
                    "title": article["title"],
                    "summary": article["summary"],
                    "date": article["date"],
                    "link": article["link"],
                },
                "llm_context": {
                    "full_text": full_text,
                    "source_url": article["link"],
                    "published_date": article["date"],
                },
            }
            scraped_data.append(record)
            time.sleep(1)  # Be polite to server

        # Save to JSON
        save_to_cache(scraped_data)

    finally:
        driver.quit()
        print("🏁 Driver closed.")

    return scraped_data


# -------------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    action = (
        input(
            "Type 'scrape' to run new scrape, or press Enter to load cache: "
        )
        .strip()
        .lower()
    )

    if action == "scrape":
        data = run_scraper()
    else:
        data = load_from_cache()
        if not data:
            print("Cache is empty. Running scraper...")
            data = run_scraper()

    if data:
        print("\n--- Sample Output ---")
        print(f"Title: {data[0]['display_card']['title']}")
        print(f"Summary: {data[0]['display_card']['summary']}")
