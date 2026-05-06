# Jimat AI Service

Multi-domain AI microservice for intelligent expense tracking, insurance claims processing, and financial insights using LangChain/LangGraph orchestration.

## Features

- **Multi-Agent Orchestration**: Router + specialized agents for expenses, insurance, and insights
- **Intelligent Categorization**: LLM-powered with confidence scoring and fallback logic
- **Document Processing**: OCR for receipt images, text extraction
- **Conversation Memory**: Stateful agent interactions with context retention
- **Domain-Agnostic Design**: Extensible architecture for future domains (trading, crypto, etc.)
- **Production-Ready**: Error handling, fallbacks, rate limiting support

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the service**:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
   ```

4. **Health check**:
   ```bash
   curl http://localhost:8001/health
   ```

## Architecture

```
RouterAgent (Intent Classification)
    ↓
    ├─ ExpenseAgent (Categorization, Validation)
    ├─ InsuranceAgent (Claims, Coverage Assessment)
    └─ InsightsAgent (Analytics, Pattern Detection)
```

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /` - Root info

### Agent Processing (Primary)
- `POST /api/v1/agent/process` - Multi-agent orchestrator

### Domain-Specific (Phase 2+)
- `POST /api/v1/documents/analyze` - OCR + text extraction
- `POST /api/v1/categorization/categorize` - Expense categorization
- `POST /api/v1/insights/generate` - Analytics generation

## Configuration

See `.env` file for all configuration options:
- `LLM_PROVIDER`: huggingface, gemini, or ollama
- `HF_API_KEY`: Hugging Face API key
- `GEMINI_API_KEY`: Google Gemini API key
- `REDIS_URL`: Redis connection string (optional)

## Development

```bash
# Format code
black app/

# Run tests
pytest tests/

# Type checking
mypy app/
```

## Environment Setup

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Next Steps

1. Phase 2: Document Processing - OCR and text extraction
2. Phase 3: LLM Categorization - Expense categorization with confidence
3. Phase 4: Insight Generation - Analytics engine
4. Phase 5: Multi-Agent Orchestration - Full LangGraph setup
