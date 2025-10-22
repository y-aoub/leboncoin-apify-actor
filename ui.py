"""
Leboncoin Scraper - Streamlit UI
Simple interface for PoC testing

Author: Advanced Scraping Solutions
"""

import streamlit as st
import json
import asyncio
from datetime import datetime
import lbc


# ============================================================================
# UI CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Leboncoin Scraper",
    page_icon="🔍",
    layout="wide"
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_categories():
    """Get all available categories from lbc library."""
    categories = {}
    for attr in dir(lbc.Category):
        if not attr.startswith('_'):
            try:
                cat = getattr(lbc.Category, attr)
                if hasattr(cat, 'value'):
                    categories[attr] = cat.value
            except:
                pass
    return categories


def get_all_departments():
    """Get all French departments."""
    departments = []
    for i in range(1, 96):
        if i == 20:
            departments.extend(["2A", "2B"])
        else:
            departments.append(str(i).zfill(2))
    return departments


def get_all_regions():
    """Get all available regions from lbc library."""
    regions = []
    for attr in dir(lbc.Region):
        if not attr.startswith('_') and attr.isupper():
            regions.append(attr)
    return regions


def run_scraper(config_data):
    """Run the scraper with given configuration."""
    try:
        from main import ScraperEngine, Config, Logger
        
        # Create config
        config = Config(config_data)
        logger = Logger.setup(verbose=True)
        
        # Run scraper
        engine = ScraperEngine(config, logger)
        result = asyncio.run(engine.run())
        
        return result
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# MAIN UI
# ============================================================================

st.title("🔍 Leboncoin Universal Scraper")
st.markdown("**Interface PoC - Configuration et lancement du scraping**")
st.markdown("---")

# Initialize session state
if 'scraping_results' not in st.session_state:
    st.session_state.scraping_results = None

