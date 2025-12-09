# 🌿 EcoLabel-MS2027

**A Complete Microservices Platform for Dynamic Environmental Scoring of Consumer Products**

EcoLabel-MS2027 is a full-stack microservices solution that parses product data (PDF/HTML/images), extracts ingredients using NLP, computes simplified lifecycle analysis (LCA), calculates an eco-score from A to E, and exposes the score through an API + embeddable widget. The platform maintains full data provenance and versioning for transparency and compliance.

---

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Datasets](#datasets)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EcoLabel-MS2027 Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   Frontend   │───▶│  Widget-API  │───▶│   Scoring    │◀──▶│ Provenance │ │
│  │   (React)    │    │   :8005      │    │   :8004      │    │   :8006    │ │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘    └────────────┘ │
│                             │                   │                            │
│                             ▼                   ▼                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   Parser     │───▶│     NLP      │───▶│   LCA-Lite   │                   │
│  │   :8001      │    │   :8002      │    │   :8003      │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           Infrastructure                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │  PostgreSQL  │    │    MinIO     │    │   MLflow     │    │  pgAdmin   │ │
│  │   :5432      │    │  :9000/9001  │    │   :5000      │    │   :5050    │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Services

### 1. Parser-Produit (Port 8001)
**Product data extraction service**

- Parses PDF documents using pdfplumber
- Extracts HTML content with BeautifulSoup4
- Processes images with Tesseract OCR
- Reads barcodes/GTINs with pyzbar
- Stores raw extracted data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/product/parse` | POST | Parse uploaded file (PDF/HTML/image) |
| `/product/{id}` | GET | Get parsed product data |
| `/health` | GET | Service health check |

### 2. NLP-Ingredients (Port 8002)
**NLP pipeline for ingredient extraction**

- spaCy pipeline for French/multilingual NER
- BERT classifier for ingredient categorization
- Ingredient normalization and taxonomy mapping
- Material and label detection

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/nlp/extract` | POST | Extract ingredients from text |
| `/nlp/classify` | POST | Classify extracted entities |
| `/taxonomy/ingredients` | GET | Get ingredient taxonomy |
| `/taxonomy/materials` | GET | Get materials taxonomy |
| `/taxonomy/labels` | GET | Get eco-labels taxonomy |

### 3. LCA-Lite (Port 8003)
**Simplified Life Cycle Assessment calculator**

- CO2 emissions calculation (kg CO2e)
- Water usage estimation (liters)
- Energy consumption (MJ)
- Transport impact calculation
- Uses FAO, ADEME, and EcoInvent datasets

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/lca/calc` | POST | Calculate LCA indicators |
| `/lca/datasets` | GET | List available datasets |
| `/lca/impact/{ingredient}` | GET | Get ingredient impact factors |

### 4. Scoring (Port 8004)
**Eco-score calculation service**

- Weighted multi-criteria scoring
- MinMaxScaler normalization (scikit-learn)
- Bonus/malus adjustments for labels
- A-E grade conversion with colors

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/score/compute` | POST | Compute eco-score |
| `/score/thresholds` | GET | Get scoring thresholds |
| `/score/weights` | GET | Get indicator weights |

### 5. Widget-API (Port 8005)
**Public API and React widget**

- RESTful API for score retrieval
- Product search and GTIN lookup
- Embeddable widget code generation
- React frontend with score visualization

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/public/product/{id}` | GET | Get product eco-score |
| `/public/products/search` | GET | Search products |
| `/public/gtin/{gtin}` | GET | Lookup by GTIN |
| `/public/embed/{id}` | GET | Get embed code |

### 6. Provenance (Port 8006)
**Data lineage and experiment tracking**

- Full data provenance tracking
- DVC integration for dataset versioning
- MLflow integration for experiments
- Audit trail generation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/provenance/{score_id}` | GET | Get score provenance |
| `/provenance/{score_id}/lineage` | GET | Get lineage graph |
| `/provenance/experiments` | GET/POST | Manage experiments |
| `/provenance/datasets` | GET/POST | Manage dataset versions |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Launch the Platform

```bash
# Clone the repository
git clone https://github.com/your-org/ecolabel-ms.git
cd ecolabel-ms

# Copy environment template
cp .env.example .env

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Access Points

| Service | URL |
|---------|-----|
| Widget Frontend | http://localhost:3000 |
| Widget API | http://localhost:8005 |
| Parser API | http://localhost:8001 |
| NLP API | http://localhost:8002 |
| LCA API | http://localhost:8003 |
| Scoring API | http://localhost:8004 |
| Provenance API | http://localhost:8006 |
| MLflow UI | http://localhost:5000 |
| MinIO Console | http://localhost:9001 |
| pgAdmin | http://localhost:5050 |

---

## 💻 Development Setup

### Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies for a service
cd parser-produit
pip install -r requirements.txt

# Run service
uvicorn main:app --reload --port 8001
```

### Running Individual Services

```bash
# Parser service
cd parser-produit && uvicorn main:app --port 8001 --reload

# NLP service
cd nlp-ingredients && uvicorn main:app --port 8002 --reload

# LCA service
cd lca-lite && uvicorn main:app --port 8003 --reload

# Scoring service
cd scoring && uvicorn main:app --port 8004 --reload

# Widget API
cd widget-api/backend && uvicorn main:app --port 8005 --reload

# Provenance service
cd provenance && uvicorn main:app --port 8006 --reload
```

### Frontend Development

```bash
cd widget-api/frontend/react-app
npm install
npm run dev
```

---

## 📚 API Documentation

Each service exposes automatic OpenAPI documentation:

- Parser: http://localhost:8001/docs
- NLP: http://localhost:8002/docs
- LCA: http://localhost:8003/docs
- Scoring: http://localhost:8004/docs
- Widget: http://localhost:8005/docs
- Provenance: http://localhost:8006/docs

### Example: Calculate Eco-Score

```bash
# 1. Parse a product PDF
curl -X POST "http://localhost:8001/product/parse" \
  -F "file=@product.pdf" \
  -F "file_type=pdf"

# 2. Extract ingredients
curl -X POST "http://localhost:8002/nlp/extract" \
  -H "Content-Type: application/json" \
  -d '{"text": "Ingredients: wheat flour, sugar, palm oil, eggs"}'

# 3. Calculate LCA
curl -X POST "http://localhost:8003/lca/calc" \
  -H "Content-Type: application/json" \
  -d '{"ingredients": [{"name": "wheat", "quantity": 0.5}, {"name": "sugar", "quantity": 0.2}]}'

# 4. Compute score
curl -X POST "http://localhost:8004/score/compute" \
  -H "Content-Type: application/json" \
  -d '{"co2_kg": 2.5, "water_l": 1500, "energy_mj": 15}'

# 5. Get public product score
curl "http://localhost:8005/public/product/123"
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_password

# Services
PARSER_SERVICE_URL=http://localhost:8001
NLP_SERVICE_URL=http://localhost:8002
LCA_SERVICE_URL=http://localhost:8003
SCORING_SERVICE_URL=http://localhost:8004
```

### NLP Models

The NLP service uses:
- **spaCy**: `fr_core_news_md` (French) - auto-downloaded
- **BERT**: `bert-base-multilingual-cased` - auto-downloaded

To use custom models, mount them to `/app/models` in the container.

---

## 📊 Datasets

### Included Datasets

```
datasets/
├── ecoinvent/
│   ├── materials_impacts.csv    # Material CO2/water/energy factors
│   ├── processes.csv            # Manufacturing process impacts
│   └── transport_factors.csv    # Transport mode emissions
├── fao/
│   ├── ingredients_impacts.csv  # Food ingredient impacts
│   └── country_factors.csv      # Country-specific factors
├── ademe/
│   ├── base_carbone.json        # French carbon database
│   └── scoring_methodology.json # Scoring thresholds
└── taxonomies/
    ├── ingredients_taxonomy.json
    └── labels_taxonomy.json
```

### Adding Custom Datasets

1. Add CSV/JSON files to the appropriate directory
2. Update the dataset loader in the relevant service
3. Rebuild the service container

---

## 🐳 Deployment

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy with swarm
docker stack deploy -c docker-compose.yml ecolabel

# Or with kubernetes
kubectl apply -f k8s/
```

### Scaling

```bash
# Scale NLP service (resource intensive)
docker-compose up -d --scale nlp-ingredients=3

# Scale Widget API for traffic
docker-compose up -d --scale widget-api=5
```

---

## 📁 Project Structure

```
ecolabel-ms/
├── parser-produit/          # PDF/HTML/Image parsing service
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── Dockerfile
├── nlp-ingredients/         # NLP extraction service
│   ├── main.py
│   ├── routes/
│   ├── nlp/
│   ├── models/
│   └── Dockerfile
├── lca-lite/                # LCA calculation service
│   ├── main.py
│   ├── routes/
│   ├── calculators/
│   ├── datasets/
│   └── Dockerfile
├── scoring/                 # Score computation service
│   ├── main.py
│   ├── routes/
│   ├── ml/
│   └── Dockerfile
├── widget-api/              # Public API + Frontend
│   ├── backend/
│   └── frontend/react-app/
├── provenance/              # Data lineage service
│   ├── main.py
│   ├── routes/
│   ├── tracking/
│   └── Dockerfile
├── datasets/                # Reference datasets
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Container orchestration
├── .env.example            # Environment template
└── README.md
```

---

## 🧪 Testing

```bash
# Run tests for all services
./scripts/run-tests.sh

# Run tests for specific service
cd parser-produit
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📈 Monitoring

- **MLflow**: http://localhost:5000 - Experiment tracking
- **pgAdmin**: http://localhost:5050 - Database management
- **MinIO Console**: http://localhost:9001 - Object storage

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [ADEME Base Carbone](https://www.bilans-ges.ademe.fr/) - French carbon database
- [FAO](https://www.fao.org/) - Food and agriculture data
- [EcoInvent](https://ecoinvent.org/) - LCA database methodology
- [spaCy](https://spacy.io/) - NLP library
- [FastAPI](https://fastapi.tiangolo.com/) - API framework

---

**Built with ❤️ for a sustainable future**
