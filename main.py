"""
Leboncoin Universal Scraper - Production Ready
Supports all categories, locations, and filters
Optimized for Apify deployment

Author: Advanced Scraping Solutions
"""

import lbc
import json
import logging
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta


# ============================================================================
# APIFY INTEGRATION
# ============================================================================

class ApifyAdapter:
    """Adapter for Apify platform integration."""
    
    @staticmethod
    async def get_input() -> Dict[str, Any]:
        """Load input from Apify or local JSON file."""
        try:
            from apify import Actor
            return await Actor.get_input() or {}
        except (ImportError, Exception):
            # Fallback to local file for testing
            if os.path.exists("apify_input.json"):
                with open("apify_input.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
    
    @staticmethod
    async def push_data(data: Dict[str, Any]) -> None:
        """Push data to Apify dataset or local file."""
        try:
            from apify import Actor
            await Actor.push_data(data)
        except (ImportError, Exception):
            # Fallback to local storage
            output_file = "apify_output.json"
            existing = []
            if os.path.exists(output_file):
                try:
                    with open(output_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                except:
                    pass
            
            existing.append(data)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Dynamic configuration from Apify input."""
    
    def __init__(self, input_data: Dict[str, Any]):
        """Initialize configuration from input data."""
        # URLs list mode (always use this now)
        self.urls_list = input_data.get("urls_list", [])
        if isinstance(self.urls_list, str):
            self.urls_list = [self.urls_list]
        
        # Legacy support for old direct_url field
        if not self.urls_list and "direct_url" in input_data:
            direct_url = input_data.get("direct_url", "").strip()
            if direct_url:
                self.urls_list = [direct_url]
        
        # URLs mode
        self.direct_url = None
        self.search_args = None
        
        # Pagination
        self.max_pages = input_data.get("max_pages", 10)
        self.limit_per_page = input_data.get("limit_per_page", 35)
        self.delay_between_pages = input_data.get("delay_between_pages", 0)  # 0 = no delay for max speed
        
        # Age filtering
        self.max_age_days = input_data.get("max_age_days", 0)  # 0 = disabled
        self.consecutive_old_limit = 5
        
        # Price interval splitting (to avoid 100-page limit)
        self.price_interval_size = input_data.get("price_interval_size", 50000)  # Default: 50k euros
        self.split_price_intervals = input_data.get("split_price_intervals", True)  # Enable by default
        
        # Proxy settings (Apify ProxyConfiguration)
        self.proxy_configuration = input_data.get("proxyConfiguration")

        # Concurrency (parallel page fetching). Each worker uses its own isolated
        # client/session (and its own rotating proxy IP when a proxy is set).
        # By default it AUTO-SCALES to the run's allocated memory so the actor
        # uses all the CPU the user paid for (Apify gives ~1 vCPU per 4 GB).
        # An explicit `concurrency` input overrides the auto value.
        self.memory_mbytes = self._detect_memory_mbytes()
        explicit = input_data.get("concurrency")
        if explicit:
            try:
                self.concurrency = int(explicit)
            except (TypeError, ValueError):
                self.concurrency = self._auto_concurrency()
        else:
            self.concurrency = self._auto_concurrency()
        self.concurrency = max(1, min(self.concurrency, self.MAX_CONCURRENCY))

    # Hard ceiling on parallel workers (each = one session + one proxy IP).
    MAX_CONCURRENCY = 50

    @staticmethod
    def _detect_memory_mbytes() -> int:
        """Memory (MB) Apify allocated to this run, or 0 if unknown (local)."""
        for var in ("ACTOR_MEMORY_MBYTES", "APIFY_MEMORY_MBYTES"):
            value = os.environ.get(var)
            if value:
                try:
                    return int(value)
                except ValueError:
                    pass
        return 0

    def _auto_concurrency(self) -> int:
        """
        Pick a worker count that uses the run's full CPU allotment.

        Apify scales CPU with memory (~1 vCPU / 4096 MB). With a proxy each
        worker has its own rotating IP, so we scale up generously; without a
        proxy we stay conservative to avoid Datadome blocks.
        """
        mem = self.memory_mbytes
        if self.proxy_configuration:
            # ~8 workers per 4 GB core; floor 8 so small runs still parallelize.
            return max(8, min(mem // 512, self.MAX_CONCURRENCY)) if mem else 8
        # No proxy: keep it low regardless of memory (anti-bot).
        return max(3, min(mem // 2048, 8)) if mem else 3

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "direct_url": self.direct_url,
            "max_pages": self.max_pages,
            "limit_per_page": self.limit_per_page,
            "delay_between_pages": self.delay_between_pages,
            "max_age_days": self.max_age_days
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
        from urllib.parse import unquote, quote
        
        if '?' not in url:
            return url
        
        base_url = url.split('?')[0]
        query_string = url.split('?')[1]
        args = query_string.split('&')
        
        new_args = []
        price_replaced = False
        
        for arg in args:
            if '=' not in arg:
                new_args.append(arg)
                continue
            
            key, value = arg.split('=', 1)
            
            if key == "price":
                # Replace price parameter
                if new_min is None and new_max is None:
                    # Should not happen, but keep original
                    new_args.append(arg)
                elif new_min is None:
                    # Format: "min-max_value"
                    new_args.append(f"price={quote(f'min-{new_max}')}")
                elif new_max is None:
                    # Format: "min_value-max"
                    new_args.append(f"price={quote(f'{new_min}-max')}")
                else:
                    # Format: "min_value-max_value"
                    new_args.append(f"price={quote(f'{new_min}-{new_max}')}")
                price_replaced = True
            else:
                new_args.append(arg)
        
        # Note: We should never add price if it didn't exist (this function is only called
        # when price already exists in the URL, so price_replaced should always be True)
        
        return f"{base_url}?{'&'.join(new_args)}"


# ============================================================================
# URL PARSER
# ============================================================================

class LeboncoinURLParser:
    """Generic parser for Leboncoin search URLs to search configuration."""
    
    # Extract category mapping from lbc.Category enum
    CATEGORY_MAP = {cat.value: cat for cat in lbc.Category}
    
    # Only fundamental mappings for core parameters
    OWNER_TYPE_MAP = {
        "private": lbc.OwnerType.PRIVATE,
        "pro": lbc.OwnerType.PRO
    }
    
    SORT_MAP = {
        "relevance": lbc.Sort.RELEVANCE
    }
    
    AD_TYPE_MAP = {
        "offer": lbc.AdType.OFFER,
        "demand": lbc.AdType.DEMAND
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
            import time
            
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
            import time
            
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
    
    @staticmethod
    def _process_sort_and_order(search_config: Dict[str, Any]) -> None:
        """Process sort and order parameters according to Leboncoin URL patterns."""
        sort_value = search_config.pop('_sort_value', None)
        order_value = search_config.pop('_order_value', None)
        
        if sort_value and order_value:
            # Handle specific combinations
            if sort_value == "time" and order_value == "desc":
                search_config['sort'] = lbc.Sort.NEWEST
            elif sort_value == "time" and order_value == "asc":
                search_config['sort'] = lbc.Sort.OLDEST
            elif sort_value == "price" and order_value == "desc":
                search_config['sort'] = lbc.Sort.EXPENSIVE
            elif sort_value == "price" and order_value == "asc":
                search_config['sort'] = lbc.Sort.CHEAPEST
            else:
                # Fallback to default mapping
                if sort_value in LeboncoinURLParser.SORT_MAP:
                    search_config['sort'] = LeboncoinURLParser.SORT_MAP[sort_value]
        elif sort_value:
            # Only sort parameter provided
            if sort_value in LeboncoinURLParser.SORT_MAP:
                search_config['sort'] = LeboncoinURLParser.SORT_MAP[sort_value]
        # If no sort/order parameters, default to RELEVANCE (set later)
    
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
    """Process and transform ad data."""
    
    
    @staticmethod
    def normalize_datetime(date_string: Optional[str]) -> Optional[str]:
        """Normalize datetime to SQL format."""
        if not date_string:
            return None
        
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d",
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        
        return date_string
    
    @staticmethod
    def is_ad_too_old(date_string: Optional[str], max_age_days: float) -> bool:
        """Check if ad is older than threshold."""
        if max_age_days <= 0:
            return False
        
        if not date_string:
            return False
        
        try:
            ad_date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            cutoff = datetime.now() - timedelta(days=max_age_days)
            return ad_date < cutoff
        except ValueError:
            return False
    
    @staticmethod
    def convert_to_serializable(value: Any) -> Any:
        """Convert any value to JSON-serializable format (optimized)."""
        # Fast path for common types
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        
        value_type = type(value)
        
        # Fast path for collections
        if value_type is list:
            return [DataProcessor.convert_to_serializable(item) for item in value]
        elif value_type is tuple:
            return [DataProcessor.convert_to_serializable(item) for item in value]
        elif value_type is dict:
            return {k: DataProcessor.convert_to_serializable(v) for k, v in value.items()}
        elif value_type is datetime:
            return value.strftime("%Y-%m-%d %H:%M:%S")
        elif hasattr(value, '__dict__'):
            # For custom objects, use __dict__ directly (faster)
            result = {}
            for attr_name, attr_value in value.__dict__.items():
                if not attr_name.startswith('_') and attr_value is not None:
                    result[attr_name] = DataProcessor.convert_to_serializable(attr_value)
            return result
        else:
            # Fallback to string
            return str(value)


# ============================================================================
# AD TRANSFORMER
# ============================================================================

class AdTransformer:
    """Transform raw ads to structured format."""
    
    @staticmethod
    def create_detailed_ad(ad: Any, search_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed ad dictionary with ALL available fields (optimized)."""
        # Use __dict__ directly for speed (much faster than dir())
        if hasattr(ad, '__dict__'):
            ad_data = {}
            for attr_name, value in ad.__dict__.items():
                if not attr_name.startswith('_') and value is not None:
                    ad_data[attr_name] = DataProcessor.convert_to_serializable(value)
        else:
            # Fallback to dir() if no __dict__
            ad_data = {}
            for attr_name in dir(ad):
                if not attr_name.startswith('_') and not callable(getattr(ad, attr_name)):
                    value = getattr(ad, attr_name, None)
                    if value is not None:
                        ad_data[attr_name] = DataProcessor.convert_to_serializable(value)
        
        # Add metadata (reuse same timestamp string)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ad_data["scraped_at"] = now_str
        ad_data["search_category"] = search_context.get("category", "Unknown")
        ad_data["search_location"] = search_context.get("location", "Unknown")
        ad_data["search_url"] = search_context.get("search_url", "Unknown")
        
        return ad_data
    


# ============================================================================
# SCRAPING ENGINE
# ============================================================================

class ScraperEngine:
    """Core scraping engine with advanced features."""
    
    def __init__(self, config: Config, logger: logging.Logger):
        """Initialize scraper engine."""
        self.config = config
        self.logger = logger
        self.client = None
        self.clients: List["lbc.Client"] = []  # Pool for concurrent page fetching
        self.seen_ids = set()
        self.total_ads_available = None  # Total ads available on Leboncoin
        self.stats = {
            "total_ads": 0,
            "unique_ads": 0,
            "duplicates": 0,
            "locations_processed": 0,
            "pages_processed": 0,
            "errors": 0
        }
    
    def _build_client(self, proxy_url: Optional[str]) -> "lbc.Client":
        """Build a single lbc.Client (blocking - performs a cookie-init request)."""
        if proxy_url:
            # Parse proxy URL to extract components for lbc.Proxy
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            proxy = lbc.Proxy(
                host=parsed.hostname,
                port=parsed.port or 8000,
                username=parsed.username,
                password=parsed.password
            )
            return lbc.Client(proxy=proxy)
        return lbc.Client()

    async def initialize_client(self) -> None:
        """
        Initialize a pool of Leboncoin clients with optional Apify proxy.

        Each client owns an isolated session (curl_cffi sessions are not safe for
        concurrent use), so one client is reserved per in-flight page request.
        With a proxy configured, each client gets its own rotating proxy IP,
        which spreads load across IPs. Clients are created concurrently so the
        cookie-init requests overlap instead of running back-to-back.
        """
        pool_size = max(1, self.config.concurrency)

        # Resolve one proxy URL per client (None means a direct connection).
        proxy_urls: List[Optional[str]] = [None] * pool_size
        if self.config.proxy_configuration:
            try:
                from apify import Actor
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
        using_proxy = any(proxy_urls)
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
            "search_url": search_url if search_url else "Unknown"
        }

    def _fetch_page_candidates(
        self, client: "lbc.Client", search_args: Dict[str, Any],
        page_num: int, search_url: Optional[str]
    ) -> tuple[List[Dict[str, Any]], Optional[int], Optional[int], bool]:
        """
        Fetch and transform one page WITHOUT touching shared mutable state.

        Runs inside a worker thread (asyncio.to_thread), so deduplication and
        stats counting are deferred to the async coordinator. Takes the page's
        own search_args, so pages from different URLs can run concurrently.
        Returns (candidate_ads, total, max_pages, ok).
        """
        try:
            search_args = {**search_args, 'page': page_num, 'limit': self.config.limit_per_page}

            result = client.search(**search_args)
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
            error_msg = str(e)
            if "Datadome" in error_msg:
                self.logger.error(f"Access blocked by Datadome (anti-bot) on page {page_num}")
            else:
                self.logger.error(f"Failed to scrape page {page_num}: {error_msg}")
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

    def _record_page(self, page_num: int, new_ads: List[Dict[str, Any]]) -> None:
        """Update stats and log after a page's new ads have been collected."""
        self.stats["total_ads"] += len(new_ads)
        self.stats["unique_ads"] += len(new_ads)
        self.stats["pages_processed"] += 1
        self.logger.info(f"Page {page_num}: {len(new_ads)} ads extracted")

    async def _scrape_urls_concurrent(self, url_specs: List[tuple]) -> int:
        """
        Scrape ALL URLs and pages through one global pool, keeping every worker
        busy for the whole run (no idle "tail" between URLs, no per-URL restart).

        How it works:
          * A global page queue is seeded with page 1 of every URL (discovery).
          * One worker per client pulls (search_args, url, page) jobs, fetches in
            a thread, and hands the result back through a small bounded queue
            (backpressure -> memory stays O(workers + batch)).
          * When a page-1 result reveals a URL's real page count, the coordinator
            enqueues that URL's remaining pages as more jobs.
          * Dedup, stats and batched dataset pushes happen only in the coordinator.

        Returns the total number of ads scraped.
        """
        scraped = 0
        batch_ads: List[Dict[str, Any]] = []
        batch_threshold = 10 * self.config.limit_per_page
        max_pages_cfg = self.config.max_pages if self.config.max_pages > 0 else 99999

        page_queue: asyncio.Queue = asyncio.Queue()
        results_queue: asyncio.Queue = asyncio.Queue(maxsize=len(self.clients))

        # Seed discovery: page 1 of each URL. `outstanding` tracks jobs enqueued
        # but not yet consumed as results, and drives termination.
        for search_args, url in url_specs:
            page_queue.put_nowait((search_args, url, 1))
        outstanding = len(url_specs)

        self.logger.info(
            f"Starting concurrent scraping ({len(self.clients)} workers, "
            f"{len(url_specs)} search URL(s))"
        )

        async def worker(client):
            while True:
                item = await page_queue.get()
                if item is None:  # shutdown sentinel
                    return
                search_args, url, page = item
                result = await asyncio.to_thread(
                    self._fetch_page_candidates, client, search_args, page, url
                )
                await results_queue.put((search_args, url, page, result))

        workers = [asyncio.create_task(worker(c)) for c in self.clients]
        try:
            while outstanding > 0:
                search_args, url, page, (cands, total, result_max_pages, ok) = await results_queue.get()
                outstanding -= 1
                if not ok:
                    continue

                # On page 1, learn how many pages this URL has and queue the rest.
                if page == 1:
                    if total is not None:
                        self.total_ads_available = (self.total_ads_available or 0) + total
                    last_page = min(max_pages_cfg, result_max_pages) if result_max_pages else max_pages_cfg
                    if cands and last_page > 1:
                        for p in range(2, last_page + 1):
                            page_queue.put_nowait((search_args, url, p))
                            outstanding += 1

                new_ads = self._dedup_and_collect(cands)
                del cands  # free the page's raw candidates immediately
                if new_ads:
                    scraped += len(new_ads)
                    batch_ads.extend(new_ads)
                    self._record_page(page, new_ads)
                if len(batch_ads) >= batch_threshold:
                    await ApifyAdapter.push_data(batch_ads)
                    batch_ads = []
        finally:
            for _ in workers:
                page_queue.put_nowait(None)
            await asyncio.gather(*workers, return_exceptions=True)

        if batch_ads:
            await ApifyAdapter.push_data(batch_ads)

        if self.total_ads_available is not None:
            self.logger.info(f"Total ads available: {self.total_ads_available} | Scraped: {scraped} from {self.stats['pages_processed']} pages")
        else:
            self.logger.info(f"Scraping completed: {scraped} ads extracted from {self.stats['pages_processed']} pages")
        return scraped

    def _scrape_single_page(self, page_num: int, search_url: str = None) -> tuple[List[Dict[str, Any]], bool]:
        """
        Scrape a single page using parsed search arguments.
        Returns (ads_list, should_stop).
        
        Args:
            page_num: Page number to scrape
            search_url: Original URL used for this search (optional)
            
        Returns:
            Tuple of (list of ads, boolean indicating if scraping should stop)
        """
        try:
            # Use parsed search arguments instead of URL
            search_args = self.config.search_args.copy()
            search_args['page'] = page_num
            search_args['limit'] = self.config.limit_per_page
            
            result = self.client.search(**search_args)
            
            # Store and log total available ads on first page only
            if page_num == 1 and hasattr(result, 'max_pages') and hasattr(result, 'total'):
                self.total_ads_available = result.total
                self.logger.info(f"Found {result.total} ads in {result.max_pages} pages")
            
            # Fast exit if no ads
            if not hasattr(result, 'ads') or not result.ads:
                return [], True
            
            page_ads = []
            old_ads_count = 0

            # Static search context (reused for all ads on this page)
            search_context = self._build_search_context(search_args, search_url)

            # Process ads
            for ad in result.ads:
                # Fast validation
                if not hasattr(ad, 'id') or not ad.id:
                    continue
                
                # Skip duplicates (set lookup is O(1))
                if ad.id in self.seen_ids:
                    self.stats["duplicates"] += 1
                    continue
                
                # Age filter (optimized)
                # Uses index_date (last update) if available, otherwise first_publication_date
                if self.config.max_age_days > 0:
                    date_to_check = None
                    
                    # Prefer index_date (last update) over first_publication_date
                    if hasattr(ad, 'index_date') and ad.index_date:
                        date_to_check = ad.index_date
                    elif hasattr(ad, 'first_publication_date') and ad.first_publication_date:
                        date_to_check = ad.first_publication_date
                    
                    if date_to_check:
                        try:
                            # Handle both datetime objects and string dates
                            check_date = date_to_check
                            if isinstance(check_date, str):
                                check_date = datetime.strptime(check_date, "%Y-%m-%d %H:%M:%S")
                            
                            ad_age_days = (datetime.now() - check_date).days
                            if ad_age_days > self.config.max_age_days:
                                old_ads_count += 1
                                if old_ads_count >= self.config.consecutive_old_limit:
                                    return page_ads, True
                                continue
                        except (ValueError, TypeError, AttributeError):
                            # Skip if date parsing fails
                            pass
                    old_ads_count = 0
                
                # Transform and add (bulk processing, no individual error handling for speed)
                try:
                    ad_data = AdTransformer.create_detailed_ad(ad, search_context)
                    self.seen_ids.add(ad.id)
                    page_ads.append(ad_data)
                except Exception:
                    # Silent skip for speed - only count error
                    self.stats["errors"] += 1
            
            return page_ads, False
            
        except Exception as e:
            error_msg = str(e)
            if "Datadome" in error_msg:
                self.logger.error(f"Access blocked by Datadome (anti-bot) on page {page_num}")
            else:
                self.logger.error(f"Failed to scrape page {page_num}: {error_msg}")
            self.stats["errors"] += 1
            return [], True

    async def scrape_from_url(self) -> int:
        """
        Scrape one search sequentially (page by page); returns the number of ads
        scraped. Used when ordering matters (per-page delay or age filtering).
        Ads are streamed to the dataset in batches, so memory stays O(batch).
        The fast concurrent path lives in `_scrape_urls_concurrent` (driven by run).
        """
        # Validate search arguments
        if not self.config.search_args:
            self.logger.error("No search arguments provided")
            self.stats["errors"] += 1
            return 0

        # If max_pages is 0, scrape all available pages (practically unlimited)
        max_pages = self.config.max_pages if self.config.max_pages > 0 else 99999

        # Sequential scraping - optimized batching
        scraped = 0
        page = 1
        batch_size = 10  # Larger batch for fewer I/O operations
        batch_ads = []

        self.logger.info("Starting sequential scraping")

        while page <= max_pages:
            # Scrape page
            page_ads, should_stop = self._scrape_single_page(page, search_url=self.config.direct_url)

            if page_ads:
                scraped += len(page_ads)
                batch_ads.extend(page_ads)
                self._record_page(page, page_ads)

            # Push batch when full or stopping
            if len(batch_ads) >= batch_size * self.config.limit_per_page or should_stop:
                if batch_ads:
                    await ApifyAdapter.push_data(batch_ads)
                    batch_ads = []

            # Check stop conditions
            if should_stop or not page_ads or page >= max_pages:
                break

            page += 1
            # Only sleep if delay configured (avoid unnecessary async overhead)
            if self.config.delay_between_pages > 0:
                await asyncio.sleep(self.config.delay_between_pages)

        # Push remaining ads
        if batch_ads:
            await ApifyAdapter.push_data(batch_ads)

        # Display total available vs scraped
        if self.total_ads_available is not None:
            self.logger.info(f"Total ads available: {self.total_ads_available} | Scraped: {scraped} from {self.stats['pages_processed']} pages")
        else:
            self.logger.info(f"Scraping completed: {scraped} ads extracted from {self.stats['pages_processed']} pages")
        return scraped
    
    async def run(self) -> Dict[str, Any]:
        """Execute scraping pipeline."""
        self.logger.info("Starting scraper")

        # Size the thread pool to the worker count so blocking lbc.search() calls
        # (run via asyncio.to_thread) never queue behind the default 32-thread cap.
        # This is how the run actually uses all the CPU the allocated memory buys.
        loop = asyncio.get_running_loop()
        loop.set_default_executor(
            ThreadPoolExecutor(max_workers=self.config.concurrency + 4, thread_name_prefix="lbc")
        )
        mem = self.config.memory_mbytes
        self.logger.info(
            f"Concurrency: {self.config.concurrency} workers"
            + (f" (auto-scaled to {mem} MB of memory)" if mem else "")
        )

        # Initialize client once
        await self.initialize_client()
        
        total_scraped = 0
        if not self.config.urls_list:
            self.logger.error("No URLs provided in urls_list")
        else:
            # Expand each URL into price sub-intervals (to beat the 100-page cap).
            expanded_urls = []
            for url in self.config.urls_list:
                if self.config.split_price_intervals:
                    split_urls = PriceIntervalSplitter.generate_urls_with_price_intervals(
                        url, self.config.price_interval_size
                    )
                    if len(split_urls) > 1:
                        self.logger.info(f"Price interval detected: splitting into {len(split_urls)} sub-intervals")
                    expanded_urls.extend(split_urls)
                else:
                    expanded_urls.append(url)

            self.logger.info(f"Processing {len(expanded_urls)} URLs ({len(self.config.urls_list)} original, {len(expanded_urls) - len(self.config.urls_list)} from price splitting)")

            # Parse every URL to search args up front.
            url_specs = []
            for url in expanded_urls:
                search_args = LeboncoinURLParser.parse_url_to_search_config(url)
                if search_args:
                    url_specs.append((search_args, url))
                else:
                    self.logger.error(f"No search arguments parsed from URL: {url}")
                    self.stats["errors"] += 1

            # Fast path: scrape ALL URLs + pages through one global pool, keeping
            # every worker busy across URLs. Safe only when pages can be reordered
            # (more than one worker, no per-page delay, age filtering off).
            use_concurrent = (
                len(self.clients) > 1
                and self.config.delay_between_pages <= 0
                and self.config.max_age_days <= 0
            )

            if use_concurrent and url_specs:
                total_scraped = await self._scrape_urls_concurrent(url_specs)
            else:
                # Sequential fallback (preserves per-page delay / age early-stop).
                for idx, (search_args, url) in enumerate(url_specs, 1):
                    self.logger.info(f"Processing URL {idx}/{len(url_specs)}: {url}")
                    self.config.search_args = search_args
                    self.config.direct_url = url
                    total_scraped += await self.scrape_from_url()
                    self.logger.info(f"URL {idx} completed")
                    if idx < len(url_specs) and self.config.delay_between_pages > 0:
                        await asyncio.sleep(self.config.delay_between_pages)

        # Final summary
        if self.total_ads_available is not None:
            self.logger.info(f"Final summary: {self.total_ads_available} total ads available | {self.stats['unique_ads']} extracted | {self.stats['pages_processed']} pages | {self.stats['duplicates']} duplicates")
        else:
            self.logger.info(f"Final summary: {self.stats['unique_ads']} unique ads, {self.stats['pages_processed']} pages, {self.stats['duplicates']} duplicates ignored")
        
        # NOTE: ads are NOT included here - they live in the dataset. Keeping
        # them out of the run summary keeps memory O(batch) and avoids storing
        # a full copy of the dataset in the key-value store.
        return {
            "stats": self.stats,
            "ads_scraped": total_scraped,
            "config": self.config.to_dict(),
            "total_ads_available": self.total_ads_available
        }
    


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main() -> None:
    """Main entry point for Apify actor."""
    try:
        # Try Apify actor
        from apify import Actor
        
        async with Actor:
            # Get input
            input_data = await Actor.get_input() or {}
            
            # Setup
            config = Config(input_data)
            logger = Logger.setup(verbose=input_data.get("verbose", True))
            
            # Run scraper
            engine = ScraperEngine(config, logger)
            result = await engine.run()
            
            # Display total ads found
            if result.get("total_ads_available"):
                logger.info(f"TOTAL ADS FOUND IN SEARCH: {result['total_ads_available']}")
            
            # Set output
            await Actor.set_value('OUTPUT', result)
            
    except ImportError:
        # Local execution fallback
        input_data = await ApifyAdapter.get_input()
        config = Config(input_data)
        logger = Logger.setup()
        
        engine = ScraperEngine(config, logger)
        result = await engine.run()
        
        # Display total ads found
        if result.get("total_ads_available"):
            logger.info(f"TOTAL ADS FOUND IN SEARCH: {result['total_ads_available']}")
        
        # Save local output
        with open("scraper_results.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info("Results saved to: scraper_results.json")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

