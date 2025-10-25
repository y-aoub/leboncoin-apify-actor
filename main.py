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
from dataclasses import fields, is_dataclass
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
            from url_parsing import parse_leboncoin_url
            self.search_args = parse_leboncoin_url(raw_url)
            
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

class URLParser:
    """Parse Le Bon Coin URLs and convert to search arguments."""
    
    # Category mapping from URL to lbc.Category (based on real fdata.json)
    CATEGORY_MAP = {
        # Toutes catégories
        "0": "ALL",
        
        # Emploi
        "71": "EMPLOI",
        "33": "EMPLOI",  # Offres d'emploi
        "74": "EMPLOI",  # Formations professionnelles
        
        # Véhicules
        "1": "VEHICULES",
        "2": "VEHICULES",  # Voitures
        "3": "VEHICULES",  # Motos
        "4": "VEHICULES",  # Caravaning
        "5": "VEHICULES",  # Utilitaires
        "300": "VEHICULES",  # Camions
        "7": "VEHICULES",  # Nautisme
        "6": "VEHICULES",  # Équipement auto
        "44": "VEHICULES",  # Équipement moto
        "50": "VEHICULES",  # Équipement caravaning
        "51": "VEHICULES",  # Équipement nautisme
        
        # Immobilier
        "8": "IMMOBILIER",
        "9": "IMMOBILIER",  # Ventes immobilières
        "2001": "IMMOBILIER",  # Immobilier Neuf
        "10": "IMMOBILIER",  # Locations
        "11": "IMMOBILIER",  # Colocations
        "13": "IMMOBILIER",  # Bureaux & Commerces
        
        # Locations de vacances
        "66": "VACANCES",
        "12": "VACANCES",  # Locations saisonnières
        
        # Électronique
        "14": "MULTIMEDIA",
        "15": "MULTIMEDIA",  # Ordinateurs
        "83": "MULTIMEDIA",  # Accessoires informatique
        "82": "MULTIMEDIA",  # Tablettes & Liseuses
        "16": "MULTIMEDIA",  # Photo, audio & vidéo
        "17": "MULTIMEDIA",  # Téléphones & Objets connectés
        "81": "MULTIMEDIA",  # Accessoires téléphone & Objets connectés
        "43": "MULTIMEDIA",  # Consoles
        "84": "MULTIMEDIA",  # Jeux vidéo
        
        # Maison & Jardin
        "18": "MAISON",
        "19": "MAISON",  # Ameublement
        "96": "MAISON",  # Papeterie & Fournitures scolaires
        "20": "MAISON",  # Électroménager
        "45": "MAISON",  # Arts de la table
        "39": "MAISON",  # Décoration
        "46": "MAISON",  # Linge de maison
        "21": "MAISON",  # Bricolage
        "52": "MAISON",  # Jardin & Plantes
        
        # Famille
        "79": "FAMILLE",
        "23": "FAMILLE",  # Équipement bébé
        "80": "FAMILLE",  # Mobilier enfant
        "54": "FAMILLE",  # Vêtements bébé
        
        # Mode
        "72": "MODE",
        "22": "MODE",  # Vêtements
        "53": "MODE",  # Chaussures
        "47": "MODE",  # Accessoires & Bagagerie
        "42": "MODE",  # Montres & Bijoux
        
        # Loisirs
        "24": "LOISIRS",
        "89": "LOISIRS",  # Antiquités
        "40": "LOISIRS",  # Collection
        "26": "LOISIRS",  # CD - Musique
        "25": "LOISIRS",  # DVD - Films
        "30": "LOISIRS",  # Instruments de musique
        "27": "LOISIRS",  # Livres
        "86": "LOISIRS",  # Modélisme
        "48": "LOISIRS",  # Vins & Gastronomie
        "41": "LOISIRS",  # Jeux & Jouets
        "88": "LOISIRS",  # Loisirs créatifs
        "29": "LOISIRS",  # Sport & Plein air
        "55": "LOISIRS",  # Vélos
        "85": "LOISIRS",  # Équipements vélos
        "1002": "LOISIRS",  # Vélos (autre ID)
        "1003": "LOISIRS",  # Équipements vélos (autre ID)
        
        # Animaux
        "75": "ANIMAUX",
        "28": "ANIMAUX",  # Animaux
        "76": "ANIMAUX",  # Accessoires animaux
        "77": "ANIMAUX",  # Animaux perdus
        
        # Matériel professionnel
        "56": "MATERIEL_PROFESSIONNEL",
        "105": "MATERIEL_PROFESSIONNEL",  # Tracteurs
        "57": "MATERIEL_PROFESSIONNEL",  # Matériel agricole
        "59": "MATERIEL_PROFESSIONNEL",  # BTP - Chantier gros-oeuvre
        "106": "MATERIEL_PROFESSIONNEL",  # Poids lourds
        "58": "MATERIEL_PROFESSIONNEL",  # Manutention - Levage
        "32": "MATERIEL_PROFESSIONNEL",  # Équipements industriels
        "61": "MATERIEL_PROFESSIONNEL",  # Équipements pour restaurants & hôtels
        "62": "MATERIEL_PROFESSIONNEL",  # Équipements & Fournitures de bureau
        "63": "MATERIEL_PROFESSIONNEL",  # Équipements pour commerces & marchés
        "64": "MATERIEL_PROFESSIONNEL",  # Matériel médical
        
        # Services
        "31": "SERVICES",
        "101": "SERVICES",  # Artistes & Musiciens
        "100": "SERVICES",  # Baby-Sitting
        "35": "SERVICES",  # Billetterie
        "65": "SERVICES",  # Covoiturage
        "36": "SERVICES",  # Cours particuliers
        "103": "SERVICES",  # Entraide entre voisins
        "49": "SERVICES",  # Évènements
        "99": "SERVICES",  # Services à la personne
        "102": "SERVICES",  # Services aux animaux
        "92": "SERVICES",  # Services de déménagement
        "95": "SERVICES",  # Services de réparations électroniques
        "93": "SERVICES",  # Services de réparations mécaniques
        "97": "SERVICES",  # Services de jardinerie & bricolage
        "98": "SERVICES",  # Services évènementiels
        "34": "SERVICES",  # Autres services
        
        # Dons
        "1000": "DONS",
        
        # Divers
        "37": "DIVERS",
        "38": "DIVERS",  # Autres
        
        # Services spécialisés (mappés vers SERVICES)
        "1001": "SERVICES",  # Services de déménagement
        "1004": "SERVICES",  # Services de réparations mécaniques
        "1005": "SERVICES",  # Services de jardinerie & bricolage
        "1006": "MAISON",  # Électroménager
        "1007": "SERVICES",  # Services de réparations électroniques
        "1008": "SERVICES",  # Artistes & Musiciens
        "1009": "SERVICES",  # Billetterie
        "1010": "SERVICES",  # Services aux animaux
        "1011": "MODE",  # Vêtements enfants
        "1012": "MODE",  # Vêtements maternité
        "1013": "MODE",  # Chaussures enfants
        "1014": "MODE",  # Montres & bijoux enfants
        "1015": "MODE",  # Accessoires & bagagerie enfants
        "1016": "LOISIRS",  # Jeux & Jouets
        "1017": "SERVICES"  # Baby-Sitting
    }
    
    # Real estate type mapping to subcategories
    REAL_ESTATE_TYPE_MAP = {
        "1": "IMMOBILIER_LOCATIONS",
        "2": "IMMOBILIER_LOCATIONS",  # Houses for rent
        "3": "IMMOBILIER_BUREAUX_ET_COMMERCES",
        "4": "IMMOBILIER_COLOCATIONS",
        "5": "IMMOBILIER_IMMOBILIER_NEUF"
    }
    
    @staticmethod
    def parse_url_to_hybrid_args(url: str) -> tuple[str, list]:
        """Parse URL to extract locations and return (url_without_locations, [locations])."""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            locations = []
            
            # Parse locations only
            if 'locations' in params:
                location_str = params['locations'][0]
                location = URLParser.parse_location(location_str)
                if location:
                    locations = [location]
                
                # Remove locations from URL parameters
                del params['locations']
            
            # Rebuild URL without locations parameter
            new_query = urlencode(params, doseq=True)
            url_without_locations = urlunparse((
                parsed.scheme, 
                parsed.netloc, 
                parsed.path, 
                parsed.params, 
                new_query, 
                parsed.fragment
            ))
            
            return url_without_locations, locations
            
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return url, []
    
    @staticmethod
    def parse_url_to_search_args(url: str) -> dict:
        """Parse URL and convert to search arguments for client.search()."""
        from urllib.parse import urlparse, parse_qs
        
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            search_args = {}
            
            # Parse category
            if 'category' in params:
                category_id = params['category'][0]
                if category_id in URLParser.CATEGORY_MAP:
                    search_args['category'] = getattr(lbc.Category, URLParser.CATEGORY_MAP[category_id])
            
            # Parse locations
            if 'locations' in params:
                location_str = params['locations'][0]
                location = URLParser.parse_location(location_str)
                if location:
                    search_args['locations'] = [location]
            
            # Parse price range
            if 'price' in params:
                price_str = params['price'][0]
                price_range = URLParser.parse_price_range(price_str)
                if price_range:
                    search_args['price'] = price_range
            
            # Parse rooms
            if 'rooms' in params:
                rooms_str = params['rooms'][0]
                rooms_range = URLParser.parse_range(rooms_str)
                if rooms_range:
                    search_args['rooms'] = rooms_range
            
            # Parse bedrooms
            if 'bedrooms' in params:
                bedrooms_str = params['bedrooms'][0]
                bedrooms_range = URLParser.parse_range(bedrooms_str)
                if bedrooms_range:
                    search_args['bedrooms'] = bedrooms_range
            
            # Parse real estate type (use subcategory instead)
            if 'real_estate_type' in params:
                real_estate_type_id = params['real_estate_type'][0]
                if real_estate_type_id in URLParser.REAL_ESTATE_TYPE_MAP:
                    search_args['category'] = getattr(lbc.Category, URLParser.REAL_ESTATE_TYPE_MAP[real_estate_type_id])
            
            # Parse text search
            if 'text' in params:
                search_args['text'] = params['text'][0]
            
            # Parse owner type
            if 'owner_type' in params:
                owner_type_str = params['owner_type'][0]
                if owner_type_str == 'private':
                    search_args['owner_type'] = lbc.OwnerType.PRIVATE
                elif owner_type_str == 'pro':
                    search_args['owner_type'] = lbc.OwnerType.PRO
            
            # Default values
            search_args.setdefault('sort', lbc.Sort.NEWEST)
            search_args.setdefault('ad_type', lbc.AdType.OFFER)
            search_args.setdefault('limit', 35)
            
            return search_args
            
        except Exception as e:
            print(f"Error parsing URL: {e}")
            return {}
    
    @staticmethod
    def parse_location(location_str: str) -> lbc.City:
        """Parse location string to lbc.City object."""
        try:
            # Handle formats like "Nanterre_92000__48.88822_2.19428_4049" or "Nanterre_92000__48.88822_2.19428_0"
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
                    # Handle radius: preserve the exact radius value
                    if len(coords_parts) > 2:
                        radius = int(coords_parts[2])
                        # Keep the exact radius value, even if it's 0
                    else:
                        radius = 10000  # Default radius when missing
                    
                    return lbc.City(
                        lat=lat,
                        lng=lng,
                        radius=radius,
                        city=city_name
                    )
            
            # Handle simple format like "Nanterre_92000" (no coordinates, default radius = 0)
            else:
                city_name, postal_code = URLParser.extract_city_from_location(location_str)
                coords = URLTransformer.get_city_coordinates(city_name, postal_code)
                
                return lbc.City(
                    lat=coords['lat'],
                    lng=coords['lng'],
                    radius=0,  # Default radius = 0 when no coordinates provided
                    city=city_name
                )
                
        except Exception as e:
            print(f"Error parsing location: {e}")
            return None
    
    @staticmethod
    def extract_city_from_location(location: str) -> tuple[str, str]:
        """Extract city name and postal code from location string."""
        parts = location.split("_")
        if len(parts) >= 2:
            city_name = "_".join(parts[:-1])
            postal_code = parts[-1]
            return city_name, postal_code
        return location, ""
    
    @staticmethod
    def parse_price_range(price_str: str) -> list:
        """Parse price range string to list."""
        try:
            if price_str.startswith('min-'):
                # Format: "min-1600"
                max_price = int(price_str.split('-')[1])
                return [0, max_price]
            elif '-' in price_str:
                # Format: "1000-2000"
                parts = price_str.split('-')
                min_price = int(parts[0])
                max_price = int(parts[1])
                return [min_price, max_price]
            else:
                # Single price
                price = int(price_str)
                return [price, price]
        except:
            return None
    
    @staticmethod
    def parse_range(range_str: str) -> tuple:
        """Parse range string to tuple."""
        try:
            if '-' in range_str:
                parts = range_str.split('-')
                min_val = int(parts[0])
                max_val = int(parts[1])
                return (min_val, max_val)
            else:
                val = int(range_str)
                return (val, val)
        except:
            return None


