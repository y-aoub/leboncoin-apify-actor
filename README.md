# 🕸️ Leboncoin Scraper

**Leboncoin scraper** to extract listings from any Leboncoin search URL — real estate, cars, classifieds and more. Paste a `leboncoin.fr/recherche?...` URL and get clean, structured data (price, location, images, dates and seller info) exported to **JSON or CSV**. It's the easiest way to get **Leboncoin data** without writing code and without an official Leboncoin API (Leboncoin has no public API).

Stop scrolling and copy-pasting ads by hand. This Leboncoin data extractor collects thousands of listings automatically, filters by your exact criteria (price, surface, rooms, mileage, year, location, keywords…), and turns France's largest classifieds marketplace into a usable dataset for analysis, monitoring and lead generation.

## ✨ Why this Leboncoin scraper

- **Works from any search URL** — replicate your exact Leboncoin search, including every filter.
- **All categories** — real estate, cars & vehicles, jobs, electronics, fashion, home and more.
- **Gets more results** — automatic price-interval splitting works around Leboncoin's 100-page limit, so large searches return far more listings.
- **Fast** — parallel page fetching pulls multiple pages at once.
- **Structured output** — every available field, exported to **JSON or CSV**.
- **No code required** — just paste a URL and run.

---

## 🎯 Use cases

- **Real estate analysis** — track apartments and houses for sale or rent by area and price.
- **Car & vehicle market research** — monitor models, prices and mileage.
- **Price monitoring & deal hunting** — spot new and underpriced listings fast.
- **Lead generation** — build prospect lists from professional sellers.
- **Competitive watch & market research** — measure supply, pricing and trends across France.

---

## 🚀 How to scrape Leboncoin (step by step)

1. Go to **Leboncoin.fr** and run a search with the filters you want.
2. Copy the search URL **from the results page** (it should start with `https://www.leboncoin.fr/recherche?...`).
3. Paste it into the **Search URLs** input (you can add several URLs at once).
4. Click **Run** and download your data from the **Output** / **Dataset** tab in minutes.

No technical knowledge required.

> Tip: use the `max_pages` setting to control volume (set `0` to scrape all available pages), and `concurrency` to control speed.

### Example input

```json
{
  "max_age_days": 0,
  "max_pages": 0,
  "urls_list": [
    "https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=250000-400000&rooms=2-4&real_estate_type=2"
  ],
  "limit_per_page": 35,
  "concurrency": 3,
  "delay_between_pages": 0
}
```

### Example output

```json
{
  "id": 3083651141,
  "first_publication_date": "2025-10-29 23:25:53",
  "index_date": "2025-10-29 23:25:53",
  "status": "active",
  "category_id": "9",
  "category_name": "Ventes immobilières",
  "subject": "Appartement 2 pièces 28 m²",
  "body": "2 pièces, complètement rénové, Paris 11ème...",
  "brand": "leboncoin",
  "ad_type": "offer",
  "url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3083651141",
  "price": 329500,
  "images": [...],
  "attributes": [
    { "key": "real_estate_type", "value": "2", "value_label": "Appartement" },
    { "key": "square", "value": "28", "value_label": "28 m²" },
    { "key": "rooms", "value": "2", "value_label": "2" },
    { "key": "bedrooms", "value": "1", "value_label": "1 ch." },
    { "key": "energy_rate", "value": "f", "value_label": "F" }
  ],
  "location": {
    "country_id": "FR",
    "region_id": "12",
    "region_name": "Ile-de-France",
    "department_id": "75",
    "department_name": "Paris",
    "city": "Paris",
    "zipcode": "75011",
    "lat": 48.85763,
    "lng": 2.38005
  },
  "has_phone": true,
  "scraped_at": "2025-10-29 22:29:25",
  "search_category": "IMMOBILIER_VENTES_IMMOBILIERES",
  "search_location": "Paris",
  "search_url": "https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=250000-400000&rooms=2-4&real_estate_type=2"
}
```

---

## 📦 Output data fields

Each Leboncoin listing is exported with fields including:

| Field | Description |
|---|---|
| `id` | Unique listing ID |
| `subject` | Listing title |
| `body` | Full description text |
| `price` | Price in euros |
| `category_id` / `category_name` | Leboncoin category |
| `ad_type` | `offer` or `demand` |
| `url` | Direct link to the listing |
| `images` | Image URLs |
| `attributes` | Category-specific details (surface, rooms, mileage, fuel, year, DPE…) |
| `location` | City, zipcode, department, region + **GPS coordinates** (lat/lng) |
| `has_phone` | Whether the seller published a phone number |
| `first_publication_date` / `index_date` | Publish / last-update dates |
| `scraped_at` | Extraction timestamp |

Export everything to **JSON, CSV, Excel or via the Apify API**.

---

## ⚙️ Input settings

- **Search URLs** — one or more `…/recherche?…` URLs to scrape.
- **Max pages** — cap pages per search (`0` = all available pages).
- **Ads per page** — listings per page (default 35).
- **Concurrency** — pages fetched in parallel (default 3).
- **Max ad age (days)** — skip listings older than N days.
- **Delay between pages** — optional rate limiting.

---

## ⁉️ FAQ

**How do I scrape Leboncoin?**
Run a search on Leboncoin.fr, copy the results URL, paste it into this actor and run it. The scraper paginates automatically and returns structured data.

**Do I need the Leboncoin API?**
No. Leboncoin has no public API — this actor extracts the same data directly from search results, so no API key is required.

**What data can I extract from Leboncoin?**
Title, description, price, category, images, listing attributes (surface, rooms, mileage, year, fuel, DPE…), location with GPS coordinates, dates and a phone-availability flag.

**Can it scrape real estate, cars and other categories?**
Yes. It works on any Leboncoin search URL, so every category is supported — real estate, vehicles, jobs, electronics, fashion and more.

**Can it get all results from a large search?**
Yes. Leboncoin caps results at ~100 pages per search; the actor automatically splits price intervals to retrieve many more listings.

**In what format is the data exported?**
JSON, CSV, Excel, or programmatically through the Apify API.

**Is scraping Leboncoin legal?**
This actor collects only publicly visible data. Personal data (e.g. seller details) falls under GDPR, so make sure your storage and use have a lawful basis, and respect Leboncoin's Terms of Service.

**Why are some runs blocked?**
Leboncoin uses DataDome anti-bot protection, so very high request rates can occasionally be blocked. If you hit blocks, lower the `concurrency` setting or add a small `delay between pages`, and split very large jobs into smaller runs.

---

## 🚀 Ready?

Open the **Input** tab → paste your Leboncoin search URL(s) → **Run** → get your data in the **Output** tab.

## 🆘 Support

Questions or issues? Post them in the **Issues** tab — I'm happy to help and respond as soon as possible! 😊
