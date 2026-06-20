# 🚀 AI-Powered Contract Intelligence & Risk Scoring System

[![CI](https://github.com/AzmatX/legal-contract-intelligence-engine/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/AzmatX/legal-contract-intelligence-engine/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A production-grade NLP system for automated contract analysis, clause classification, and risk scoring. Built with FastAPI, spaCy, and Tesseract OCR.

## ✨ Features

- **📄 Multi-format Document Support**: Process PDF and DOCX contracts
- **🔍 OCR Pipeline**: Extract text from scanned documents using Tesseract
- **🏷️ Named Entity Recognition**: Identify organizations, dates, monetary values, persons, and legal entities using spaCy
- **📋 Clause Classification**: Detect key contract clauses (Termination, Confidentiality, Indemnification, Limitation of Liability, Governing Law)
- **⚠️ Risk Scoring**: Automated risk assessment (Low/Medium/High) with detailed breakdowns
- **🚀 RESTful API**: FastAPI backend with async processing and Swagger documentation
- **🐳 Docker Ready**: Containerized deployment with docker-compose
- **✅ Comprehensive Testing**: >80% code coverage with pytest
- **🔄 CI/CD**: GitHub Actions for automated testing and Docker publishing

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI, Uvicorn |
| NLP | spaCy (en_core_web_sm) |
| OCR | Tesseract, pdf2image, pytesseract |
| Validation | Pydantic, pydantic-settings |
| Testing | pytest, pytest-cov |
| Linting | Ruff |
| Containerization | Docker, docker-compose |
| CI/CD | GitHub Actions |

## 📦 Installation

### Prerequisites

- Python 3.10 or 3.11
- Tesseract OCR
- Poppler utilities (for PDF processing)

### Local Setup

1. **Clone the repository**:
```bash
git clone https://github.com/AzmatX/legal-contract-intelligence-engine.git
cd legal-contract-intelligence-engine
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install system dependencies**:

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
```

**macOS**:
```bash
brew install tesseract poppler
```

4. **Install Python dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

5. **Download spaCy model**:
```bash
python -m spacy download en_core_web_sm
```

6. **Configure environment**:
```bash
cp .env.example .env
```

## 🚀 Quick Start

### Run with Docker (Recommended)

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Run Locally

```bash
# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Start the server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Usage

### Health Check

```bash
curl http://localhost:8000/health
```

### Analyze a Contract

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data/sample_contracts/sample_service_agreement.txt"
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI or `http://localhost:8000/redoc` for ReDoc.

### Example Response

```json
{
  "extracted_text": "SERVICE AGREEMENT\n\nThis Service Agreement...",
  "entities": [
    {"text": "TechCorp Solutions Inc.", "label": "ORG", "start": 45, "end": 68},
    {"text": "January 15, 2024", "label": "DATE", "start": 12, "end": 28},
    {"text": "$250,000 USD", "label": "MONEY", "start": 512, "end": 524}
  ],
  "clauses": [
    {
      "type": "termination",
      "text": "Either party may terminate this Agreement...",
      "confidence": 0.92
    },
    {
      "type": "confidentiality",
      "text": "Both parties agree to maintain strict confidentiality...",
      "confidence": 0.88
    }
  ],
  "risk_score": 45,
  "risk_category": "Medium",
  "summary": "Contract contains standard termination and confidentiality clauses with moderate risk exposure."
}
```

## 🧪 Testing

Run all tests with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

Run specific test modules:

```bash
pytest tests/test_ocr.py -v
pytest tests/test_ner.py -v
pytest tests/test_clause.py -v
pytest tests/test_risk.py -v
pytest tests/test_api.py -v
```

## 📁 Project Structure

```
contract-intelligence/
├── .github/workflows/       # CI/CD pipelines
├── src/
│   ├── api/                 # FastAPI application
│   ├── ocr/                 # OCR and PDF processing
│   ├── ner/                 # Named Entity Recognition
│   ├── clause_classification/ # Clause detection
│   ├── risk_scoring/        # Risk assessment
│   └── utils/               # Utilities and logging
├── tests/                   # Test suite
├── data/
│   ├── sample_contracts/    # Sample PDF/TXT files
│   └── cuad_sample/         # CUAD dataset samples
├── docker/
│   └── Dockerfile           # Production Docker image
├── docker-compose.yml       # Local development setup
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── pyproject.toml          # Project configuration
```

## 🔧 Configuration

Environment variables (via `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SPACY_MODEL` | `en_core_web_sm` | spaCy model to use |
| `RISK_LOW_THRESHOLD` | `30` | Threshold for Low risk category |
| `RISK_HIGH_THRESHOLD` | `70` | Threshold for High risk category |
| `TESSERACT_PATH` | `/usr/bin/tesseract` | Path to Tesseract executable |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines (enforced by Ruff)
- Write tests for new features
- Maintain >80% code coverage
- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CUAD Dataset](https://www.atticusprojectai.org/cuad) for contract annotation standards
- [spaCy](https://spacy.io/) for NLP capabilities
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for text extraction
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

For issues and feature requests, please open an issue on the [GitHub repository](https://github.com/AzmatX/legal-contract-intelligence-engine/issues).

---

Built with ❤️ for legal tech innovation
