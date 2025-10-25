"""
Generic URL Parser for Leboncoin Search URLs
Converts Leboncoin search URLs to search configuration dictionaries
Based on the actual lbc library parsing logic
"""

import lbc
from urllib.parse import unquote
from typing import Dict, Any, List, Optional, Union, Tuple


class LeboncoinURLParser:
    """Generic parser for Leboncoin search URLs to search configuration."""
    
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
                        category_id = int(value)
                        # Try to find the category in lbc.Category
                        for cat in lbc.Category:
                            if cat.value == str(category_id):
                                search_config['category'] = cat
                                break
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
    def _parse_price_range(price_str: str) -> Optional[Tuple[int, int]]:
        """Parse price range string to tuple."""
        try:
            if price_str.startswith('min-'):
                # Format: "min-1600"
                max_price = int(price_str.split('-')[1])
                return (0, max_price)
            elif price_str.endswith('-max'):
                # Format: "2020-max"
                min_price = int(price_str.split('-')[0])
                return (min_price, 99999999)
            elif '-' in price_str:
                # Format: "1000-2000"
                parts = price_str.split('-')
                min_price = int(parts[0])
                max_price = int(parts[1])
                return (min_price, max_price)
            else:
                # Single price
                price = int(price_str)
                return (price, price)
        except:
            return None
    
    @staticmethod
    def _parse_range(range_str: str) -> Optional[Tuple[int, int]]:
        """Parse range string to tuple."""
        try:
            if range_str.startswith('min-'):
                # Format: "min-1600"
                max_val = int(range_str.split('-')[1])
                return (0, max_val)
            elif range_str.endswith('-max'):
                # Format: "2020-max"
                min_val = int(range_str.split('-')[0])
                return (min_val, 9999999)
            elif '-' in range_str:
                # Format: "1000-2000"
                parts = range_str.split('-')
                min_val = int(parts[0])
                max_val = int(parts[1])
                return (min_val, max_val)
            else:
                # Single value
                val = int(range_str)
                return (val, val)
        except:
            return None
    
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
    
    @staticmethod
    def _serialize_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize config for JSON output."""
        serialized = {}
        for key, value in config.items():
            if hasattr(value, 'value'):
                # Enum object
                serialized[key] = str(value)
            elif hasattr(value, '__dict__'):
                # Custom object like City - convert to dict
                if hasattr(value, 'lat') and hasattr(value, 'lng'):
                    # City object
                    serialized[key] = {
                        "lat": value.lat,
                        "lng": value.lng,
                        "radius": value.radius,
                        "city": value.city
                    }
                else:
                    serialized[key] = str(value)
            elif isinstance(value, list):
                # List of objects
                serialized[key] = []
                for item in value:
                    if hasattr(item, '__dict__'):
                        if hasattr(item, 'lat') and hasattr(item, 'lng'):
                            # City object
                            serialized[key].append({
                                "lat": item.lat,
                                "lng": item.lng,
                                "radius": item.radius,
                                "city": item.city
                            })
                        else:
                            serialized[key].append(str(item))
                    else:
                        serialized[key].append(item)
            else:
                # Basic types
                serialized[key] = value
        return serialized


def parse_leboncoin_url(url: str) -> Dict[str, Any]:
    """
    Convenience function to parse a Leboncoin URL to search configuration.
    
    Args:
        url: Leboncoin search URL
        
    Returns:
        Dictionary containing search configuration compatible with lbc.Client.search()
    """
    return LeboncoinURLParser.parse_url_to_search_config(url)


if __name__ == "__main__":
    # Test the parser with example URLs
    test_urls = [
        "https://www.leboncoin.fr/recherche?category=2&locations=Lyon__45.76053450713997_4.835562580016857_7308_5000&price=500-max&regdate=2020-max&u_car_brand=ABARTH",
        "https://www.leboncoin.fr/recherche?category=10&locations=Nanterre_92000__48.88822_2.19428_0&price=min-1600&rooms=3-3&bedrooms=2-2&real_estate_type=2&owner_type=private&furnished=1"
    ]
    
    for url in test_urls:
        print(f"\nURL: {url}")
        config = parse_leboncoin_url(url)
        print(f"Config: {config}")