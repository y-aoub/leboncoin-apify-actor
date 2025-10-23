"""
Leboncoin Universal Scraper - Production Ready
Supports all categories, locations, and filters
Optimized for Apify deployment

Author: Advanced Scraping Solutions
"""

import lbc
import json
import logging
import time
import os
import asyncio
from dataclasses import fields, is_dataclass
from typing import Any, Optional, Dict, List, Union
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
        # URL scraping (only mode)
        self.direct_url = input_data.get("direct_url", "").strip()
        
        # Pagination
        self.max_pages = input_data.get("max_pages", 10)
        self.limit_per_page = 35
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
# CATEGORY & ENUM UTILITIES (kept for compatibility)
# ============================================================================

class EnumMapper:
    """Map string inputs to lbc enums."""
    
    @staticmethod
    def get_category(category_str: str) -> Any:
        """Convert category string to lbc.Category enum."""
        try:
            return getattr(lbc.Category, category_str.upper())
        except AttributeError:
            return lbc.Category.TOUTES_CATEGORIES
    
    @staticmethod
    def get_sort(sort_str: str) -> Any:
        """Convert sort string to lbc.Sort enum."""
        try:
            return getattr(lbc.Sort, sort_str.upper())
        except AttributeError:
            return lbc.Sort.NEWEST
    
    @staticmethod
    def get_ad_type(ad_type_str: str) -> Any:
        """Convert ad type string to lbc.AdType enum."""
        try:
            return getattr(lbc.AdType, ad_type_str.upper())
        except AttributeError:
            return lbc.AdType.OFFER
    
    @staticmethod
    def get_owner_type(owner_type_str: Optional[str]) -> Optional[Any]:
        """Convert owner type string to lbc.OwnerType enum."""
        if not owner_type_str:
            return None
        try:
            return getattr(lbc.OwnerType, owner_type_str.upper())
        except AttributeError:
            return None


# ============================================================================
# DATA PROCESSING
# ============================================================================