# ============================================================================
# URL TRANSFORMER
# ============================================================================

class URLTransformer:
    """Transform Le Bon Coin URLs to the correct format with GPS coordinates."""
    
    # Base coordinates for major French cities
    CITY_COORDINATES = {
        "paris": {"lat": 48.8566, "lng": 2.3522, "postal": "75000"},
        "lyon": {"lat": 45.7640, "lng": 4.8357, "postal": "69000"},
        "marseille": {"lat": 43.2965, "lng": 5.3698, "postal": "13000"},
        "toulouse": {"lat": 43.6047, "lng": 1.4442, "postal": "31000"},
        "nice": {"lat": 43.7102, "lng": 7.2620, "postal": "06000"},
        "nantes": {"lat": 47.2184, "lng": -1.5536, "postal": "44000"},
        "strasbourg": {"lat": 48.5734, "lng": 7.7521, "postal": "67000"},
        "montpellier": {"lat": 43.6110, "lng": 3.8767, "postal": "34000"},
        "bordeaux": {"lat": 44.8378, "lng": -0.5792, "postal": "33000"},
        "lille": {"lat": 50.6292, "lng": 3.0573, "postal": "59000"},
        "rennes": {"lat": 48.1173, "lng": -1.6778, "postal": "35000"},
        "reims": {"lat": 49.2583, "lng": 4.0317, "postal": "51100"},
        "saint_etienne": {"lat": 45.09, "lng": 4.39, "postal": "42000"},
        "toulon": {"lat": 43.1242, "lng": 5.9280, "postal": "83000"},
        "le_havre": {"lat": 49.4944, "lng": 0.1079, "postal": "76600"},
        "grenoble": {"lat": 45.1885, "lng": 5.7245, "postal": "38000"},
        "dijon": {"lat": 47.3220, "lng": 5.0415, "postal": "21000"},
        "angers": {"lat": 47.4784, "lng": -0.5632, "postal": "49000"},
        "nimes": {"lat": 43.8367, "lng": 4.3601, "postal": "30000"},
        "villeurbanne": {"lat": 45.7667, "lng": 4.8833, "postal": "69100"},
        "saint_denis": {"lat": 48.9361, "lng": 2.3574, "postal": "93200"},
        "le_mans": {"lat": 48.0061, "lng": 0.1996, "postal": "72000"},
        "aix_en_provence": {"lat": 43.5263, "lng": 5.4454, "postal": "13100"},
        "clermont_ferrand": {"lat": 45.7772, "lng": 3.0870, "postal": "63000"},
        "brest": {"lat": 48.3905, "lng": -4.4860, "postal": "29200"},
        "tours": {"lat": 47.3941, "lng": 0.6848, "postal": "37000"},
        "limoges": {"lat": 45.8336, "lng": 1.2611, "postal": "87000"},
        "amiens": {"lat": 49.8943, "lng": 2.2958, "postal": "80000"},
        "perpignan": {"lat": 42.6886, "lng": 2.8948, "postal": "66000"},
        "metz": {"lat": 49.1193, "lng": 6.1757, "postal": "57000"},
        "nanterre": {"lat": 48.8938, "lng": 2.2064, "postal": "92000"},
        "boulogne_billancourt": {"lat": 48.8355, "lng": 2.2413, "postal": "92100"},
        "orleans": {"lat": 47.9029, "lng": 1.9093, "postal": "45000"},
        "mulhouse": {"lat": 47.7508, "lng": 7.3359, "postal": "68100"},
        "rouen": {"lat": 49.4432, "lng": 1.0993, "postal": "76000"},
        "caen": {"lat": 49.1829, "lng": -0.3707, "postal": "14000"},
        "dunkerque": {"lat": 51.0343, "lng": 2.3768, "postal": "59140"},
        "nancy": {"lat": 48.6921, "lng": 6.1844, "postal": "54000"},
        "saint_pierre": {"lat": 46.7753, "lng": -56.1773, "postal": "97500"},
        "reunion": {"lat": -21.1151, "lng": 55.5364, "postal": "97400"},
        "antilles": {"lat": 14.6415, "lng": -61.0242, "postal": "97200"},
        "nouvelle_caledonie": {"lat": -22.2758, "lng": 166.4581, "postal": "98800"},
        "polynesie": {"lat": -17.6797, "lng": -149.4068, "postal": "98700"},
    }
    
    @staticmethod
    def normalize_city_name(city_name: str) -> str:
        """Normalize city name for lookup."""
        return city_name.lower().replace(" ", "_").replace("-", "_")
    
    @staticmethod
    def extract_city_from_location(location: str) -> tuple[str, str]:
        """Extract city name and postal code from location string."""
        # Handle formats like "Nanterre_92000", "Paris_75000", etc.
        parts = location.split("_")
        if len(parts) >= 2:
            city_name = "_".join(parts[:-1])  # Everything except last part
            postal_code = parts[-1]  # Last part
            return city_name, postal_code
        return location, ""
    
    @staticmethod
    def get_city_coordinates(city_name: str, postal_code: str = "") -> dict:
        """Get coordinates for a city."""
        normalized_name = URLTransformer.normalize_city_name(city_name)
        
        # Try exact match first
        if normalized_name in URLTransformer.CITY_COORDINATES:
            return URLTransformer.CITY_COORDINATES[normalized_name]
        
        # Try partial matches
        for city_key, coords in URLTransformer.CITY_COORDINATES.items():
            if normalized_name in city_key or city_key in normalized_name:
                return coords
        
        # Default to Paris if not found
        return URLTransformer.CITY_COORDINATES["paris"]
    
    @staticmethod
    def transform_url(url: str) -> str:
        """Transform a Le Bon Coin URL to the correct format with all filters preserved."""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        
        try:
            # Parse URL
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Transform locations parameter
            if 'locations' in params:
                locations = params['locations'][0]
                
                # Normalize the location format
                normalized_location = URLTransformer.normalize_location_format(locations)
                
                # Update params with normalized location
                params['locations'] = [normalized_location]
                
                # Rebuild URL with all parameters preserved
                new_query = urlencode(params, doseq=True)
                new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
                
                return new_url
            
            return url
            
        except Exception as e:
            # If transformation fails, return original URL
            return url
    
    @staticmethod
    def normalize_location_format(location: str) -> str:
        """Normalize location format to the correct GPS format."""
        # Handle various formats:
        # 1. "Nanterre_92000" -> convert to GPS format
        # 2. "Nanterre_92000__48.88822_2.19428_4049" -> fix format but preserve GPS coordinates
        # 3. "Nanterre__48.88822_2.19428_92000_10000" -> already correct
        
        # Check if location already has GPS coordinates
        if '__' in location:
            parts = location.split('__')
            city_part = parts[0]
            coords_part = parts[1] if len(parts) > 1 else ""
            
            # Check if coords_part contains GPS coordinates (lat_lng format)
            coords_parts = coords_part.split('_')
            if len(coords_parts) >= 2:
                try:
                    # Try to parse as coordinates
                    lat = float(coords_parts[0])
                    lng = float(coords_parts[1])
                    
                    # If we have valid coordinates, preserve them
                    if -90 <= lat <= 90 and -180 <= lng <= 180:
                        # Extract city name from city_part
                        city_parts = city_part.split('_')
                        if len(city_parts) >= 2 and city_parts[-1].isdigit():
                            # Last part is postal code
                            city_name = '_'.join(city_parts[:-1])
                            postal_code = city_parts[-1]
                        else:
                            # No postal code in city part
                            city_name = city_part
                            postal_code = ""
                        
                        # Use existing coordinates, postal code, and radius if available
                        if len(coords_parts) >= 3:
                            # Try to use original radius
                            try:
                                radius = int(coords_parts[2])
                                # For the API lbc, we need to use the postal code from the original city part
                                # The format should be: City__lat_lng_postal_radius
                                normalized_location = f"{city_name}__{lat}_{lng}_{postal_code}_{radius}"
                            except ValueError:
                                normalized_location = f"{city_name}__{lat}_{lng}_{postal_code}_10000"
                        else:
                            normalized_location = f"{city_name}__{lat}_{lng}_{postal_code}_10000"
                        return normalized_location
                except ValueError:
                    pass  # Not valid coordinates, fall through to default handling
        
        # No valid GPS coordinates found, extract city and postal code
        if '__' in location:
            city_part = location.split('__')[0]
            city_name, postal_code = URLTransformer.extract_city_from_location(city_part)
        else:
            city_name, postal_code = URLTransformer.extract_city_from_location(location)
        
        # Get coordinates for the city
        coords = URLTransformer.get_city_coordinates(city_name, postal_code)
        
        # Build correct format: City__lat_lng_postal_radius
        normalized_location = f"{city_name}__{coords['lat']}_{coords['lng']}_{coords['postal']}_10000"
        
        return normalized_location


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

