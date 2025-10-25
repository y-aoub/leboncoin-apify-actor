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
        # Check if search_args are provided directly or need to be parsed from URL
        if "search_args" in input_data and input_data["search_args"]:
            # Direct search arguments provided
            self.search_args = input_data["search_args"]
            self.direct_url = ""  # No URL when using direct search args
            # print(f"Using direct search arguments: {self.search_args}")
        else:
            # URL scraping mode - parse URL to search args
            raw_url = input_data.get("direct_url", "").strip()
            self.direct_url = raw_url
            self.search_args = LeboncoinURLParser.parse_url_to_search_config(raw_url)
            
            # Log parsed search arguments
            if self.search_args:
                print(f"Parsed search arguments from URL: {self.search_args}")
        
        # Pagination
        self.max_pages = input_data.get("max_pages", 10)
        self.limit_per_page = input_data.get("limit_per_page", 35)
        self.delay_between_pages = input_data.get("delay_between_pages", 0)  # 0 = no delay for max speed
        
        # Age filtering
        self.max_age_days = input_data.get("max_age_days", 0)  # 0 = disabled
        self.consecutive_old_limit = 5
        
        # Proxy settings (Apify ProxyConfiguration)
        self.proxy_configuration = input_data.get("proxyConfiguration")
        
        # Output settings
        self.output_format = input_data.get("output_format", "detailed")
        
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            "direct_url": self.direct_url,
            "max_pages": self.max_pages,
            "limit_per_page": self.limit_per_page,
            "delay_between_pages": self.delay_between_pages,
            "max_age_days": self.max_age_days,
            "output_format": self.output_format
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
        "time": lbc.Sort.NEWEST,
        "price": lbc.Sort.CHEAPEST,
        "price_asc": lbc.Sort.EXPENSIVE,
        "price_desc": lbc.Sort.CHEAPEST,
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
                    if value in LeboncoinURLParser.SORT_MAP:
                        search_config['sort'] = LeboncoinURLParser.SORT_MAP[value]
                        
                elif key == "order":
                    # Handle sort order
                    if value == "desc":
                        if 'sort' in search_config and search_config['sort'] == lbc.Sort.EXPENSIVE:
                            search_config['sort'] = lbc.Sort.CHEAPEST
                    elif value == "asc":
                        if 'sort' in search_config and search_config['sort'] == lbc.Sort.CHEAPEST:
                            search_config['sort'] = lbc.Sort.EXPENSIVE
                            
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
            
            # Set default values
            search_config.setdefault('sort', lbc.Sort.NEWEST)
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
            # Handle formats like "Nanterre_92000__48.88822_2.19428_4049"
            if '__' in location_str:
                parts = location_str.split('__')
                city_part = parts[0]
                coords_part = parts[1] if len(parts) > 1 else ""
                
                # Extract city name
                city_parts = city_part.split('_')
                if len(city_parts) >= 2 and city_parts[-1].isdigit():
                    city_name = '_'.join(city_parts[:-1])
                else:
                    city_name = city_part
                
                # Extract coordinates
                coords_parts = coords_part.split('_')
                if len(coords_parts) >= 2:
                    lat = float(coords_parts[0])
                    lng = float(coords_parts[1])
                    radius = int(coords_parts[2]) if len(coords_parts) > 2 else 0
                    
                    return lbc.City(
                        lat=lat,
                        lng=lng,
                        radius=radius,
                        city=city_name
                    )
            
            # Handle simple format like "Nanterre_92000"
            else:
                city_parts = location_str.split('_')
                if len(city_parts) >= 2 and city_parts[-1].isdigit():
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
                
        except Exception as e:
            print(f"Error parsing location '{location_str}': {e}")
            return None
    
    @staticmethod
    def _get_city_coordinates(city_name: str, postal_code: str = "") -> Dict[str, float]:
        """Get coordinates for a city."""
        # Base coordinates for major French cities
        CITY_COORDINATES = {
            "paris": {"lat": 48.8566, "lng": 2.3522},
            "lyon": {"lat": 45.7640, "lng": 4.8357},
            "marseille": {"lat": 43.2965, "lng": 5.3698},
            "toulouse": {"lat": 43.6047, "lng": 1.4442},
            "nice": {"lat": 43.7102, "lng": 7.2620},
            "nantes": {"lat": 47.2184, "lng": -1.5536},
            "strasbourg": {"lat": 48.5734, "lng": 7.7521},
            "montpellier": {"lat": 43.6110, "lng": 3.8767},
            "bordeaux": {"lat": 44.8378, "lng": -0.5792},
            "lille": {"lat": 50.6292, "lng": 3.0573},
            "rennes": {"lat": 48.1173, "lng": -1.6778},
            "reims": {"lat": 49.2583, "lng": 4.0317},
            "saint_etienne": {"lat": 45.09, "lng": 4.39},
            "toulon": {"lat": 43.1242, "lng": 5.9280},
            "le_havre": {"lat": 49.4944, "lng": 0.1079},
            "grenoble": {"lat": 45.1885, "lng": 5.7245},
            "dijon": {"lat": 47.3220, "lng": 5.0415},
            "angers": {"lat": 47.4784, "lng": -0.5632},
            "nimes": {"lat": 43.8367, "lng": 4.3601},
            "villeurbanne": {"lat": 45.7667, "lng": 4.8833},
            "saint_denis": {"lat": 48.9361, "lng": 2.3574},
            "le_mans": {"lat": 48.0061, "lng": 0.1996},
            "aix_en_provence": {"lat": 43.5263, "lng": 5.4454},
            "clermont_ferrand": {"lat": 45.7772, "lng": 3.0870},
            "brest": {"lat": 48.3905, "lng": -4.4860},
            "tours": {"lat": 47.3941, "lng": 0.6848},
            "limoges": {"lat": 45.8336, "lng": 1.2611},
            "amiens": {"lat": 49.8943, "lng": 2.2958},
            "perpignan": {"lat": 42.6886, "lng": 2.8948},
            "metz": {"lat": 49.1193, "lng": 6.1757},
            "nanterre": {"lat": 48.8938, "lng": 2.2064},
            "boulogne_billancourt": {"lat": 48.8355, "lng": 2.2413},
            "orleans": {"lat": 47.9029, "lng": 1.9093},
            "mulhouse": {"lat": 47.7508, "lng": 7.3359},
            "rouen": {"lat": 49.4432, "lng": 1.0993},
            "caen": {"lat": 49.1829, "lng": -0.3707},
            "dunkerque": {"lat": 51.0343, "lng": 2.3768},
            "nancy": {"lat": 48.6921, "lng": 6.1844},
        }
        
        normalized_name = city_name.lower().replace(" ", "_").replace("-", "_")
        
        # Try exact match first
        if normalized_name in CITY_COORDINATES:
            return CITY_COORDINATES[normalized_name]
        
        # Try partial matches
        for city_key, coords in CITY_COORDINATES.items():
            if normalized_name in city_key or city_key in normalized_name:
                return coords
        
        # Default to Paris if not found
        return CITY_COORDINATES["paris"]
    
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
        self.seen_ids = set()
        self.stats = {
            "total_ads": 0,
            "unique_ads": 0,
            "duplicates": 0,
            "locations_processed": 0,
            "pages_processed": 0,
            "errors": 0
        }
    
    async def initialize_client(self) -> None:
        """Initialize Leboncoin client with optional Apify proxy."""
        proxy_url = None
        
        # Try to use Apify ProxyConfiguration
        if self.config.proxy_configuration:
            try:
                from apify import Actor
                proxy_config = await Actor.create_proxy_configuration(
                    actor_proxy_input=self.config.proxy_configuration
                )
                if proxy_config:
                    proxy_url = await proxy_config.new_url()
                    self.logger.info("Proxy configured successfully")
            except Exception as e:
                self.logger.error(f"Failed to configure proxy: {e}")
        
        # Initialize client with or without proxy
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
            self.client = lbc.Client(proxy=proxy)
            self.logger.info("Leboncoin client initialized with proxy")
        else:
            self.client = lbc.Client()
            self.logger.info("Leboncoin client initialized without proxy")
    
    
    def _scrape_single_page(self, page_num: int) -> tuple[List[Dict[str, Any]], bool]:
        """
        Scrape a single page using parsed search arguments.
        Returns (ads_list, should_stop).
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            Tuple of (list of ads, boolean indicating if scraping should stop)
        """
        try:
            # Use parsed search arguments instead of URL
            search_args = self.config.search_args.copy()
            search_args['page'] = page_num
            search_args['limit'] = self.config.limit_per_page
            
            result = self.client.search(**search_args)
            
            # Log info on first page only
            if page_num == 1 and hasattr(result, 'max_pages') and hasattr(result, 'total'):
                self.logger.info(f"Found {result.total} ads in {result.max_pages} pages")
            
            # Fast exit if no ads
            if not hasattr(result, 'ads') or not result.ads:
                return [], True
            
            page_ads = []
            old_ads_count = 0
            
            # Static search context (reused for all ads on this page)
            search_context = {"category": "URL", "location": "Direct URL"}
            
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
                if self.config.max_age_days > 0:
                    if hasattr(ad, 'first_publication_date') and ad.first_publication_date:
                        ad_age_days = (datetime.now() - ad.first_publication_date).days
                        if ad_age_days > self.config.max_age_days:
                            old_ads_count += 1
                            if old_ads_count >= self.config.consecutive_old_limit:
                                return page_ads, True
                            continue
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

    async def scrape_from_url(self) -> List[Dict[str, Any]]:
        """Scrape using search arguments (sequential, optimized for speed)."""
        all_ads = []
        
        max_pages = self.config.max_pages if self.config.max_pages > 0 else 100
        
        # Validate search arguments
        if not self.config.search_args:
            self.logger.error("No search arguments provided")
            self.stats["errors"] += 1
            return all_ads
        
        self.logger.info("Search arguments validated - will be passed directly to lbc library")

        # Sequential scraping - optimized batching
        page = 1
        batch_size = 10  # Larger batch for fewer I/O operations
        batch_ads = []
        
        self.logger.info("Starting scraping")
        
        while page <= max_pages:
            # Scrape page
            page_ads, should_stop = self._scrape_single_page(page)
            
            if page_ads:
                all_ads.extend(page_ads)
                batch_ads.extend(page_ads)
                self.stats["total_ads"] += len(page_ads)
                self.stats["unique_ads"] += len(page_ads)
                self.stats["pages_processed"] += 1
                # Log every 5 pages to reduce overhead
                if page % 5 == 1:
                    self.logger.info(f"Page {page}: {len(page_ads)} ads extracted")
            
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
        
        self.logger.info(f"Scraping completed: {len(all_ads)} ads from {self.stats['pages_processed']} pages")
        return all_ads
    
    async def run(self) -> Dict[str, Any]:
        """Execute scraping pipeline."""
        self.logger.info("Starting scraper")
        if self.config.direct_url:
            self.logger.info(f"URL: {self.config.direct_url}")
            # Log parsed search arguments
            if self.config.search_args:
                self.logger.info(f"Parsed search arguments: {self.config.search_args}")
        else:
            self.logger.info(f"Search args: {self.config.search_args}")
        self.logger.info(f"Max pages: {self.config.max_pages}, Delay: {self.config.delay_between_pages}s")
        
        # Initialize client
        await self.initialize_client()
        
        # Scrape using search arguments
        all_ads = await self.scrape_from_url()
        
        # Final summary
        self.logger.info(f"Completed: {self.stats['unique_ads']} ads, {self.stats['pages_processed']} pages")
        
        return {
            "stats": self.stats,
            "ads": all_ads,
            "config": self.config.to_dict()
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
            
            # Set output
            await Actor.set_value('OUTPUT', result)
            
    except ImportError:
        # Local execution fallback
        input_data = await ApifyAdapter.get_input()
        config = Config(input_data)
        logger = Logger.setup()
        
        engine = ScraperEngine(config, logger)
        result = await engine.run()
        
        # Save local output
        with open("scraper_results.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info("Results saved to: scraper_results.json")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

