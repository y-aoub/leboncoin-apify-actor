"""
Leboncoin Universal Scraper for Apify.

Parses Leboncoin search URLs, fetches result pages (in parallel when safe),
and pushes structured ad data to the Apify dataset.
"""

import json
import logging
import os
import asyncio
from typing import Any, Optional, Dict, List
from datetime import datetime

import lbc

try:
    from apify import Actor
    _HAS_APIFY = True
except ImportError:  # Local execution / tests without the Apify SDK installed.
    Actor = None
    _HAS_APIFY = False


# ============================================================================
# APIFY INTEGRATION
# ============================================================================

class ApifyIO:
    """Input/output layer: uses the Apify SDK when available, else local files."""

    LOCAL_INPUT = "apify_input.json"
    LOCAL_DATASET = "apify_output.json"
    LOCAL_OUTPUT = "scraper_results.json"

    # Pay-per-event event names (must match the events configured in the
    # Apify Console monetization settings). Prices are set there, not in code.
    EVENT_ACTOR_START = "actor-start"
    EVENT_RESULT = "listing-scraped"

    @staticmethod
    async def get_input() -> Dict[str, Any]:
        """Load the actor input."""
        if _HAS_APIFY:
            return await Actor.get_input() or {}
        if os.path.exists(ApifyIO.LOCAL_INPUT):
            with open(ApifyIO.LOCAL_INPUT, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    async def push_data(items: List[Dict[str, Any]]) -> None:
        """Push a batch of ads to the dataset (or append to a local file)."""
        if not items:
            return
        if _HAS_APIFY:
            await Actor.push_data(items)
            return
        existing = []
        if os.path.exists(ApifyIO.LOCAL_DATASET):
            try:
                with open(ApifyIO.LOCAL_DATASET, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except (json.JSONDecodeError, OSError):
                existing = []
        existing.extend(items)
        with open(ApifyIO.LOCAL_DATASET, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    @staticmethod
    async def set_output(value: Dict[str, Any]) -> None:
        """Store the run summary in the key-value store (or a local file)."""
        if _HAS_APIFY:
            await Actor.set_value("OUTPUT", value)
        else:
            with open(ApifyIO.LOCAL_OUTPUT, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2)

    @staticmethod
    async def charge(event_name: str, count: int = 1) -> bool:
        """
        Charge a pay-per-event event; return True if its budget limit is reached.

        No-op off-platform (local runs) or when the Actor isn't on a pay-per-event
        pricing model. Never raises — billing problems must not crash a scrape.
        """
        if not _HAS_APIFY or count <= 0:
            return False
        try:
            result = await Actor.charge(event_name=event_name, count=count)
            return bool(getattr(result, "event_charge_limit_reached", False))
        except Exception:
            # e.g. SDK too old, or Actor not on a pay-per-event plan.
            return False


class _DatasetBatcher:
    """Buffers ads and pushes them to the dataset once a threshold is reached."""

    def __init__(self, threshold: int):
        self.threshold = threshold
        self.buffer: List[Dict[str, Any]] = []

    async def add(self, ads: List[Dict[str, Any]]) -> None:
        """Buffer ads, flushing automatically when the threshold is hit."""
        if not ads:
            return
        self.buffer.extend(ads)
        if len(self.buffer) >= self.threshold:
            await self.flush()

    async def flush(self) -> None:
        """Push any buffered ads (no-op when empty)."""
        if self.buffer:
            await ApifyIO.push_data(self.buffer)
            self.buffer = []


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Run configuration parsed from the Apify input."""

    def __init__(self, input_data: Dict[str, Any]):
        urls = input_data.get("urls_list", [])
        if isinstance(urls, str):
            urls = [urls]
        self.urls_list: List[str] = urls

        # Pagination
        self.max_pages = input_data.get("max_pages", 10)
        self.limit_per_page = input_data.get("limit_per_page", 35)
        self.delay_between_pages = input_data.get("delay_between_pages", 0)  # 0 = no delay

        # Proxy (Apify ProxyConfiguration). Required in practice to get past
        # Leboncoin's Datadome anti-bot - without it every request is blocked.
        self.proxy_configuration = input_data.get("proxyConfiguration")

        # Concurrency (parallel page fetching). Each worker uses its own isolated
        # client/session (and its own rotating proxy IP when a proxy is set), so
        # this is safe. Higher with a proxy since load spreads across IPs; lower
        # without one to limit anti-bot blocking.
        default_concurrency = 8 if self.proxy_configuration else 3
        try:
            self.concurrency = int(input_data.get("concurrency", default_concurrency))
        except (TypeError, ValueError):
            self.concurrency = default_concurrency
        self.concurrency = max(1, min(self.concurrency, 30))

        # Age filtering (0 = disabled). Stops a search once enough consecutive
        # ads exceed the age threshold (results are date-sorted).
        self.max_age_days = input_data.get("max_age_days", 0)
        self.consecutive_old_limit = 5

        # Price interval splitting, to work around Leboncoin's 100-page cap.
        self.price_interval_size = input_data.get("price_interval_size", 50000)
        self.split_price_intervals = input_data.get("split_price_intervals", True)

    @property
    def effective_max_pages(self) -> int:
        """Page cap to honor (max_pages=0 means 'all available pages')."""
        return self.max_pages if self.max_pages > 0 else 99999

    def summary(self) -> Dict[str, Any]:
        """Compact configuration summary for the run output."""
        return {
            "max_pages": self.max_pages,
            "limit_per_page": self.limit_per_page,
            "delay_between_pages": self.delay_between_pages,
            "max_age_days": self.max_age_days,
            "concurrency": self.concurrency,
        }


# ============================================================================
# LOGGING SETUP
# ============================================================================

class Logger:
    """Professional logging with Apify-style formatting."""
    
    @staticmethod
    def setup(verbose: bool = True) -> logging.Logger:
        """Configure Apify-style logging with minimal color."""
        logger = logging.getLogger("scraper")
        logger.setLevel(logging.INFO if verbose else logging.WARNING)
        logger.handlers.clear()
        
        # Create simple formatter without timestamp
        formatter = logging.Formatter(
            "[apify] %(levelname)-6s %(message)s"
        )
        
        # Create a stream handler
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO if verbose else logging.WARNING)
        
        # Add the handler to the logger
        logger.addHandler(handler)
        
        return logger




# ============================================================================
# PRICE INTERVAL SPLITTER
# ============================================================================

class PriceIntervalSplitter:
    """Split price intervals into smaller sub-intervals to avoid 100-page limit."""
    
    # Default interval size (in euros) - can be configured
    DEFAULT_INTERVAL_SIZE = 50000  # 50k euros per interval
    
    @staticmethod
    def split_price_interval(min_price: int, max_price: int, interval_size: Optional[int] = None) -> List[tuple[int, int]]:
        """
        Split a price range into smaller intervals.
        
        Args:
            min_price: Minimum price (0 if None)
            max_price: Maximum price (9999999 if None)
            interval_size: Size of each interval in euros (default: 50000)
            
        Returns:
            List of (min, max) tuples for each sub-interval
        """
        if interval_size is None:
            interval_size = PriceIntervalSplitter.DEFAULT_INTERVAL_SIZE
        
        intervals = []
        current_min = min_price
        
        while current_min < max_price:
            current_max = min(current_min + interval_size, max_price)
            intervals.append((current_min, current_max))
            current_min = current_max
        
        return intervals
    
    @staticmethod
    def extract_price_from_url(url: str) -> Optional[tuple[Optional[int], Optional[int]]]:
        """
        Extract price range from URL.
        
        Args:
            url: Leboncoin search URL
            
        Returns:
            Tuple of (min_price, max_price) or None if no price parameter
            Values can be None for 'min' or 'max' keywords
        """
        try:
            from urllib.parse import unquote
            
            if '?' not in url:
                return None
            
            query_string = url.split('?')[1]
            args = query_string.split('&')
            
            for arg in args:
                if '=' not in arg:
                    continue
                
                key, value = arg.split('=', 1)
                value = unquote(value)
                
                if key == "price":
                    # Parse price value
                    if '-' in value and len(value.split('-')) == 2:
                        range_parts = value.split('-')
                        try:
                            if range_parts[0] == 'min':
                                # Format: "min-1600"
                                max_val = int(range_parts[1])
                                return (None, max_val)
                            elif range_parts[1] == 'max':
                                # Format: "2020-max"
                                min_val = int(range_parts[0])
                                return (min_val, None)
                            else:
                                # Format: "100-200"
                                min_val = int(range_parts[0])
                                max_val = int(range_parts[1])
                                return (min_val, max_val)
                        except ValueError:
                            return None
                    else:
                        # Single price value (not a range)
                        try:
                            price = int(value)
                            return (price, price)
                        except ValueError:
                            return None
            
            return None
            
        except Exception:
            return None
    
    @staticmethod
    def generate_urls_with_price_intervals(base_url: str, interval_size: Optional[int] = None) -> List[str]:
        """
        Generate multiple URLs by splitting price interval into sub-intervals.
        
        Args:
            base_url: Original Leboncoin search URL
            interval_size: Size of each price interval in euros (default: 50000)
            
        Returns:
            List of URLs with different price intervals, or [base_url] if no price parameter
        """
        price_range = PriceIntervalSplitter.extract_price_from_url(base_url)
        
        if price_range is None:
            # No price parameter, return original URL
            return [base_url]
        
        original_min, original_max = price_range
        
        # Set defaults for min/max
        actual_min = original_min if original_min is not None else 0
        actual_max = original_max if original_max is not None else 10000000  # 10M euros as practical max
        
        # If interval is too small, don't split
        if actual_max - actual_min <= (interval_size or PriceIntervalSplitter.DEFAULT_INTERVAL_SIZE):
            return [base_url]
        
        # Split into intervals
        intervals = PriceIntervalSplitter.split_price_interval(actual_min, actual_max, interval_size)
        
        # Generate URLs for each interval
        urls = []
        for i, (interval_min, interval_max) in enumerate(intervals):
            # For first interval: preserve original min if it was "min"
            # For last interval: preserve original max if it was "max"
            new_min = None if (i == 0 and original_min is None) else interval_min
            new_max = None if (i == len(intervals) - 1 and original_max is None) else interval_max
            
            new_url = PriceIntervalSplitter._replace_price_in_url(
                base_url, 
                new_min,
                new_max
            )
            urls.append(new_url)
        
        return urls
    
    @staticmethod
    def _replace_price_in_url(url: str, new_min: Optional[int], new_max: Optional[int]) -> str:
        """
        Replace price parameter in URL with new values.
        
        Args:
            url: Original URL
            new_min: New minimum price (None for 'min')
            new_max: New maximum price (None for 'max')
            
        Returns:
            URL with updated price parameter
        """
        from urllib.parse import quote

        if '?' not in url:
            return url

        base_url, query_string = url.split('?', 1)
        new_args = []

        for arg in query_string.split('&'):
            if '=' not in arg:
                new_args.append(arg)
                continue

            key, _ = arg.split('=', 1)
            if key != "price":
                new_args.append(arg)
            elif new_min is None and new_max is None:
                new_args.append(arg)  # Should not happen; keep original.
            elif new_min is None:
                new_args.append(f"price={quote(f'min-{new_max}')}")
            elif new_max is None:
                new_args.append(f"price={quote(f'{new_min}-max')}")
            else:
                new_args.append(f"price={quote(f'{new_min}-{new_max}')}")

        return f"{base_url}?{'&'.join(new_args)}"


# ============================================================================
# URL PARSER
# ============================================================================

class LeboncoinURLParser:
    """Generic parser for Leboncoin search URLs to search configuration."""
    
    # Category id -> lbc.Category enum, derived from the library.
    CATEGORY_MAP = {cat.value: cat for cat in lbc.Category}

    OWNER_TYPE_MAP = {
        "private": lbc.OwnerType.PRIVATE,
        "pro": lbc.OwnerType.PRO,
    }

    AD_TYPE_MAP = {
        "offer": lbc.AdType.OFFER,
        "demand": lbc.AdType.DEMAND,
    }

    @staticmethod
    def parse_url_to_search_config(url: str) -> Dict[str, Any]:
        """
        Parse a Leboncoin search URL and convert it to a search configuration dictionary.
        This parser is truly generic and handles ALL possible URL parameters.
        
        Args:
            url: Leboncoin search URL
            
        Returns:
            Dictionary containing search configuration compatible with lbc.Client.search()
        """
        try:
            from urllib.parse import unquote
            
            # Extract query string and split by &
            if '?' not in url:
                return {}
            
            query_string = url.split('?')[1]
            args = query_string.split('&')
            
            search_config = {}
            kwargs_filters = {}
            
            for arg in args:
                if '=' not in arg:
                    continue
                    
                key, value = arg.split('=', 1)
                value = unquote(value)
                
                # Parse each parameter
                if key == "text":
                    search_config['text'] = value
                    
                elif key == "category":
                    try:
                        category_id = str(value)  # Convert to string for mapping lookup
                        if category_id in LeboncoinURLParser.CATEGORY_MAP:
                            search_config['category'] = LeboncoinURLParser.CATEGORY_MAP[category_id]
                        else:
                            # Fallback to TOUTES_CATEGORIES if not found
                            search_config['category'] = lbc.Category.TOUTES_CATEGORIES
                    except ValueError:
                        pass
                        
                elif key == "locations":
                    locations = LeboncoinURLParser._parse_locations(value)
                    if locations:
                        search_config['locations'] = locations
                        
                elif key == "owner_type":
                    if value in LeboncoinURLParser.OWNER_TYPE_MAP:
                        search_config['owner_type'] = LeboncoinURLParser.OWNER_TYPE_MAP[value]
                        
                elif key == "sort":
                    # Store sort parameter for later processing with order
                    search_config['_sort_value'] = value
                        
                elif key == "order":
                    # Store order parameter for later processing with sort
                    search_config['_order_value'] = value
                            
                elif key == "ad_type":
                    if value in LeboncoinURLParser.AD_TYPE_MAP:
                        search_config['ad_type'] = LeboncoinURLParser.AD_TYPE_MAP[value]
                        
                elif key == "shippable":
                    if value == "1":
                        search_config['shippable'] = True
                        
                elif key == "page":
                    # Skip page parameter
                    continue
                    
                else:
                    # Generic parameter - add to kwargs filters
                    parsed_value = LeboncoinURLParser._parse_generic_value(value)
                    if parsed_value is not None:
                        # Keep ranges as tuples, convert single values to lists of strings
                        if isinstance(parsed_value, tuple):
                            # Range values stay as tuples (e.g., (100, 200), (0, 1600))
                            kwargs_filters[key] = parsed_value
                        elif isinstance(parsed_value, list):
                            # List values stay as lists of strings (e.g., ['BMW', 'Audi'])
                            kwargs_filters[key] = parsed_value
                        else:
                            # Single values become lists of strings (e.g., 'BMW' -> ['BMW'])
                            kwargs_filters[key] = [str(parsed_value)]
            
            # Add kwargs filters to search config
            if kwargs_filters:
                search_config.update(kwargs_filters)
            
            # Process sort and order parameters
            LeboncoinURLParser._process_sort_and_order(search_config)
            
            # Set default values
            search_config.setdefault('sort', lbc.Sort.RELEVANCE)  # Default to relevance
            search_config.setdefault('ad_type', lbc.AdType.OFFER)
            search_config.setdefault('limit', 35)
            
            return search_config
            
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return {}
    
    @staticmethod
    def _parse_locations(location_str: str) -> List[lbc.City]:
        """Parse location string to lbc.City objects."""
        locations = []
        
        # Split by comma for multiple locations
        location_parts = location_str.split(',')
        
        for location_part in location_parts:
            location = LeboncoinURLParser._parse_single_location(location_part.strip())
            if location:
                locations.append(location)
        
        return locations
    
    @staticmethod
    def _parse_single_location(location_str: str) -> Optional[lbc.City]:
        """Parse a single location string to lbc.City object."""
        try:
            # Handle formats like "Paris__48.86023250788424_2.339006433295173_9256_1000"
            # or "Nanterre_92000__48.88822_2.19428_9256_1000"
            if '__' in location_str:
                parts = location_str.split('__')
                city_part = parts[0]
                coords_part = parts[1] if len(parts) > 1 else ""
                
                # Extract city name
                city_parts = city_part.split('_')
                # Check if last part is a postal code (digits only)
                if len(city_parts) >= 2 and city_parts[-1].isdigit():
                    # Format: "Nanterre_92000" -> city_name = "Nanterre", postal_code = "92000"
                    city_name = '_'.join(city_parts[:-1])
                else:
                    # Format: "Paris" -> city_name = "Paris"
                    city_name = city_part
                
                # Extract coordinates: lat, lng, default_radius, radius
                coords_parts = coords_part.split('_')
                if len(coords_parts) >= 2:
                    lat = float(coords_parts[0])
                    lng = float(coords_parts[1])
                    default_radius = int(coords_parts[2]) if len(coords_parts) > 2 else None
                    radius = int(coords_parts[3]) if len(coords_parts) > 3 else 0
                    
                    return lbc.City(
                        lat=lat,
                        lng=lng,
                        radius=radius,
                        default_radius=default_radius,
                        city=city_name
                    )
            
            # Handle simple format like "Nanterre_92000" or "Marseille"
            else:
                city_parts = location_str.split('_')
                if len(city_parts) >= 2 and city_parts[-1].isdigit():
                    # Format: "Nanterre_92000" -> city_name = "Nanterre", postal_code = "92000"
                    city_name = '_'.join(city_parts[:-1])
                    postal_code = city_parts[-1]
                    
                    # Get coordinates for the city
                    coords = LeboncoinURLParser._get_city_coordinates(city_name, postal_code)
                    
                    return lbc.City(
                        lat=coords['lat'],
                        lng=coords['lng'],
                        radius=0,
                        city=city_name
                    )
                else:
                    # Format: "Marseille" -> city_name = "Marseille", no postal code
                    city_name = location_str
                    
                    # Get coordinates for the city without postal code
                    coords = LeboncoinURLParser._get_city_coordinates(city_name, "")
                    
                    return lbc.City(
                        lat=coords['lat'],
                        lng=coords['lng'],
                        radius=0,
                        city=city_name
                    )
                
        except Exception as e:
            print(f"Error parsing location '{location_str}': {e}")
            return None
    
    @staticmethod
    def _get_city_coordinates(city_name: str, postal_code: str = "") -> Dict[str, float]:
        """Get coordinates for a city using free API."""
        try:
            import requests

            # Build search query for API Adresse (data.gouv.fr)
            query_parts = []
            if city_name:
                query_parts.append(city_name.replace("_", " "))
            if postal_code:
                query_parts.append(postal_code)
            
            query = " ".join(query_parts)
            
            # API Adresse de data.gouv.fr (gratuite pour la France)
            url = "https://api-adresse.data.gouv.fr/search"
            params = {
                "q": query,
                "limit": 1,
                "type": "municipality"  # Focus on municipalities
            }
            
            # Make request with timeout
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("features") and len(data["features"]) > 0:
                    feature = data["features"][0]
                    geometry = feature.get("geometry", {})
                    coordinates = geometry.get("coordinates", [])
                    
                    if len(coordinates) >= 2:
                        # API returns [lng, lat] format
                        lng, lat = coordinates[0], coordinates[1]
                        return {"lat": lat, "lng": lng}
            
            # Fallback to Nominatim (OpenStreetMap) if API Adresse fails
            return LeboncoinURLParser._get_coordinates_nominatim(query)
            
        except Exception as e:
            print(f"Error getting coordinates for {city_name}: {e}")
            # Fallback to Paris coordinates
            return {"lat": 48.8566, "lng": 2.3522}
    
    @staticmethod
    def _get_coordinates_nominatim(query: str) -> Dict[str, float]:
        """Fallback method using Nominatim (OpenStreetMap)."""
        try:
            import requests

            # Nominatim API (OpenStreetMap) - free but with rate limiting
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": f"{query}, France",
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            # Add user agent header (required by Nominatim)
            headers = {
                "User-Agent": "LeboncoinScraper/1.0"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result["lat"])
                    lng = float(result["lon"])
                    return {"lat": lat, "lng": lng}
            
            # Final fallback to Paris
            return {"lat": 48.8566, "lng": 2.3522}
            
        except Exception as e:
            print(f"Error with Nominatim fallback: {e}")
            return {"lat": 48.8566, "lng": 2.3522}
    
    # (sort, order) -> lbc.Sort. Anything not listed (e.g. relevance, or a bare
    # sort value) falls back to the RELEVANCE default applied by the caller.
    SORT_ORDER_MAP = {
        ("time", "desc"): lbc.Sort.NEWEST,
        ("time", "asc"): lbc.Sort.OLDEST,
        ("price", "desc"): lbc.Sort.EXPENSIVE,
        ("price", "asc"): lbc.Sort.CHEAPEST,
    }

    @staticmethod
    def _process_sort_and_order(search_config: Dict[str, Any]) -> None:
        """Map the Leboncoin sort/order URL params to an lbc.Sort value."""
        sort_value = search_config.pop('_sort_value', None)
        order_value = search_config.pop('_order_value', None)

        sort = LeboncoinURLParser.SORT_ORDER_MAP.get((sort_value, order_value))
        if sort is not None:
            search_config['sort'] = sort
        # Otherwise the RELEVANCE default is applied by the caller.

    @staticmethod
    def _parse_generic_value(value: str) -> Any:
        """Parse a generic parameter value."""
        try:
            # Try to parse as range first (e.g., "100-200", "min-1600", "2020-max")
            if '-' in value and len(value.split('-')) == 2:
                range_parts = value.split('-')
                try:
                    if range_parts[0] == 'min':
                        # Format: "min-1600"
                        max_val = int(range_parts[1])
                        return (0, max_val)
                    elif range_parts[1] == 'max':
                        # Format: "2020-max"
                        min_val = int(range_parts[0])
                        return (min_val, 9999999)
                    else:
                        # Format: "100-200"
                        min_val = int(range_parts[0])
                        max_val = int(range_parts[1])
                        return (min_val, max_val)
                except ValueError:
                    pass
            
            # Try to parse as comma-separated list
            if ',' in value:
                parts = value.split(',')
                # Always return as strings
                return [x.strip() for x in parts]
            
            # Try single integer
            try:
                return int(value)
            except ValueError:
                # Fall back to string
                return value
                
        except Exception:
            return value




# ============================================================================
# DATA PROCESSING
# ============================================================================

class DataProcessor:
    """Helpers for turning lbc objects into JSON-serializable data."""

    @staticmethod
    def convert_to_serializable(value: Any) -> Any:
        """Recursively convert a value into JSON-serializable form."""
        # Fast path for common scalar types.
        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        value_type = type(value)
        if value_type is list or value_type is tuple:
            return [DataProcessor.convert_to_serializable(item) for item in value]
        if value_type is dict:
            return {k: DataProcessor.convert_to_serializable(v) for k, v in value.items()}
        if value_type is datetime:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(value, '__dict__'):
            # Custom objects (lbc dataclasses): expose public, non-null attributes.
            return {
                name: DataProcessor.convert_to_serializable(attr)
                for name, attr in value.__dict__.items()
                if not name.startswith('_') and attr is not None
            }
        return str(value)


# ============================================================================
# AD TRANSFORMER
# ============================================================================

class AdTransformer:
    """Turn an lbc.Ad into a flat, JSON-serializable dictionary."""

    @staticmethod
    def create_detailed_ad(ad: Any, search_context: Dict[str, Any]) -> Dict[str, Any]:
        """Expose all public ad fields plus the search context metadata."""
        ad_data = DataProcessor.convert_to_serializable(ad)
        ad_data["scraped_at"] = search_context["scraped_at"]
        ad_data["search_category"] = search_context["category"]
        ad_data["search_location"] = search_context["location"]
        ad_data["search_url"] = search_context["search_url"]
        return ad_data



# ============================================================================
# SCRAPING ENGINE
# ============================================================================

class ScraperEngine:
    """Fetches Leboncoin search pages and emits structured ads."""

    # Number of pages worth of ads to buffer before pushing a dataset batch.
    BATCH_PAGES = 10

    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.client = None
        self.clients: List["lbc.Client"] = []  # Isolated clients for concurrent fetching.
        self.seen_ids = set()
        self.total_ads_available: Optional[int] = None  # Total ads reported by Leboncoin.
        self.charge_limit_reached = False  # Set once the pay-per-event budget is hit.
        self.stats = {
            "total_ads": 0,
            "unique_ads": 0,
            "duplicates": 0,
            "pages_processed": 0,
            "errors": 0,
        }

    @property
    def _batch_threshold(self) -> int:
        return self.BATCH_PAGES * self.config.limit_per_page
    
    def _build_client(self, proxy_url: Optional[str] = None) -> "lbc.Client":
        """Build a single lbc.Client (blocking - performs a cookie-init request)."""
        if proxy_url:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            proxy = lbc.Proxy(
                host=parsed.hostname,
                port=parsed.port or 8000,
                username=parsed.username,
                password=parsed.password,
            )
            return lbc.Client(proxy=proxy)
        return lbc.Client()

    async def initialize_client(self) -> None:
        """
        Initialize a pool of Leboncoin clients for concurrent page fetching.

        Each client owns an isolated session (curl_cffi sessions are not safe for
        concurrent use, and the lbc 403-retry swaps the session), so a worker must
        never share a client. When a proxy is configured we request a fresh URL per
        client, spreading load across rotating IPs (essential to get past Datadome).
        Clients are created concurrently so the cookie-init requests overlap.
        """
        pool_size = max(1, self.config.concurrency)

        # Resolve one proxy URL per client (None means a direct connection).
        proxy_urls: List[Optional[str]] = [None] * pool_size
        if self.config.proxy_configuration and _HAS_APIFY:
            try:
                proxy_config = await Actor.create_proxy_configuration(
                    actor_proxy_input=self.config.proxy_configuration
                )
                if proxy_config:
                    proxy_urls = [await proxy_config.new_url() for _ in range(pool_size)]
                    self.logger.info("Proxy configured successfully")
            except Exception as e:
                self.logger.error(f"Failed to configure proxy: {e}")

        # Build clients concurrently (each constructor performs a blocking request).
        built = await asyncio.gather(
            *[asyncio.to_thread(self._build_client, purl) for purl in proxy_urls],
            return_exceptions=True
        )
        self.clients = [c for c in built if isinstance(c, lbc.Client)]

        # Fallback: ensure we always have at least one working client.
        if not self.clients:
            self.clients = [self._build_client(None)]

        self.client = self.clients[0]
        using_proxy = any(purl for purl in proxy_urls)
        if not using_proxy:
            self.logger.warning(
                "Running WITHOUT a proxy - Leboncoin/Datadome will likely block requests. "
                "Enable Apify Proxy (FR residential) in the input."
            )
        self.logger.info(
            f"Initialized {len(self.clients)} client(s) "
            f"{'with proxy' if using_proxy else 'without proxy'}"
        )

    def _build_search_context(self, search_args: Dict[str, Any], search_url: Optional[str]) -> Dict[str, Any]:
        """Build the static per-page search context attached to each ad."""
        category_name = "Unknown"
        location_name = "Unknown"

        category = search_args.get('category')
        if category:
            if hasattr(category, 'name'):
                category_name = category.name
            elif hasattr(category, 'value'):
                category_name = category.value
            elif isinstance(category, str):
                category_name = category

        locations = search_args.get('locations', [])
        if locations and len(locations) > 0:
            first_loc = locations[0]
            if hasattr(first_loc, 'city'):
                location_name = first_loc.city
            elif hasattr(first_loc, 'name'):
                location_name = first_loc.name

        return {
            "category": category_name,
            "location": location_name,
            "search_url": search_url if search_url else "Unknown",
            # Computed once per page and shared by every ad on it.
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _search_params(self, search_args: Dict[str, Any], page_num: int) -> Dict[str, Any]:
        """Search args for a specific page (page/limit applied per request)."""
        return {**search_args, 'page': page_num, 'limit': self.config.limit_per_page}

    def _log_page_error(self, page_num: int, exc: Exception) -> None:
        """Log a page fetch failure, calling out Datadome blocks specifically."""
        if "Datadome" in str(exc):
            self.logger.error(f"Access blocked by Datadome (anti-bot) on page {page_num}")
        else:
            self.logger.error(f"Failed to scrape page {page_num}: {exc}")

    def _record_page(self, page_num: int, new_ads: List[Dict[str, Any]]) -> None:
        """Update stats and log after a page's new ads have been collected."""
        self.stats["total_ads"] += len(new_ads)
        self.stats["unique_ads"] += len(new_ads)
        self.stats["pages_processed"] += 1
        self.logger.info(f"Page {page_num}: {len(new_ads)} ads extracted")

    def _log_scrape_summary(self, scraped_count: int) -> None:
        """Log the per-URL scrape summary."""
        if self.total_ads_available is not None:
            self.logger.info(
                f"Total ads available: {self.total_ads_available} | "
                f"Scraped: {scraped_count} from {self.stats['pages_processed']} pages"
            )
        else:
            self.logger.info(
                f"Scraping completed: {scraped_count} ads extracted "
                f"from {self.stats['pages_processed']} pages"
            )

    def _is_ad_too_old(self, ad: Any, now: datetime) -> bool:
        """True if the ad's most recent date exceeds the configured max age."""
        date_to_check = getattr(ad, 'index_date', None) or getattr(ad, 'first_publication_date', None)
        if not date_to_check:
            return False
        try:
            if isinstance(date_to_check, str):
                date_to_check = datetime.strptime(date_to_check, "%Y-%m-%d %H:%M:%S")
            return (now - date_to_check).days > self.config.max_age_days
        except (ValueError, TypeError, AttributeError):
            return False

    def _scrape_single_page(
        self, page_num: int, search_args: Dict[str, Any], search_url: Optional[str]
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Scrape one page sequentially (with dedup/age filtering applied inline).

        Returns (new_ads, should_stop). should_stop signals the end of pagination
        (no more results, an error, or the age threshold reached).
        """
        try:
            result = self.client.search(**self._search_params(search_args, page_num))

            # Record the total available count from the first page.
            if page_num == 1 and hasattr(result, 'max_pages') and hasattr(result, 'total'):
                self.total_ads_available = result.total
                self.logger.info(f"Found {result.total} ads in {result.max_pages} pages")

            if not getattr(result, 'ads', None):
                return [], True

            search_context = self._build_search_context(search_args, search_url)
            page_ads: List[Dict[str, Any]] = []
            consecutive_old = 0
            now = datetime.now()

            for ad in result.ads:
                if not getattr(ad, 'id', None):
                    continue
                if ad.id in self.seen_ids:
                    self.stats["duplicates"] += 1
                    continue

                # Age filter: stop once enough consecutive ads are too old.
                if self.config.max_age_days > 0:
                    if self._is_ad_too_old(ad, now):
                        consecutive_old += 1
                        if consecutive_old >= self.config.consecutive_old_limit:
                            return page_ads, True
                        continue
                    consecutive_old = 0

                try:
                    page_ads.append(AdTransformer.create_detailed_ad(ad, search_context))
                    self.seen_ids.add(ad.id)
                except Exception:
                    self.stats["errors"] += 1

            return page_ads, False

        except Exception as e:
            self._log_page_error(page_num, e)
            self.stats["errors"] += 1
            return [], True

    def _fetch_and_transform_page(
        self, client: "lbc.Client", page_num: int,
        search_args: Dict[str, Any], search_url: Optional[str]
    ) -> tuple[List[Dict[str, Any]], Optional[int], Optional[int], bool]:
        """
        Fetch and transform a page WITHOUT touching shared mutable state.

        Runs inside a worker thread (via asyncio.to_thread), so deduplication and
        counting are deferred to the async coordinator. Returns
        (candidate_ads, total, max_pages, ok).
        """
        try:
            result = client.search(**self._search_params(search_args, page_num))
            total = getattr(result, 'total', None)
            result_max_pages = getattr(result, 'max_pages', None)

            if not getattr(result, 'ads', None):
                return [], total, result_max_pages, True

            search_context = self._build_search_context(search_args, search_url)
            candidates: List[Dict[str, Any]] = []
            for ad in result.ads:
                if not getattr(ad, 'id', None):
                    continue
                try:
                    candidates.append(AdTransformer.create_detailed_ad(ad, search_context))
                except Exception:
                    self.stats["errors"] += 1
            return candidates, total, result_max_pages, True

        except Exception as e:
            self._log_page_error(page_num, e)
            self.stats["errors"] += 1
            return [], None, None, False

    def _dedup_and_collect(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate candidate ads against seen_ids (single-threaded, safe)."""
        new_ads = []
        for ad_data in candidates:
            ad_id = ad_data.get("id")
            if ad_id is None:
                continue
            if ad_id in self.seen_ids:
                self.stats["duplicates"] += 1
                continue
            self.seen_ids.add(ad_id)
            new_ads.append(ad_data)
        return new_ads

    async def scrape_from_url(
        self, search_args: Dict[str, Any], search_url: str
    ) -> List[Dict[str, Any]]:
        """
        Scrape all pages for one search, choosing the fastest safe strategy.

        The concurrent path is used only when pages can be safely reordered:
        multiple workers are available, no per-page delay is requested, and age
        filtering is off (it relies on strict sequential early-stop). Otherwise
        pages are scraped sequentially.
        """
        if not search_args:
            self.logger.error("No search arguments provided")
            self.stats["errors"] += 1
            return []

        if (
            len(self.clients) > 1
            and self.config.delay_between_pages <= 0
            and self.config.max_age_days <= 0
        ):
            return await self._scrape_concurrent(search_args, search_url)
        return await self._scrape_sequential(search_args, search_url)

    async def _handle_page(
        self, page_num: int, new_ads: List[Dict[str, Any]],
        all_ads: List[Dict[str, Any]], batcher: _DatasetBatcher
    ) -> None:
        """Account for, buffer, and charge for a page's new (deduplicated) ads."""
        if not new_ads:
            return
        all_ads.extend(new_ads)
        self._record_page(page_num, new_ads)
        await batcher.add(new_ads)
        # Pay-per-event: charge per delivered listing (no-op off pay-per-event).
        if await ApifyIO.charge(ApifyIO.EVENT_RESULT, len(new_ads)):
            self.charge_limit_reached = True
            self.logger.info("Pay-per-event budget limit reached - stopping scrape")

    async def _scrape_concurrent(
        self, search_args: Dict[str, Any], search_url: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch pages in parallel using the client pool.

        Page 1 is fetched first to learn the real number of available pages, then
        the rest are fetched concurrently. Each in-flight request holds one client
        from the pool (so no session is used concurrently); deduplication, stats and
        dataset pushes all happen here in the single coordinator.
        """
        all_ads: List[Dict[str, Any]] = []
        batcher = _DatasetBatcher(self._batch_threshold)
        max_pages = self.config.effective_max_pages

        self.logger.info(f"Starting concurrent scraping ({len(self.clients)} workers)")

        # Page 1 reveals the real page count.
        candidates, total, result_max_pages, ok = await asyncio.to_thread(
            self._fetch_and_transform_page, self.clients[0], 1, search_args, search_url
        )
        if not ok:
            return all_ads

        if total is not None and result_max_pages is not None:
            self.total_ads_available = total
            self.logger.info(f"Found {total} ads in {result_max_pages} pages")

        await self._handle_page(1, self._dedup_and_collect(candidates), all_ads, batcher)

        last_page = min(max_pages, result_max_pages) if result_max_pages else max_pages

        # Fetch remaining pages concurrently, one client per in-flight request.
        if candidates and last_page > 1:
            client_queue: asyncio.Queue = asyncio.Queue()
            for client in self.clients:
                client_queue.put_nowait(client)

            async def fetch_page(page_num: int):
                client = await client_queue.get()
                try:
                    return page_num, await asyncio.to_thread(
                        self._fetch_and_transform_page, client, page_num, search_args, search_url
                    )
                finally:
                    client_queue.put_nowait(client)

            tasks = [asyncio.create_task(fetch_page(p)) for p in range(2, last_page + 1)]

            # Process as results complete for incremental pushes and bounded memory.
            try:
                for coro in asyncio.as_completed(tasks):
                    page_num, (cands, _t, _mp, page_ok) = await coro
                    if page_ok:
                        await self._handle_page(page_num, self._dedup_and_collect(cands), all_ads, batcher)
                    if self.charge_limit_reached:
                        break
            finally:
                # Cancel any still-pending page fetches (e.g. on early budget stop).
                for t in tasks:
                    if not t.done():
                        t.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)

        await batcher.flush()
        self._log_scrape_summary(len(all_ads))
        return all_ads

    async def _scrape_sequential(
        self, search_args: Dict[str, Any], search_url: str
    ) -> List[Dict[str, Any]]:
        """Fetch pages one by one (used when ordering or rate-limiting matters)."""
        all_ads: List[Dict[str, Any]] = []
        batcher = _DatasetBatcher(self._batch_threshold)
        max_pages = self.config.effective_max_pages

        self.logger.info("Starting sequential scraping")

        page = 1
        while page <= max_pages:
            # _scrape_single_page already deduplicates against seen_ids.
            page_ads, should_stop = self._scrape_single_page(page, search_args, search_url)
            await self._handle_page(page, page_ads, all_ads, batcher)

            if should_stop or not page_ads or page >= max_pages or self.charge_limit_reached:
                break

            page += 1
            if self.config.delay_between_pages > 0:
                await asyncio.sleep(self.config.delay_between_pages)

        await batcher.flush()
        self._log_scrape_summary(len(all_ads))
        return all_ads

    def _expand_urls(self, urls: List[str]) -> List[str]:
        """Expand each search URL into price sub-intervals when enabled."""
        expanded: List[str] = []
        for url in urls:
            if self.config.split_price_intervals:
                split_urls = PriceIntervalSplitter.generate_urls_with_price_intervals(
                    url, self.config.price_interval_size
                )
                if len(split_urls) > 1:
                    self.logger.info(f"Price interval detected: splitting into {len(split_urls)} sub-intervals")
                expanded.extend(split_urls)
            else:
                expanded.append(url)
        return expanded

    def _log_final_summary(self) -> None:
        """Log the aggregate summary across all processed URLs."""
        if self.total_ads_available is not None:
            self.logger.info(
                f"Final summary: {self.total_ads_available} total ads available | "
                f"{self.stats['unique_ads']} extracted | {self.stats['pages_processed']} pages | "
                f"{self.stats['duplicates']} duplicates"
            )
        else:
            self.logger.info(
                f"Final summary: {self.stats['unique_ads']} unique ads, "
                f"{self.stats['pages_processed']} pages, {self.stats['duplicates']} duplicates ignored"
            )

    def _result(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assemble the run output object."""
        return {
            "stats": self.stats,
            "ads": ads,
            "config": self.config.summary(),
            "total_ads_available": self.total_ads_available,
        }

    async def run(self) -> Dict[str, Any]:
        """Run the full scraping pipeline over every configured URL."""
        self.logger.info("Starting scraper")

        if not self.config.urls_list:
            self.logger.error("No URLs provided in urls_list")
            return self._result([])

        await self.initialize_client()

        expanded_urls = self._expand_urls(self.config.urls_list)
        self.logger.info(
            f"Processing {len(expanded_urls)} URLs "
            f"({len(self.config.urls_list)} original, "
            f"{len(expanded_urls) - len(self.config.urls_list)} from price splitting)"
        )

        all_ads: List[Dict[str, Any]] = []
        for idx, url in enumerate(expanded_urls, 1):
            self.logger.info(f"Processing URL {idx}/{len(expanded_urls)}: {url}")

            search_args = LeboncoinURLParser.parse_url_to_search_config(url)
            self.logger.info(f"Search arguments from URL {idx}: {search_args}")

            url_ads = await self.scrape_from_url(search_args, url)
            all_ads.extend(url_ads)
            self.logger.info(f"URL {idx} completed: {len(url_ads)} ads extracted")

            if idx < len(expanded_urls) and self.config.delay_between_pages > 0:
                await asyncio.sleep(self.config.delay_between_pages)

        self._log_final_summary()
        return self._result(all_ads)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def _execute() -> None:
    """Load input, run the scraper, and store the output."""
    input_data = await ApifyIO.get_input()
    logger = Logger.setup(verbose=input_data.get("verbose", True))

    # Pay-per-event: charge the one-off start fee (no-op off pay-per-event).
    await ApifyIO.charge(ApifyIO.EVENT_ACTOR_START, 1)

    engine = ScraperEngine(Config(input_data), logger)
    result = await engine.run()

    if result.get("total_ads_available"):
        logger.info(f"TOTAL ADS FOUND IN SEARCH: {result['total_ads_available']}")

    await ApifyIO.set_output(result)
    if not _HAS_APIFY:
        logger.info(f"Results saved to: {ApifyIO.LOCAL_OUTPUT}")


async def main() -> None:
    """Entry point: run inside the Apify actor context when available."""
    if _HAS_APIFY:
        async with Actor:
            await _execute()
    else:
        await _execute()


if __name__ == "__main__":
    asyncio.run(main())

