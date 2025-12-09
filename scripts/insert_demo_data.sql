-- Script SQL pour insérer des produits de démonstration
-- Database: widget_db

-- Créer la table des produits si elle n'existe pas
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    gtin VARCHAR(20) UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer la table des scores si elle n'existe pas
CREATE TABLE IF NOT EXISTS scores (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    score FLOAT NOT NULL,
    grade VARCHAR(1) NOT NULL,
    co2 FLOAT,
    water FLOAT,
    energy FLOAT,
    confidence FLOAT DEFAULT 0.85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Créer la table des détails produits
CREATE TABLE IF NOT EXISTS product_details (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    ingredients TEXT,
    packaging VARCHAR(255),
    origin VARCHAR(255),
    weight_kg FLOAT,
    labels TEXT
);

-- Vider les tables existantes (ATTENTION: Supprime toutes les données)
TRUNCATE products, scores, product_details CASCADE;

-- Insérer les produits de démonstration

-- 1. Nutella
INSERT INTO products (name, brand, gtin, description) 
VALUES (
    'Nutella Pâte à Tartiner',
    'Ferrero',
    '3017620422003',
    'Pâte à tartiner aux noisettes et au cacao'
) RETURNING id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '3017620422003')
INSERT INTO scores (product_id, score, grade, co2, water, energy, confidence)
SELECT id, 45.5, 'D', 3.8, 250.0, 85.5, 0.82 FROM product_id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '3017620422003')
INSERT INTO product_details (product_id, ingredients, packaging, origin, weight_kg, labels)
SELECT id, 
    'Sucre, huile de palme, noisettes 13%, cacao maigre 7.4%, lait écrémé en poudre 6.6%, lactosérum en poudre, émulsifiants (lécithine de soja), vanilline',
    'Pot en verre, couvercle plastique',
    'France',
    0.4,
    NULL
FROM product_id;

-- 2. Barilla Spaghetti
INSERT INTO products (name, brand, gtin, description)
VALUES (
    'Pâtes Barilla Spaghetti',
    'Barilla',
    '8076809513005',
    'Spaghetti de qualité supérieure'
);

WITH product_id AS (SELECT id FROM products WHERE gtin = '8076809513005')
INSERT INTO scores (product_id, score, grade, co2, water, energy, confidence)
SELECT id, 72.3, 'B', 1.2, 80.0, 35.0, 0.88 FROM product_id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '8076809513005')
INSERT INTO product_details (product_id, ingredients, packaging, origin, weight_kg, labels)
SELECT id,
    'Semoule de blé dur de qualité supérieure, eau',
    'Carton recyclable',
    'Italie',
    0.5,
    NULL
FROM product_id;

-- 3. Lait Bio Lactel
INSERT INTO products (name, brand, gtin, description)
VALUES (
    'Lait Demi-Écrémé Bio',
    'Lactel',
    '3250391806058',
    'Lait demi-écrémé issu de l''agriculture biologique'
);

WITH product_id AS (SELECT id FROM products WHERE gtin = '3250391806058')
INSERT INTO scores (product_id, score, grade, co2, water, energy, confidence)
SELECT id, 68.0, 'B', 1.5, 95.0, 42.0, 0.90 FROM product_id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '3250391806058')
INSERT INTO product_details (product_id, ingredients, packaging, origin, weight_kg, labels)
SELECT id,
    'Lait demi-écrémé pasteurisé',
    'Brique carton TetraPak',
    'France',
    1.0,
    'Bio, AB'
FROM product_id;

-- 4. Pommes Golden Bio
INSERT INTO products (name, brand, gtin, description)
VALUES (
    'Pommes Golden Bio',
    'Vergers de France',
    '3760123456789',
    'Pommes Golden issues de l''agriculture biologique'
);

WITH product_id AS (SELECT id FROM products WHERE gtin = '3760123456789')
INSERT INTO scores (product_id, score, grade, co2, water, energy, confidence)
SELECT id, 82.5, 'A', 0.8, 45.0, 20.0, 0.92 FROM product_id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '3760123456789')
INSERT INTO product_details (product_id, ingredients, packaging, origin, weight_kg, labels)
SELECT id,
    'Pommes Golden issues de l''agriculture biologique',
    'Filet plastique recyclable',
    'France, Normandie',
    1.5,
    'Bio, AB, Local'
FROM product_id;

-- 5. Café Arabica Malongo
INSERT INTO products (name, brand, gtin, description)
VALUES (
    'Café Arabica Éthiopie',
    'Malongo',
    '3104030007404',
    'Café arabica 100% origine Éthiopie, commerce équitable'
);

WITH product_id AS (SELECT id FROM products WHERE gtin = '3104030007404')
INSERT INTO scores (product_id, score, grade, co2, water, energy, confidence)
SELECT id, 58.0, 'C', 2.5, 180.0, 65.0, 0.85 FROM product_id;

WITH product_id AS (SELECT id FROM products WHERE gtin = '3104030007404')
INSERT INTO product_details (product_id, ingredients, packaging, origin, weight_kg, labels)
SELECT id,
    'Café arabica 100% origine Éthiopie',
    'Sachet aluminium',
    'Éthiopie',
    0.25,
    'Commerce équitable, Max Havelaar'
FROM product_id;

-- Vérifier les données insérées
SELECT 
    p.name,
    p.brand,
    p.gtin,
    s.score,
    s.grade,
    s.co2,
    pd.origin
FROM products p
LEFT JOIN scores s ON p.id = s.product_id
LEFT JOIN product_details pd ON p.id = pd.product_id
ORDER BY s.score DESC;

-- Afficher le compte total
SELECT 
    COUNT(*) as total_products,
    COUNT(DISTINCT s.id) as products_with_scores
FROM products p
LEFT JOIN scores s ON p.id = s.product_id;
