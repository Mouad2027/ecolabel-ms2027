"""
Insert demo products directly into widget_db database
"""
import psycopg2
import psycopg2.extras
import json
from datetime import datetime
import uuid

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "widget_db",
    "user": "postgres",
    "password": "postgres"
}

# Demo products
PRODUCTS = [
    {
        "title": "Nutella Pâte à Tartiner",
        "brand": "Ferrero",
        "gtin": "3017620422003",
        "score_letter": "D",
        "score_numeric": 45.5,
        "confidence": 0.82,
        "co2": 3.8,
        "water": 250.0,
        "energy": 85.5,
        "ingredients": ["sucre", "huile de palme", "noisettes", "cacao", "lait écrémé"],
        "origins": ["France"],
        "labels": []
    },
    {
        "title": "Pâtes Barilla Spaghetti",
        "brand": "Barilla",
        "gtin": "8076809513005",
        "score_letter": "B",
        "score_numeric": 72.3,
        "confidence": 0.88,
        "co2": 1.2,
        "water": 80.0,
        "energy": 35.0,
        "ingredients": ["semoule de blé dur", "eau"],
        "origins": ["Italie"],
        "labels": []
    },
    {
        "title": "Lait Demi-Écrémé Bio",
        "brand": "Lactel",
        "gtin": "3250391806058",
        "score_letter": "B",
        "score_numeric": 68.0,
        "confidence": 0.90,
        "co2": 1.5,
        "water": 95.0,
        "energy": 42.0,
        "ingredients": ["lait demi-écrémé pasteurisé"],
        "origins": ["France"],
        "labels": ["Bio", "AB"]
    },
    {
        "title": "Pommes Golden Bio",
        "brand": "Vergers de France",
        "gtin": "3760123456789",
        "score_letter": "A",
        "score_numeric": 82.5,
        "confidence": 0.92,
        "co2": 0.8,
        "water": 45.0,
        "energy": 20.0,
        "ingredients": ["pommes golden bio"],
        "origins": ["France", "Normandie"],
        "labels": ["Bio", "AB", "Local"]
    },
    {
        "title": "Café Arabica Éthiopie",
        "brand": "Malongo",
        "gtin": "3104030007404",
        "score_letter": "C",
        "score_numeric": 58.0,
        "confidence": 0.85,
        "co2": 2.5,
        "water": 180.0,
        "energy": 65.0,
        "ingredients": ["café arabica 100%"],
        "origins": ["Éthiopie"],
        "labels": ["Commerce équitable", "Max Havelaar"]
    }
]

def insert_products():
    """Insert demo products into database"""
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Clear existing products (optional)
        print("\nClearing existing products...")
        cursor.execute("DELETE FROM products")
        conn.commit()
        print(f"✓ Cleared existing products")
        
        # Insert products
        print(f"\nInserting {len(PRODUCTS)} demo products...")
        
        insert_query = """
        INSERT INTO products (
            id, title, brand, gtin,
            score_letter, score_numeric, confidence,
            co2, water, energy,
            ingredients, origins, labels,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s
        )
        """
        
        now = datetime.utcnow()
        
        for product in PRODUCTS:
            product_id = str(uuid.uuid4())
            score_id = f"score_{product_id[:8]}"
            
            cursor.execute(insert_query, (
                product_id,
                product["title"],
                product["brand"],
                product["gtin"],
                product["score_letter"],
                product["score_numeric"],
                product["confidence"],
                product["co2"],
                product["water"],
                product["energy"],
                psycopg2.extras.Json(product["ingredients"]),
                psycopg2.extras.Json(product["origins"]),
                psycopg2.extras.Json(product["labels"]),
                now,
                now
            ))
            
            print(f"  ✓ {product['title']:<45} Grade: {product['score_letter']}")
        
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        print(f"\n{'='*70}")
        print(f"✓ Successfully inserted {count} products into widget_db")
        print(f"{'='*70}")
        
        # Display products
        print("\nProducts in database:")
        cursor.execute("""
            SELECT title, brand, gtin, score_letter, score_numeric
            FROM products
            ORDER BY score_numeric DESC
        """)
        
        for row in cursor.fetchall():
            title, brand, gtin, letter, score = row
            print(f"  • {title:<40} {brand:<15} Grade: {letter} ({score:.1f})")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*70}")
        print("✅ Demo data successfully loaded!")
        print(f"{'='*70}")
        print("\nYou can now search for products:")
        print("  - http://localhost:3000")
        print("  - http://localhost:8005/public/products/search?q=nutella")
        print(f"{'='*70}\n")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  ECOLABEL-MS2027 - Demo Data Insertion")
    print("="*70)
    insert_products()
