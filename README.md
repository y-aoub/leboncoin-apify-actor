# 🏠 Leboncoin Scraper

A simple tool to extract Leboncoin listings and turn the French marketplace into structured, usable data.

---

## 💡 Why use this tool?

Stop scrolling and copy-pasting. Collect thousands of listings automatically, filter by your exact criteria, and export to JSON or CSV for analysis.

### 🎯 Use cases

✅ Real-estate analysis • Price monitoring • Deal hunting • Competitive watch • Lead generation • Market research

---

## 🚀 Quick start

1. Go to Leboncoin.fr and perform a search
2. Copy the search URL (e.g. `https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=100000-300000`)
3. Paste it in the input (or provide multiple URLs) and run
4. Fetch your data in minutes

No technical knowledge required.

---

## 📊 Example Input

```json
{
  "max_age_days": 0,
  "max_pages": 0,
  "proxyConfiguration": {
    "useApifyProxy": false,
    "proxyUrls": [
      "http://LOGIN:PASSWORD@HOST:PORT"
    ]
  },
  "urls_list": [
    "https://www.leboncoin.fr/recherche?category=9&locations=Paris&price=250000-400000&rooms=2-4&real_estate_type=2"
  ],
  "limit_per_page": 35,
  "delay_between_pages": 0
}
```

---

## 📤 Example Output

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
    {
      "key": "real_estate_type",
      "value": "2",
      "value_label": "Appartement"
    },
    {
      "key": "square",
      "value": "28",
      "value_label": "28 m²"
    },
    {
      "key": "rooms",
      "value": "2",
      "value_label": "2"
    },
    {
      "key": "bedrooms",
      "value": "1",
      "value_label": "1 ch."
    },
    {
      "key": "energy_rate",
      "value": "f",
      "value_label": "F"
    }
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

## ✨ Features

- Advanced filters: price, surface, rooms, DPE, mileage, year, fuel, geolocation, keywords
- Rich export: title, description, price, photos, address, GPS, seller info, metadata
- Formats: JSON or CSV
- Performance: 100–200 ads/min, no page limit (set `max_pages = 0`)

---

## 📋 Supported categories

Real estate • Vehicles • Jobs • Electronics • Home & Garden • Fashion • Leisure • Services

---

## FAQ

- Cost: $39/month — unlimited extraction
- Legal: public data only. Respect Terms of Service and GDPR
- Blocking: FR residential proxies recommended for high volume
- Freshness: data is collected at runtime
- Automation: integrates with Apify API and workflows

---

## ⚠️ Important

Use responsibly • GDPR compliant • Not affiliated with Leboncoin

---

## 🚀 Ready?

1) Open the "Input" tab → paste your URL(s) → Run  
2) Get your data in "Dataset"

Questions? See "Issues".
