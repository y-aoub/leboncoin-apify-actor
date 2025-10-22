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
        self.delay_between_pages = input_data.get("delay_between_pages", 1)
        
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
    """Advanced logging with Apify integration."""
    
    @staticmethod
    def setup(verbose: bool = True) -> logging.Logger:
        """Configure logger for Apify environment."""
        try:
            from apify import Actor
            logger = logging.getLogger("LeboncoinScraper")
            logger.setLevel(logging.INFO if verbose else logging.WARNING)
            if not logger.handlers:
                handler = logging.StreamHandler()
                handler.setFormatter(logging.Formatter('%(message)s'))
                logger.addHandler(handler)
            return logger
        except ImportError:
            logger = logging.getLogger("LeboncoinScraper")
            logger.setLevel(logging.INFO if verbose else logging.WARNING)
            logger.handlers.clear()
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO if verbose else logging.WARNING)
            formatter = logging.Formatter('[%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
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


# ============================================================================
# AD TRANSFORMER
# ============================================================================

class AdTransformer:
    """Transform raw ads to structured format."""
    
    @staticmethod
    def create_detailed_ad(ad: Any, search_context: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed ad dictionary with all available fields."""
        location = ad.location if hasattr(ad, 'location') else None
        user = ad.user if hasattr(ad, 'user') else None
        
        # Extract all attributes
        attributes = DataProcessor.extract_all_attributes(
            ad.attributes if hasattr(ad, 'attributes') else []
        )
        
        # Filter attributes to remove technical/internal/redundant fields
        excluded_attributes = {
            # Technical/internal fields
            'rating_score', 'rating_count', 'profile_picture_url',
            'estimated_parcel_weight', 'estimated_parcel_size',
            'is_bundleable', 'purchase_cta_visible', 'negotiation_cta_visible',
            'country_isocode3166', 'is_import', 'payment_methods',
            
            # Redundant fields (duplicates with "u_" prefix)
            'u_car_brand', 'u_car_model', 'u_car_version',
            
            # Activity/Store technical fields
            'activity_sector', 'store_logo', 'store_name', 'online_store_id',
            'custom_ref', 'has_visibility_option',
            
            # Argus/pricing technical fields
            'old_price', 'car_price_min', 'car_price_max', 'car_price_positioning',
            'argus_object_id', 'monthly_payment_price',
            
            # Other technical fields
            'licence_plate_available', 'spare_parts_availability',
            'recent_used_vehicle', 'vehicle_vsp'
        }
        
        filtered_attributes = {
            k: v for k, v in attributes.items()
            if k not in excluded_attributes
        }
        
        # Base data (flattened - single level depth)
        ad_data = {
            # IDs and basic info
            "id": ad.id if hasattr(ad, 'id') else None,
            "url": ad.url if hasattr(ad, 'url') else None,
            "title": ad.title if hasattr(ad, 'title') else None,
            "subject": ad.subject if hasattr(ad, 'subject') else None,
            "body": ad.body if hasattr(ad, 'body') else None,
            
            # Category
            "category_id": ad.category_id if hasattr(ad, 'category_id') else None,
            "category_name": ad.category_name if hasattr(ad, 'category_name') else None,
            
            # Price
            "price": ad.price if hasattr(ad, 'price') else None,
            
            # Status and type
            "ad_type": ad.ad_type if hasattr(ad, 'ad_type') else None,
            "status": ad.status if hasattr(ad, 'status') else None,
            
            # Dates
            "first_publication_date": DataProcessor.normalize_datetime(
                ad.first_publication_date if hasattr(ad, 'first_publication_date') else None
            ),
            "index_date": DataProcessor.normalize_datetime(
                ad.index_date if hasattr(ad, 'index_date') else None
            ),
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            
            # Contact info
            "has_phone": ad.has_phone if hasattr(ad, 'has_phone') else None,
            
            # Location
            "city": location.city if location else None,
            "zipcode": location.zipcode if location else None,
            "department_id": location.department_id if location else None,
            "department_name": location.department_name if location else None,
            "region_name": location.region_name if location else None,
            "latitude": location.lat if location else None,
            "longitude": location.lng if location else None,
            
            # Images (as comma-separated string or keep as list)
            "images": ad.images if hasattr(ad, 'images') and ad.images else [],
            "image_count": len(ad.images) if hasattr(ad, 'images') and ad.images else 0,
            
            # User/Seller info (flattened with user_ prefix)
            "user_id": user.id if user and hasattr(user, 'id') else None,
            "user_name": user.name if user and hasattr(user, 'name') else None,
            "user_is_pro": user.is_pro if user and hasattr(user, 'is_pro') else None,
            "user_registered_at": DataProcessor.normalize_datetime(
                user.registered_at if user and hasattr(user, 'registered_at') else None
            ),
            "user_total_ads": user.total_ads if user and hasattr(user, 'total_ads') else None,
            
            # Search context
            "search_category": search_context.get("category"),
            "search_location": search_context.get("location"),
        }
        
        # Add flattened attributes with attribute_ prefix
        for key, value in filtered_attributes.items():
            ad_data[f"attribute_{key}"] = value
        
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
                    self.logger.info(f"Proxy configured successfully")
            except Exception as e:
                self.logger.warning(f"Failed to configure proxy: {e}")
        
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
                    self.logger.info(f"Found {total_results} total ads across {total_pages or '?'} pages")

                # Collect ads for this page
                page_ads = 0
                had_any = False
                for ad in ads_iter:
                    try:
                        had_any = True
                        # Skip if ad is not a proper object
                        if not hasattr(ad, 'id') or isinstance(ad, str):
                            self.logger.warning(f"Skipping invalid ad object of type: {type(ad)}")
                            continue
                        
                        # Create ad data
                        if self.config.output_format == "detailed":
                            ad_data = AdTransformer.create_detailed_ad(ad, search_context)
                        else:
                            ad_data = AdTransformer.create_compact_ad(ad, search_context)
                        
                        # Check for duplicates
                        ad_id = ad_data.get("id")
                        if ad_id in self.seen_ids:
                            self.stats["duplicates"] += 1
                            continue
                        
                        # Check age filter
                        if DataProcessor.is_ad_too_old(
                            ad_data.get("index_date"),
                            self.config.max_age_days
                        ):
                            old_ads_count += 1
                            if old_ads_count >= self.config.consecutive_old_limit:
                                self.logger.info(f"Age cutoff reached after {old_ads_count} consecutive old ads")
                                return all_ads
                        else:
                            old_ads_count = 0
                        
                        # Add ad
                        self.seen_ids.add(ad_id)
                        all_ads.append(ad_data)
                        page_ads += 1
                        self.stats["total_ads"] += 1
                        self.stats["unique_ads"] += 1
                        
                        # Push to Apify dataset
                        await ApifyAdapter.push_data(ad_data)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing ad: {e}")
                        self.stats["errors"] += 1
                        continue
                
                if not had_any:
                    self.logger.info(f"No more ads found on page {page}")
                    break

                self.logger.info(f"Extracted {page_ads} unique ads from page {page}")
                self.stats["pages_processed"] += 1
                
                # Check pagination limits
                if self.config.max_pages > 0 and page >= self.config.max_pages:
                    self.logger.info(f"Max pages limit reached ({self.config.max_pages})")
                    break
                
                if total_pages and page >= total_pages:
                    self.logger.info(f"Reached last page")
                    break
                
                page += 1
                await asyncio.sleep(self.config.delay_between_pages)
                
            except Exception as e:
                self.logger.error(f"Error fetching page {page}: {e}")
                self.stats["errors"] += 1
                break
        
        self.logger.info(f"Completed location {location_name}: {len(all_ads)} ads extracted")
        return all_ads
    
    async def scrape_from_url(self) -> List[Dict[str, Any]]:
        """Scrape from a direct Leboncoin URL."""
        all_ads = []
        page = 1
        
        max_pages = self.config.max_pages if self.config.max_pages > 0 else 100
        
        # Validate URL: only support /recherche URLs, not category pages
        try:
            from urllib.parse import urlparse
            parsed = urlparse(self.config.direct_url)
            if not parsed.scheme.startswith("http"):
                raise ValueError("URL invalide: doit commencer par http/https")
            if not parsed.netloc.endswith("leboncoin.fr"):
                raise ValueError("URL invalide: domaine non supporté (leboncoin.fr attendu)")
            if "/recherche" not in parsed.path:
                raise ValueError("URL non supportée: utilisez une URL de recherche (contenant /recherche)")
        except Exception as e:
            self.logger.error(f"Direct URL validation error: {e}")
            self.stats["errors"] += 1
            return all_ads

        while page <= max_pages:
            self.logger.info(f"Scraping page {page} from URL")
            
            try:
                # Scrape using URL
                result = self.client.search(url=self.config.direct_url, limit=self.config.limit_per_page, page=page)
                
                # Normalize iterator result
                ads_iter = getattr(result, 'ads', None)
                if ads_iter is None:
                    ads_iter = result
                
                page_ads = 0
                old_ads_count = 0
                had_any = False
                
                for ad in ads_iter:
                    try:
                        had_any = True
                        # Validate ad
                        if not hasattr(ad, 'id') or not ad.id:
                            continue
                        
                        ad_id = ad.id
                        
                        # Skip duplicates
                        if ad_id in self.seen_ids:
                            continue
                        
                        # Check age filter
                        if self.config.max_age_days > 0:
                            if hasattr(ad, 'first_publication_date') and ad.first_publication_date:
                                ad_age_days = (datetime.now() - ad.first_publication_date).days
                                if ad_age_days > self.config.max_age_days:
                                    old_ads_count += 1
                                    if old_ads_count >= self.config.consecutive_old_limit:
                                        self.logger.info(f"Age cutoff reached")
                                        return all_ads
                                    continue
                                else:
                                    old_ads_count = 0
                        
                        # Transform ad
                        ad_data = AdTransformer.create_detailed_ad(ad, {"category": "URL", "location": "Direct URL"})
                        
                        # Add ad
                        self.seen_ids.add(ad_id)
                        all_ads.append(ad_data)
                        page_ads += 1
                        self.stats["total_ads"] += 1
                        self.stats["unique_ads"] += 1
                        
                        # Push to Apify dataset
                        await ApifyAdapter.push_data(ad_data)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing ad: {e}")
                        self.stats["errors"] += 1
                        continue
                
                if not had_any:
                    self.logger.info("No more ads found")
                    break
                
                self.logger.info(f"Extracted {page_ads} ads from page {page}")
                self.stats["pages_processed"] += 1
                
                # Stop if no more ads
                if page_ads == 0:
                    self.logger.info("No more ads found")
                    break
                
                # Check pagination limits
                if page >= max_pages:
                    self.logger.info(f"Max pages limit reached ({max_pages})")
                    break
                
                page += 1
                await asyncio.sleep(self.config.delay_between_pages)
                
            except StopIteration:
                self.logger.info("Reached end of results")
                break
            except Exception as e:
                self.logger.error(f"Error on page {page}: {e}")
                self.stats["errors"] += 1
                break
        
        self.logger.info(f"Completed URL scraping: {len(all_ads)} ads extracted")
        return all_ads
    
    async def run(self) -> Dict[str, Any]:
        """Execute URL scraping pipeline."""
        self.logger.info("Starting Leboncoin URL scraper")
        
        # Log configuration
        config_summary = self.config.to_dict()
        self.logger.info(f"URL: {self.config.direct_url}")
        self.logger.info(f"Max pages: {self.config.max_pages}")
        
        # Initialize client
        await self.initialize_client()
        
        # Scrape from URL
        all_ads = await self.scrape_from_url()
        
        # Final summary
        self.logger.info("Scraping completed successfully")
        self.logger.info(f"Final statistics: {self.stats}")
        
        return {
            "stats": self.stats,
            "ads": all_ads,
            "config": config_summary
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

