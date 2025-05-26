import requests
from bs4 import BeautifulSoup
import csv
import time
import random

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html',
        'Connection': 'keep-alive'
    }

def fetch_page(url):
    try:
        res = requests.get(url, headers=get_headers(), timeout=15)
        res.raise_for_status()
        return res.text
    except Exception as err:
        print("Failed to load page:", err)
        return None

def scrape_olx():
    url = "https://www.olx.in/items/q-car-cover"
    html = fetch_page(url)
    if not html:
        return

    soup = BeautifulSoup(html, 'html.parser')

    selectors = [
        "li.EIR5N",
        "div[data-cy='l-card']",
        "div[data-testid='adCard']",
        "div[data-aut-id='itemBox']"
    ]

    listings = []
    items = []

    for sel in selectors:
        items = soup.select(sel)
        if items:
            print(f"Using selector: {sel} — found {len(items)} listings")
            break

    if not items:
        print("No listings found. Try checking the page manually.")
        return

    for ad in items:
        title, price, location, link = None, None, None, None

        # Try extracting title
        for t_sel in ["span._2tW1I", "h6[data-cy='adTitle']", "div[data-aut-id='itemTitle']"]:
            t = ad.select_one(t_sel)
            if t and t.text.strip():
                title = t.text.strip()
                break

        # Try extracting price
        for p_sel in ["span.T3q9n", "span[data-aut-id='itemPrice']", "span[data-cy='adPrice']"]:
            p = ad.select_one(p_sel)
            if p and p.text.strip():
                price = p.text.strip()
                break

        # Try extracting location
        for l_sel in ["span._2kHMt", "span[data-aut-id='item-location']", "span[data-cy='ad-location']"]:
            l = ad.select_one(l_sel)
            if l and l.text.strip():
                location = l.text.strip()
                break

        # Extract link
        a_tag = ad.find('a')
        if a_tag and a_tag.get('href'):
            link = a_tag['href']
            if not link.startswith('http'):
                link = "https://www.olx.in" + link

        if title and price and location and link:
            listings.append([title, price, location, link])
            print("✓", title)
        else:
            print("Skipped an item with missing info.")

        time.sleep(random.uniform(0.5, 1.2))  

    if listings:
        with open("olx_covers.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Price", "Location", "Link"])
            writer.writerows(listings)
        print(f"\nSaved {len(listings)} listings to olx_covers.csv")
    else:
        print("No valid listings found.")

if __name__ == "__main__":
    scrape_olx()