# ============================================================================
# SIDEBAR - CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Category selection
    st.subheader("1. Catégorie")
    categories = get_all_categories()
    category_names = list(categories.keys())
    selected_category = st.selectbox(
        "Catégorie",
        options=category_names,
        index=category_names.index("TOUTES_CATEGORIES") if "TOUTES_CATEGORIES" in category_names else 0,
        help="Sélectionnez la catégorie d'annonces"
    )
    
    # Search text
    search_text = st.text_input(
        "Recherche textuelle",
        value="",
        help="Mots-clés à rechercher (optionnel)"
    )
    
    # Location type
    st.subheader("2. Localisation")
    location_type = st.radio(
        "Type de localisation",
        options=["Aucune (France entière)", "Département", "Région", "Ville"],
        help="Sélectionnez le type de localisation"
    )
    
    locations = []
    
    if location_type == "Département":
        departments = get_all_departments()
        selected_depts = st.multiselect(
            "Départements",
            options=departments,
            help="Sélectionnez un ou plusieurs départements"
        )
        locations = [{"code": dept} for dept in selected_depts]
        location_type_key = "department"
        
    elif location_type == "Région":
        regions = get_all_regions()
        selected_regions = st.multiselect(
            "Régions",
            options=regions,
            help="Sélectionnez une ou plusieurs régions"
        )
        locations = [{"name": region} for region in selected_regions]
        location_type_key = "region"
        
    elif location_type == "Ville":
        st.info("Configuration avancée ville")
        city_name = st.text_input("Nom de la ville", value="Paris")
        city_lat = st.number_input("Latitude", value=48.8566, format="%.6f")
        city_lng = st.number_input("Longitude", value=2.3522, format="%.6f")
        city_radius = st.number_input("Rayon (mètres)", value=10000, min_value=1000, step=1000)
        
        if st.button("Ajouter ville"):
            locations.append({
                "name": city_name,
                "lat": city_lat,
                "lng": city_lng,
                "radius": city_radius
            })
        location_type_key = "city"
    else:
        location_type_key = "none"
    
    # Filters
    st.subheader("3. Filtres")
    
    # Price range
    price_filter = st.checkbox("Filtrer par prix")
    price_min = None
    price_max = None
    if price_filter:
        col1, col2 = st.columns(2)
        with col1:
            price_min = st.number_input("Prix min (€)", value=0, min_value=0, step=100)
        with col2:
            price_max = st.number_input("Prix max (€)", value=100000, min_value=0, step=1000)
    
    # Sort
    sort_options = ["NEWEST", "RELEVANCE", "PRICE_ASC", "PRICE_DESC"]
    sort_type = st.selectbox(
        "Tri",
        options=sort_options,
        help="Ordre de tri des résultats"
    )
    
    # Ad type
    ad_type_options = ["OFFER", "DEMAND"]
    ad_type = st.selectbox(
        "Type d'annonce",
        options=ad_type_options,
        help="Type d'annonce à rechercher"
    )
    
    # Owner type
    owner_type_options = ["Tous", "PRIVATE", "PRO"]
    owner_type_selected = st.selectbox(
        "Type de vendeur",
        options=owner_type_options,
        help="Type de propriétaire"
    )
    owner_type = None if owner_type_selected == "Tous" else owner_type_selected
    
    # Search in title only
    search_in_title_only = st.checkbox(
        "Rechercher uniquement dans le titre",
        value=False
    )
    
    # Advanced filters
    st.subheader("4. Filtres avancés")
    
    with st.expander("Filtres personnalisés (JSON)"):
        st.info("Ajoutez des filtres spécifiques selon la catégorie (ex: square, rooms, etc.)")
        custom_filters = st.text_area(
            "Filtres JSON",
            value='{}',
            help="Format JSON: {\"square\": [100, 200], \"rooms\": [3, 5]}"
        )
        try:
            filters_dict = json.loads(custom_filters)
        except:
            filters_dict = {}
            st.error("Format JSON invalide")
    
    # Pagination
    st.subheader("5. Pagination")
    max_pages = st.number_input(
        "Pages max (0 = illimité)",
        value=10,
        min_value=0,
        step=1,
        help="Nombre maximum de pages à scraper (0 pour tout)"
    )
    
    delay_pages = st.slider(
        "Délai entre pages (s)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5
    )
    
    delay_locations = st.slider(
        "Délai entre localisations (s)",
        min_value=0.5,
        max_value=10.0,
        value=2.0,
        step=0.5
    )
    
    # Age filter
    st.subheader("6. Filtrage par âge")
    enable_age_filter = st.checkbox("Activer le filtrage par âge")
    max_age_days = 0
    if enable_age_filter:
        max_age_days = st.number_input(
            "Âge max (jours)",
            value=7.0,
            min_value=0.1,
            step=0.5,
            format="%.1f",
            help="Annonces plus anciennes seront ignorées"
        )
    
    # Proxy
    st.subheader("7. Proxy (optionnel)")
    use_proxy = st.checkbox("Utiliser un proxy")
    proxy_host = None
    proxy_port = None
    proxy_username = None
    proxy_password = None
    
    if use_proxy:
        proxy_host = st.text_input("Host", value="")
        proxy_port = st.number_input("Port", value=8080, min_value=1, max_value=65535)
        proxy_username = st.text_input("Username (optionnel)", value="")
        proxy_password = st.text_input("Password (optionnel)", value="", type="password")
    
    # Output format
    st.subheader("8. Format de sortie")
    output_format = st.radio(
        "Format",
        options=["detailed", "compact"],
        help="detailed = tous les champs, compact = champs essentiels"
    )


