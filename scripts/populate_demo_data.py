"""
Script to populate the database with demo products
Run this script to add sample products for testing
"""
import requests
import json
from datetime import datetime

# Service URLs
PARSER_URL = "http://localhost:8001"
NLP_URL = "http://localhost:8002"
LCA_URL = "http://localhost:8003"
SCORING_URL = "http://localhost:8004"
WIDGET_URL = "http://localhost:8005"

# Demo products data
DEMO_PRODUCTS = [
    {
        "name": "Nutella Pâte à Tartiner",
        "brand": "Ferrero",
        "gtin": "3017620422003",
        "ingredients_text": "Sucre, huile de palme, noisettes 13%, cacao maigre 7.4%, lait écrémé en poudre 6.6%, lactosérum en poudre, émulsifiants (lécithine de soja), vanilline",
        "packaging": "pot en verre, couvercle plastique",
        "origin": "France",
        "weight_kg": 0.4
    },
    {
        "name": "Pâtes Barilla Spaghetti",
        "brand": "Barilla",
        "gtin": "8076809513005",
        "ingredients_text": "Semoule de blé dur de qualité supérieure, eau",
        "packaging": "carton recyclable",
        "origin": "Italie",
        "weight_kg": 0.5
    },
    {
        "name": "Lait Demi-Écrémé Bio",
        "brand": "Lactel",
        "gtin": "3250391806058",
        "ingredients_text": "Lait demi-écrémé pasteurisé",
        "packaging": "brique carton TetraPak",
        "origin": "France",
        "weight_kg": 1.0
    },
    {
        "name": "Pommes Golden Bio",
        "brand": "Vergers de France",
        "gtin": "3760123456789",
        "ingredients_text": "Pommes Golden issues de l'agriculture biologique",
        "packaging": "filet plastique",
        "origin": "France, Normandie",
        "weight_kg": 1.5
    },
    {
        "name": "Café Arabica Éthiopie",
        "brand": "Malongo",
        "gtin": "3104030007404",
        "ingredients_text": "Café arabica 100% origine Éthiopie",
        "packaging": "sachet aluminium",
        "origin": "Éthiopie",
        "weight_kg": 0.25
    }
]

def create_product(product_data):
    """Create a complete product with score"""
    print(f"\n{'='*60}")
    print(f"Processing: {product_data['name']}")
    print(f"{'='*60}")
    
    # Step 1: Extract ingredients with NLP
    print("1. Extracting ingredients with NLP...")
    nlp_response = requests.post(f"{NLP_URL}/nlp/extract", json={
        "text": product_data["ingredients_text"],
        "language": "fr"
    })
    
    if nlp_response.status_code != 200:
        print(f"   ⚠️  NLP service error: {nlp_response.status_code}")
        ingredients = [{"name": "unknown", "weight": product_data["weight_kg"]}]
    else:
        nlp_data = nlp_response.json()
        print(f"   ✓ Found {len(nlp_data.get('ingredients', []))} ingredients")
        
        # Convert NLP ingredients to LCA format
        ingredients = []
        for ing in nlp_data.get('ingredients', []):
            ingredients.append({
                "name": ing.get("name", "unknown"),
                "weight": product_data["weight_kg"] / max(len(nlp_data['ingredients']), 1)
            })
        
        if not ingredients:
            ingredients = [{"name": "mixed ingredients", "weight": product_data["weight_kg"]}]
    
    # Step 2: Calculate LCA
    print("2. Calculating LCA indicators...")
    lca_response = requests.post(f"{LCA_URL}/lca/calc", json={
        "ingredients": ingredients,
        "packaging_material": "plastic" if "plastique" in product_data["packaging"].lower() else "cardboard",
        "packaging_weight_kg": product_data["weight_kg"] * 0.05,
        "transport": [
            {
                "mode": "truck",
                "distance_km": 500 if "France" in product_data["origin"] else 2000
            }
        ]
    })
    
    if lca_response.status_code != 200:
        print(f"   ⚠️  LCA service error: {lca_response.status_code}")
        lca_data = {"co2": 2.5, "water": 100.0, "energy": 50.0}
    else:
        lca_data = lca_response.json()
        print(f"   ✓ CO2: {lca_data['co2']:.2f} kg, Water: {lca_data['water']:.2f} L, Energy: {lca_data['energy']:.2f} MJ")
    
    # Step 3: Calculate Score
    print("3. Computing eco-score...")
    score_response = requests.post(f"{SCORING_URL}/score/compute", json={
        "co2": lca_data["co2"],
        "water": lca_data["water"],
        "energy": lca_data["energy"]
    })
    
    if score_response.status_code != 200:
        print(f"   ⚠️  Scoring service error: {score_response.status_code}")
        score_data = {"score": 50, "grade": "C"}
    else:
        score_data = score_response.json()
        print(f"   ✓ Score: {score_data.get('score', 'N/A')} - Grade: {score_data.get('grade', 'N/A')}")
    
    # Step 4: Register in Widget API (direct DB insert via service)
    print("4. Registering product in catalog...")
    
    # Since we don't have a direct insert endpoint, we'll display the data
    final_product = {
        "name": product_data["name"],
        "brand": product_data["brand"],
        "gtin": product_data["gtin"],
        "score": score_data.get("score", 50),
        "grade": score_data.get("grade", "C"),
        "co2": lca_data["co2"],
        "water": lca_data["water"],
        "energy": lca_data["energy"],
        "ingredients": ingredients,
        "packaging": product_data["packaging"],
        "origin": product_data["origin"]
    }
    
    print(f"   ✓ Product ready: {final_product['name']} - Grade {final_product['grade']}")
    return final_product

def main():
    print("\n" + "="*60)
    print("  ECOLABEL-MS2027 - Demo Data Population")
    print("="*60)
    
    # Check if services are running
    print("\nChecking services...")
    services = {
        "NLP": NLP_URL,
        "LCA": LCA_URL,
        "Scoring": SCORING_URL,
        "Widget": WIDGET_URL
    }
    
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✓ {name} service is running")
            else:
                print(f"   ✗ {name} service returned {response.status_code}")
        except Exception as e:
            print(f"   ✗ {name} service is not accessible: {str(e)}")
    
    print("\n" + "="*60)
    print(f"Creating {len(DEMO_PRODUCTS)} demo products...")
    print("="*60)
    
    results = []
    for product_data in DEMO_PRODUCTS:
        try:
            result = create_product(product_data)
            results.append(result)
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"\n✓ Successfully processed {len(results)} products\n")
    
    for product in results:
        print(f"  • {product['name']:<40} Grade: {product['grade']}")
    
    print("\n" + "="*60)
    print("Note: Products are processed but not persisted in database.")
    print("To persist data, you need to implement a POST /public/products endpoint")
    print("or insert directly into the widget_db database.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
