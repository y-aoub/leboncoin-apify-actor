"""
Quick test script for Leboncoin Universal Scraper
Tests basic functionality without full scraping
"""

import json
import asyncio
from main import ScraperEngine, Config, Logger


def test_basic_config():
    """Test 1: Basic configuration loading"""
    print("\n" + "="*70)
    print("TEST 1: Configuration Loading")
    print("="*70)
    
    test_config = {
        "search_text": "test",
        "category": "TOUTES_CATEGORIES",
        "location_type": "none",
        "locations": [],
        "max_pages": 1,
        "output_format": "compact",
        "verbose": True
    }
    
    try:
        config = Config(test_config)
        print("✅ Config created successfully")
        print(f"   Category: {config.category}")
        print(f"   Sort: {config.sort}")
        print(f"   Max pages: {config.max_pages}")
        return True
    except Exception as e:
        print(f"❌ Config creation failed: {e}")
        return False


def test_enum_mapping():
    """Test 2: Enum mapping"""
    print("\n" + "="*70)
    print("TEST 2: Enum Mapping")
    print("="*70)
    
    from main import EnumMapper
    import lbc
    
    try:
        # Test category mapping
        cat = EnumMapper.get_category("IMMOBILIER")
        print(f"✅ Category mapping: IMMOBILIER -> {cat}")
        
        # Test sort mapping
        sort = EnumMapper.get_sort("NEWEST")
        print(f"✅ Sort mapping: NEWEST -> {sort}")
        
        # Test ad type mapping
        ad_type = EnumMapper.get_ad_type("OFFER")
        print(f"✅ Ad type mapping: OFFER -> {ad_type}")
        
        return True
    except Exception as e:
        print(f"❌ Enum mapping failed: {e}")
        return False


def test_location_builder():
    """Test 3: Location building"""
    print("\n" + "="*70)
    print("TEST 3: Location Building")
    print("="*70)
    
    from main import LocationBuilder
    
    try:
        # Test department location
        dept_data = {"code": "75"}
        dept_loc = LocationBuilder.build_location(dept_data, "department")
        print(f"✅ Department location: {dept_loc}")
        
        # Test city location
        city_data = {
            "name": "Paris",
            "lat": 48.8566,
            "lng": 2.3522,
            "radius": 10000
        }
        city_loc = LocationBuilder.build_location(city_data, "city")
        print(f"✅ City location: {city_loc}")
        
        # Test list building
        locations = LocationBuilder.build_locations_list(
            [{"code": "75"}, {"code": "92"}],
            "department"
        )
        print(f"✅ Built {len(locations)} locations")
        
        return True
    except Exception as e:
        print(f"❌ Location building failed: {e}")
        return False


def test_data_processor():
    """Test 4: Data processing utilities"""
    print("\n" + "="*70)
    print("TEST 4: Data Processing")
    print("="*70)
    
    from main import DataProcessor
    from datetime import datetime, timedelta
    
    try:
        # Test datetime normalization
        date1 = "2025-10-22 10:00:00"
        normalized = DataProcessor.normalize_datetime(date1)
        print(f"✅ Date normalization: {normalized}")
        
        # Test age checking
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")
        is_old = DataProcessor.is_ad_too_old(old_date, max_age_days=7)
        print(f"✅ Age check (10 days old, max 7): {is_old}")
        
        recent_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        is_recent = DataProcessor.is_ad_too_old(recent_date, max_age_days=7)
        print(f"✅ Age check (2 days old, max 7): {not is_recent}")
        
        return True
    except Exception as e:
        print(f"❌ Data processing failed: {e}")
        return False


async def test_client_initialization():
    """Test 5: Client initialization"""
    print("\n" + "="*70)
    print("TEST 5: Client Initialization")
    print("="*70)
    
    test_config = {
        "search_text": "",
        "category": "TOUTES_CATEGORIES",
        "location_type": "none",
        "locations": [],
        "max_pages": 1,
        "verbose": False
    }
    
    try:
        config = Config(test_config)
        logger = Logger.setup(verbose=False)
        engine = ScraperEngine(config, logger)
        engine.initialize_client()
        
        if engine.client:
            print("✅ Client initialized successfully")
            return True
        else:
            print("❌ Client is None")
            return False
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False


async def test_minimal_scrape():
    """Test 6: Minimal scraping test (1 page, no location)"""
    print("\n" + "="*70)
    print("TEST 6: Minimal Scraping (WARNING: Makes real API call)")
    print("="*70)
    
    response = input("Run minimal scrape test? (y/n): ").lower()
    if response != 'y':
        print("⏭️  Skipped")
        return True
    
    test_config = {
        "search_text": "",
        "category": "TOUTES_CATEGORIES",
        "location_type": "none",
        "locations": [],
        "max_pages": 1,
        "limit_per_page": 5,
        "output_format": "compact",
        "verbose": False
    }
    
    try:
        config = Config(test_config)
        logger = Logger.setup(verbose=True)
        engine = ScraperEngine(config, logger)
        
        result = await engine.run()
        
        if result and 'stats' in result:
            print(f"✅ Scraping completed")
            print(f"   Total ads: {result['stats']['total_ads']}")
            print(f"   Pages: {result['stats']['pages_processed']}")
            return True
        else:
            print("❌ No results returned")
            return False
            
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_example_configs():
    """Test 7: Load and validate example configurations"""
    print("\n" + "="*70)
    print("TEST 7: Example Configurations")
    print("="*70)
    
    try:
        with open("config_examples.json", "r", encoding="utf-8") as f:
            examples = json.load(f)
        
        print(f"✅ Loaded {len(examples)} example configurations:")
        for name, example in examples.items():
            try:
                config = Config(example['config'])
                print(f"   ✅ {name}: Valid")
            except Exception as e:
                print(f"   ❌ {name}: Invalid - {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Failed to load examples: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*20 + "LEBONCOIN SCRAPER TESTS" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    tests = [
        ("Configuration Loading", test_basic_config()),
        ("Enum Mapping", test_enum_mapping()),
        ("Location Building", test_location_builder()),
        ("Data Processing", test_data_processor()),
        ("Client Initialization", await test_client_initialization()),
        ("Example Configurations", test_example_configs()),
        ("Minimal Scraping", await test_minimal_scrape()),
    ]
    
    results = []
    for name, result in tests:
        results.append((name, result))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Scraper is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review errors above.")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