# ============================================================================
# MAIN AREA - CONFIGURATION PREVIEW & EXECUTION
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📋 Configuration actuelle")
    
    # Build config
    config_data = {
        "search_text": search_text,
        "category": selected_category,
        "sort": sort_type,
        "ad_type": ad_type,
        "owner_type": owner_type,
        "search_in_title_only": search_in_title_only,
        "location_type": location_type_key,
        "locations": locations,
        "filters": filters_dict,
        "price_min": price_min if price_filter else None,
        "price_max": price_max if price_filter else None,
        "max_pages": max_pages,
        "limit_per_page": 35,
        "delay_between_pages": delay_pages,
        "delay_between_locations": delay_locations,
        "max_age_days": max_age_days,
        "consecutive_old_limit": 5,
        "proxy_host": proxy_host if use_proxy else None,
        "proxy_port": proxy_port if use_proxy else None,
        "proxy_username": proxy_username if use_proxy else None,
        "proxy_password": proxy_password if use_proxy else None,
        "output_format": output_format,
        "verbose": True
    }
    
    # Display config
    st.json(config_data)
    
    # Export config
    if st.button("💾 Exporter configuration (apify_input.json)"):
        with open("apify_input.json", "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        st.success("✅ Configuration exportée vers apify_input.json")

with col2:
    st.header("🚀 Actions")
    
    if st.button("▶️ Lancer le scraping", type="primary", use_container_width=True):
        with st.spinner("Scraping en cours..."):
            result = run_scraper(config_data)
            st.session_state.scraping_results = result
    
    if st.button("🗑️ Effacer les résultats", use_container_width=True):
        st.session_state.scraping_results = None
        st.rerun()
    
    # Stats display
    if st.session_state.scraping_results and 'stats' in st.session_state.scraping_results:
        st.subheader("📊 Statistiques")
        stats = st.session_state.scraping_results['stats']
        st.metric("Annonces totales", stats.get('total_ads', 0))
        st.metric("Annonces uniques", stats.get('unique_ads', 0))
        st.metric("Duplicatas", stats.get('duplicates', 0))
        st.metric("Pages traitées", stats.get('pages_processed', 0))
        st.metric("Erreurs", stats.get('errors', 0))

# ============================================================================
# RESULTS DISPLAY
# ============================================================================

if st.session_state.scraping_results:
    st.markdown("---")
    st.header("📊 Résultats du scraping")
    
    if 'error' in st.session_state.scraping_results:
        st.error(f"❌ Erreur: {st.session_state.scraping_results['error']}")
    else:
        results = st.session_state.scraping_results
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📋 Aperçu", "📥 Export", "📊 Détails"])
        
        with tab1:
            if 'ads' in results and results['ads']:
                st.write(f"**{len(results['ads'])} annonces trouvées**")
                
                # Display first 10 ads
                for i, ad in enumerate(results['ads'][:10], 1):
                    with st.expander(f"{i}. {ad.get('subject', 'Sans titre')} - {ad.get('price', 'N/A')}€"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID:** {ad.get('id')}")
                            st.write(f"**Prix:** {ad.get('price')}€")
                            st.write(f"**Ville:** {ad.get('city', 'N/A')}")
                            st.write(f"**Code postal:** {ad.get('zipcode', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Date de publication:** {ad.get('first_publication_date', 'N/A')}")
                            st.write(f"**Dernière MAJ:** {ad.get('index_date', 'N/A')}")
                            st.write(f"**URL:** [{ad.get('url')}]({ad.get('url')})")
                        
                        if output_format == "detailed" and 'attributes' in ad:
                            st.write("**Attributs:**")
                            st.json(ad['attributes'])
                
                if len(results['ads']) > 10:
                    st.info(f"Affichage de 10/{len(results['ads'])} annonces. Utilisez l'export pour voir toutes les données.")
            else:
                st.warning("Aucune annonce trouvée")
        
        with tab2:
            if 'ads' in results and results['ads']:
                # Export JSON
                json_data = json.dumps(results['ads'], ensure_ascii=False, indent=2)
                st.download_button(
                    label="⬇️ Télécharger JSON",
                    data=json_data,
                    file_name=f"leboncoin_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                
                # Export CSV (simplified)
                try:
                    import pandas as pd
                    df = pd.json_normalize(results['ads'])
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Télécharger CSV",
                        data=csv_data,
                        file_name=f"leboncoin_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Impossible de générer le CSV: {e}")
            else:
                st.warning("Aucune donnée à exporter")
        
        with tab3:
            st.subheader("Détails du scraping")
            
            if 'stats' in results:
                stats = results['stats']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total ads", stats.get('total_ads', 0))
                    st.metric("✅ Unique ads", stats.get('unique_ads', 0))
                
                with col2:
                    st.metric("📄 Pages", stats.get('pages_processed', 0))
                    st.metric("📍 Locations", stats.get('locations_processed', 0))
                
                with col3:
                    st.metric("🔄 Duplicates", stats.get('duplicates', 0))
                    st.metric("❌ Errors", stats.get('errors', 0))
            
            if 'config' in results:
                st.subheader("Configuration utilisée")
                st.json(results['config'])

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Leboncoin Universal Scraper v1.0</strong></p>
    <p>Interface PoC pour test avant déploiement Apify</p>
</div>
""", unsafe_allow_html=True)