class DataProcessor:
    """Process and transform ad data."""
    
    @staticmethod
    def serialize_to_dict(obj: Any) -> Any:
        """Recursively convert dataclass objects to dictionaries."""
        if is_dataclass(obj):
            result = {}
            for field in fields(obj):
                if field.name.startswith('_'):
                    continue
                value = getattr(obj, field.name)
                result[field.name] = DataProcessor.serialize_to_dict(value)
            return result
        elif isinstance(obj, list):
            return [DataProcessor.serialize_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: DataProcessor.serialize_to_dict(v) for k, v in obj.items()}
        else:
            return obj
    
    @staticmethod
    def extract_attribute_value(attributes: list, key: str) -> Optional[str]:
        """Extract attribute value by key."""
        for attr in attributes:
            if hasattr(attr, 'key') and attr.key == key:
                return attr.value
        return None
    
    @staticmethod
    def extract_all_attributes(attributes: list) -> Dict[str, str]:
        """Extract all attributes as dictionary."""
        result = {}
        for attr in attributes:
            if hasattr(attr, 'key') and hasattr(attr, 'value'):
                result[attr.key] = attr.value
        return result
    
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
    
    @staticmethod
    def create_compact_ad(ad: Any, search_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create compact ad dictionary with essential fields only."""
        location = ad.location if hasattr(ad, 'location') else None
        
        return {
            "id": ad.id if hasattr(ad, 'id') else None,
            "url": ad.url if hasattr(ad, 'url') else None,
            "subject": ad.subject if hasattr(ad, 'subject') else None,
            "price": ad.price if hasattr(ad, 'price') else None,
            "city": location.city if location else None,
            "zipcode": location.zipcode if location else None,
            "index_date": DataProcessor.normalize_datetime(
                ad.index_date if hasattr(ad, 'index_date') else None
            ),
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


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
        self._parsed_filters = {}  # Parsed URL filters
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
    
    def build_search_params(self, location: Any = None) -> Dict[str, Any]:
        """Build search parameters for API call."""
        # If location is a string (department format like "d_01"), build URL instead
        if isinstance(location, str):
            return None  # Signal to use URL-based search
        
        params = {
            "category": EnumMapper.get_category(self.config.category),
            "sort": EnumMapper.get_sort(self.config.sort),
            "ad_type": EnumMapper.get_ad_type(self.config.ad_type),
            "limit": self.config.limit_per_page,
            "search_in_title_only": self.config.search_in_title_only,
        }
        
        # Add text search
        if self.config.search_text:
            params["text"] = self.config.search_text
        
        # Add location (only for City or Region objects)
        if location:
            params["locations"] = [location]
        
        # Add owner type
        owner_type_str = self.config.owner_type
        if owner_type_str and owner_type_str != "all":
            owner_type = EnumMapper.get_owner_type(owner_type_str)
        if owner_type:
            params["owner_type"] = owner_type
        
        # Add price range
        if self.config.price_min is not None or self.config.price_max is not None:
            price_range = []
            if self.config.price_min is not None:
                price_range.append(self.config.price_min)
            if self.config.price_max is not None:
                if not price_range:
                    price_range.append(0)
                price_range.append(self.config.price_max)
            if len(price_range) == 2:
                params["price"] = price_range
        
        # Add custom filters
        params.update(self.config.filters)
        
        return params
    
    def build_search_url(self, location: str) -> str:
        """Build search URL for department-based search."""
        # Get category ID
        category = EnumMapper.get_category(self.config.category)
        category_id = category.value if hasattr(category, 'value') else "0"
        
        # Base URL
        url_parts = [f"https://www.leboncoin.fr/recherche?category={category_id}"]
        
        # Add location
        url_parts.append(f"locations={location}")
        
        # Add text search
        if self.config.search_text:
            url_parts.append(f"text={self.config.search_text}")
        
        # Add price
        if self.config.price_min is not None or self.config.price_max is not None:
            price_min = self.config.price_min or 0
            price_max = self.config.price_max or "max"
            url_parts.append(f"price={price_min}-{price_max}")
        
        # Add custom filters as URL parameters
        for key, value in self.config.filters.items():
            if isinstance(value, list):
                if all(isinstance(v, (int, float)) for v in value) and len(value) == 2:
                    # Range filter
                    url_parts.append(f"{key}={value[0]}-{value[1]}")
                else:
                    # List filter
                    url_parts.append(f"{key}={','.join(str(v) for v in value)}")
            else:
                url_parts.append(f"{key}={value}")
        
        return "&".join(url_parts)
    
    async def scrape_location(self, location: Any, location_name: str) -> List[Dict[str, Any]]:
        """Scrape all ads for a specific location."""
        self.logger.info(f"Starting scrape for location: {location_name}")
        
        # Determine if we need URL-based search (for departments) or params-based
        search_params = self.build_search_params(location)
        use_url = (search_params is None)  # URL is needed for departments
        
        if use_url and isinstance(location, str):
            search_url = self.build_search_url(location)
            self.logger.info(f"Using URL-based search for department")
        
        search_context = {
            "category": self.config.category,
            "location": location_name
        }
        
        all_ads = []
        page = 1
        total_pages = None
        old_ads_count = 0
        
        while True:
            try:
                self.logger.info(f"Fetching page {page}{f'/{total_pages}' if total_pages else ''}")
                
                # Search using URL or params
                if use_url:
                    result = self.client.search(url=search_url, page=page, limit=self.config.limit_per_page)
                else:
                    result = self.client.search(**search_params, page=page)
                
                # Normalize iterator result
                ads_iter = getattr(result, 'ads', None)
                if ads_iter is None:
                    # Some versions return an iterator directly
                    ads_iter = result
                
                if page == 1:
                    total_pages = getattr(result, 'max_pages', None)
                    total_results = getattr(result, 'total', None) or 0
                    self.logger.info(f"Found {total_results} ads across {total_pages or '?'} pages")

                # Collect ads for this page
                page_ads = 0
                had_any = False
                for ad in ads_iter:
                    had_any = True
                    # Fast validation
                    if not hasattr(ad, 'id') or isinstance(ad, str):
                        continue
                    
                    # Create ad data
                    if self.config.output_format == "detailed":
                        ad_data = AdTransformer.create_detailed_ad(ad, search_context)
                    else:
                        ad_data = AdTransformer.create_compact_ad(ad, search_context)
                    
                    # Check duplicates
                    ad_id = ad_data.get("id")
                    if ad_id in self.seen_ids:
                        self.stats["duplicates"] += 1
                        continue
                    
                    # Age filter
                    if DataProcessor.is_ad_too_old(
                        ad_data.get("index_date"),
                        self.config.max_age_days
                    ):
                        old_ads_count += 1
                        if old_ads_count >= self.config.consecutive_old_limit:
                            self.logger.info(f"Age cutoff reached")
                            return all_ads
                    else:
                        old_ads_count = 0
                    
                    # Add ad
                    try:
                        self.seen_ids.add(ad_id)
                        all_ads.append(ad_data)
                        page_ads += 1
                        self.stats["total_ads"] += 1
                        self.stats["unique_ads"] += 1
                        
                        # Push to Apify dataset
                        await ApifyAdapter.push_data(ad_data)
                    except Exception:
                        self.stats["errors"] += 1
                
                if not had_any:
                    break

                # Log every 5 pages to reduce overhead
                if page % 5 == 1:
                    self.logger.info(f"Page {page}: {page_ads} ads extracted")
                self.stats["pages_processed"] += 1
                
                # Check pagination limits
                if self.config.max_pages > 0 and page >= self.config.max_pages:
                    self.logger.info(f"Max pages limit reached ({self.config.max_pages})")
                    break
                
                if total_pages and page >= total_pages:
                    self.logger.info(f"Reached last page")
                    break
                
                page += 1
                # Only sleep if delay configured
                if self.config.delay_between_pages > 0:
                    await asyncio.sleep(self.config.delay_between_pages)
                
            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {e}")
                self.stats["errors"] += 1
                break
        
        self.logger.info(f"Completed location {location_name}: {len(all_ads)} ads extracted")
        return all_ads
    
    def _scrape_single_page(self, page_num: int) -> tuple[List[Dict[str, Any]], bool]:
        """
        Scrape a single page sequentially (optimized for speed).
        Returns (ads_list, should_stop).
        
        Args:
            page_num: Page number to scrape
            
        Returns:
            Tuple of (list of ads, boolean indicating if scraping should stop)
        """
        try:
            # Use parsed filters for precise control
            result = self.client.search(
                **self._parsed_filters,
                page=page_num,
                limit=self.config.limit_per_page
            )
            
            # Log info on first page only
            if page_num == 1 and hasattr(result, 'max_pages') and hasattr(result, 'total'):
                self.logger.info(f"Found {result.total} ads in {result.max_pages} pages")
            
            # Fast exit if no ads
            if not result.ads:
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

    def _parse_url_filters(self, url: str) -> Dict[str, Any]:
        """
        Parse Leboncoin URL and extract all filters in lbc-compatible format.
        Universal parser that works for ALL categories.
        """
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        filters = {}
        
        # Known range parameters (convert "min-max" to [min, max])
        RANGE_PARAMS = {
            # Immobilier
            'price', 'square', 'land_plot', 'rooms', 'bedrooms',
            # Voitures / Véhicules
            'mileage', 'regdate', 'cubic_capacity', 'horse_power', 'seats', 'year',
            # Électronique / High-tech
            'screen_size', 'storage',
            # Général
            'energy_rate', 'gearbox', 'weight', 'size'
        }
        
        for key, value_list in query_params.items():
            # Skip pagination and tracking parameters
            if key in ['page', 'kst', 'from', 'utm_source', 'utm_medium', 'utm_campaign']:
                continue
            
            value = value_list[0] if len(value_list) == 1 else value_list
            
            try:
                # Category: integer ID
                if key == 'category':
                    filters['category'] = int(value)
                
                # Locations: parse format "City_Zipcode__lat_lng_radius"
                elif key == 'locations':
                    if isinstance(value, str) and '__' in value:
                        parts = value.split('__')
                        if len(parts) == 2:
                            # Parse city name (remove zipcode from the end)
                            city_parts = parts[0].rsplit('_', 1)
                            city_name = city_parts[0] if len(city_parts) > 1 else parts[0]
                            
                            # Parse coordinates
                            coords = parts[1].split('_')
                            if len(coords) >= 3:
                                lat = float(coords[0])
                                lng = float(coords[1])
                                radius = int(coords[2])
                                
                                # lbc.City only accepts: lat, lng, radius, city
                                location = lbc.City(
                                    lat=lat,
                                    lng=lng,
                                    radius=radius,
                                    city=city_name
                                )
                                filters['locations'] = [location]
                
                # Range parameters: convert "min-max" to [min, max]
                elif key in RANGE_PARAMS:
                    if isinstance(value, str) and '-' in value:
                        parts = value.split('-', 1)
                        if len(parts) == 2:
                            # Handle "min", "max", or numeric values
                            min_str = parts[0].strip().lower()
                            max_str = parts[1].strip().lower()
                            
                            # Convert to int, treating "min" as None/0 and "max" as None
                            if min_str in ['min', '']:
                                min_val = None
                            elif min_str.isdigit():
                                min_val = int(min_str)
                            else:
                                min_val = None
                            
                            if max_str in ['max', '']:
                                max_val = None
                            elif max_str.isdigit():
                                max_val = int(max_str)
                            else:
                                max_val = None
                            
                            # Build range list
                            if min_val is not None and max_val is not None:
                                filters[key] = [min_val, max_val]
                            elif min_val is not None:
                                filters[key] = [min_val]
                            elif max_val is not None:
                                filters[key] = [0, max_val]
                    elif isinstance(value, str) and value.isdigit():
                        # Single value
                        filters[key] = int(value)
                
                # Text search
                elif key == 'text':
                    filters['text'] = value
                
                # Boolean/enum-like parameters (pass as string or convert to int if numeric)
                elif key in ['ad_type', 'owner_type', 'sort']:
                    if isinstance(value, str) and value.isdigit():
                        filters[key] = int(value)
                    else:
                        filters[key] = value
                
                # Multi-value filters (e.g., real_estate_type=1,2,3 or fuel=essence,diesel)
                elif isinstance(value, str) and ',' in value:
                    # Split comma-separated values
                    values = value.split(',')
                    # Try to convert to integers, otherwise keep as strings
                    converted = []
                    for v in values:
                        v = v.strip()
                        if v.isdigit():
                            converted.append(int(v))
                        else:
                            converted.append(v)
                    filters[key] = converted
                
                # Boolean-like parameters (yes/no, true/false)
                elif isinstance(value, str) and value.lower() in ['yes', 'no', 'true', 'false', '0', '1']:
                    if value.lower() in ['yes', 'true', '1']:
                        filters[key] = True
                    elif value.lower() in ['no', 'false', '0']:
                        filters[key] = False
                
                # All other filters: pass as-is
                else:
                    # Try to convert to int if it's numeric
                    if isinstance(value, str) and value.isdigit():
                        filters[key] = int(value)
                    else:
                        # Keep as string
                        filters[key] = value
                        
            except (ValueError, IndexError, AttributeError) as e:
                # If parsing fails, log and skip this parameter
                self.logger.warning(f"Could not parse filter '{key}={value}': {e}")
                continue
        
        return filters
    
    async def scrape_from_url(self) -> List[Dict[str, Any]]:
        """Scrape from a direct Leboncoin URL (sequential, optimized for speed)."""
        all_ads = []
        
        max_pages = self.config.max_pages if self.config.max_pages > 0 else 100
        
        # Validate and parse URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.config.direct_url)
            
            if not parsed.scheme.startswith("http"):
                raise ValueError("URL invalide: doit commencer par http/https")
            if not parsed.netloc.endswith("leboncoin.fr"):
                raise ValueError("URL invalide: domaine non supporté (leboncoin.fr attendu)")
            if "/recherche" not in parsed.path:
                raise ValueError("URL non supportée: utilisez une URL de recherche (contenant /recherche)")
            
            # Parse all filters from URL
            self._parsed_filters = self._parse_url_filters(self.config.direct_url)
            filter_names = ', '.join(self._parsed_filters.keys()) if self._parsed_filters else 'none'
            self.logger.info(f"Parsed {len(self._parsed_filters)} filters: {filter_names}")
            
        except Exception as e:
            self.logger.error(f"URL validation/parsing failed: {e}")
            self.stats["errors"] += 1
            return all_ads

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
        """Execute URL scraping pipeline."""
        self.logger.info("Starting scraper")
        self.logger.info(f"URL: {self.config.direct_url}")
        self.logger.info(f"Max pages: {self.config.max_pages}, Delay: {self.config.delay_between_pages}s")
        
        # Initialize client
        await self.initialize_client()
        
        # Scrape from URL
        all_ads = await self.scrape_from_url()
        
        # Final summary
        self.logger.info(f"Completed: {self.stats['unique_ads']} ads, {self.stats['pages_processed']} pages")
        
        return {
            "stats": self.stats,
            "ads": all_ads,
            "config": self.config.to_dict()
        }
    
    def _get_location_name(self, location: Any, index: int) -> str:
        """Get readable name for location."""
        if location is None:
            return "Global"
        
        # Handle string locations (departments like "d_01")
        if isinstance(location, str):
            return f"Department {location}"
        
        if hasattr(location, 'city'):
            return location.city
        
        if hasattr(location, 'value'):
            return location.value[1] if isinstance(location.value, tuple) else str(location.value)
        
        return f"Location {index}"


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

