# Jimat - Expense Management System

A comprehensive FastAPI project with multi-domain AI orchestration for intelligent expense tracking and financial insights.

## Project Structure

```
FastAPI Test/
├── jimat/               # Backend API (Express Management)
├── jimat-ai/           # AI Service (LLM & Orchestration)
├── jimat-frontend/     # Frontend (Next.js)
├── venv/               # Virtual environment (shared)
└── README.md           # This file
```

## Quick Start - Local Development

This project consists of three main services that work together. Follow the steps below to set up and run all services locally.

### Prerequisites

- Python 3.9+
- Node.js 16+ and npm
- Git

### Initial Setup

#### Step 1: Create and Activate Virtual Environment

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Step 2: Install Backend Dependencies

```bash
# Install dependencies for both backend services
pip install -r jimat/requirements.txt
```

### Running Services Locally

You'll need **3 terminal windows** - one for each service:

#### Terminal 1: Backend API (Jimat)

```bash
# Activate virtual environment (if not already activated)
.\venv\Scripts\activate

# Navigate to backend directory
cd jimat

# Run the FastAPI server
uvicorn app.main:app --reload --port 8000
```

**Available at**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Terminal 2: AI Service (Jimat-AI)

```bash
# Activate virtual environment (if not already activated)
.\venv\Scripts\activate

# Navigate to AI service directory
cd jimat-ai

# Run the AI microservice
uvicorn app.main:app --reload --port 8001
```

**Available at**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

#### Terminal 3: Frontend (Jimat-Frontend)

```bash
# Navigate to frontend directory
cd jimat-frontend

# Install dependencies (first time only)
npm install

# Run development server
npm run dev
```

**Available at**: http://localhost:3000

### Stopping Services

- Press `Ctrl + C` in each terminal to stop the respective service

### Environment Configuration

Each service may use `.env` files for configuration. Check each service's directory for `.env.example` to set up required environment variables.

## Detailed Setup Instructions

## Detailed Setup Instructions

### Backend Service (Jimat)

**Purpose**: Core expense management API

**Location**: `./jimat`

**Key Features**:
- Category management
- Expense tracking
- CRUD operations
- SQLAlchemy ORM
- Database session management

**To run**:
```bash
cd jimat
uvicorn app.main:app --reload --port 8000
```

**API Endpoints**:
- `GET /api/v1/categories` - List categories
- `POST /api/v1/categories` - Create category
- `GET /api/v1/expenses` - List expenses
- `POST /api/v1/expenses` - Create expense
- (See http://localhost:8000/docs for complete API)

### AI Service (Jimat-AI)

**Purpose**: AI-powered document processing and insights generation

**Location**: `./jimat-ai`

**Key Features**:
- Document processing
- Expense categorization
- Financial insights
- LangChain/LangGraph orchestration
- HuggingFace integration

**To run**:
```bash
cd jimat-ai
uvicorn app.main:app --reload --port 8001
```

**API Endpoints**:
- `/api/v1/documents/upload` - Upload documents for processing
- `/api/v1/categorization` - Categorize expenses
- `/api/v1/insights` - Generate financial insights
- (See http://localhost:8001/docs for complete API)

### Frontend Service (Jimat-Frontend)

**Purpose**: Next.js web interface for expense management

**Location**: `./jimat-frontend`

**Key Features**:
- Expense dashboard
- Category management UI
- Responsive design
- Real-time updates
- TypeScript support

**To run**:
```bash
cd jimat-frontend
npm install  # First time only
npm run dev
```

**Build for production**:
```bash
npm run build
npm start
```

## API Communication

The services communicate as follows:

```
Frontend (Port 3000)
    ↓
Backend API (Port 8000) - Main expense management
    ↓
AI Service (Port 8001) - Intelligence layer
```

**CORS Configuration**: The services are configured to allow cross-origin requests. Ensure the ports match the configuration in each service's `.env` file.

### Example: Creating an Expense

1. **Frontend** sends data to **Backend API**
   ```
   POST http://localhost:8000/api/v1/expenses
   ```

2. **Backend API** stores the expense and may trigger **AI Service**
   ```
   POST http://localhost:8001/api/v1/categorization
   ```

3. **AI Service** analyzes and returns categorization
4. **Frontend** displays the result

## Testing

### Backend Tests (Jimat)

```bash
cd jimat
pytest
```

### AI Service Tests (Jimat-AI)

```bash
cd jimat-ai
pytest
```

### Frontend Tests

```bash
cd jimat-frontend
npm run lint  # ESLint
```

## Troubleshooting

### Port Already in Use

If you see "Address already in use" error:

```bash
# Find and kill the process using the port
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Import Errors in Backend

```bash
# Ensure you're in the correct directory and virtual environment is activated
cd jimat
pip install -r requirements.txt
```

### Frontend Not Connecting to Backend

1. Verify both backend services are running on ports 8000 and 8001
2. Check CORS configuration in `.env` files
3. Verify API endpoints in `jimat-frontend/lib/api.ts`

### Database Issues

The backend creates SQLite database automatically. If you need to reset:

```bash
# Remove existing database
rm jimat/app/database/app.db

# Restart the backend service - it will recreate the database
```

## Environment Variables

Each service may have a `.env` file. Check each directory for `.env.example`:

### Jimat Backend
- `DATABASE_URL` - Database connection string
- `APP_NAME` - Application name

### Jimat-AI
- `HUGGINGFACE_API_KEY` - For HuggingFace model access
- `GOOGLE_API_KEY` - For Google Generative AI
- `OLLAMA_HOST` - For local LLM

### Jimat-Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_AI_URL` - AI service URL

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Jimat Frontend (Next.js)                │
│        http://localhost:3000                    │
│  ├─ Dashboard                                   │
│  ├─ Categories Management                       │
│  └─ Expenses Management                         │
└────────────────┬────────────────────────────────┘
                 │ API Calls
        ┌────────▼────────────────────────────────┐
        │    Jimat Backend (FastAPI)              │
        │    http://localhost:8000                │
        │  ├─ Category CRUD                       │
        │  ├─ Expense CRUD                        │
        │  └─ Database Management                 │
        └────────┬────────────────────────────────┘
                 │ Intelligent Processing
        ┌────────▼────────────────────────────────┐
        │   Jimat-AI Service (FastAPI)            │
        │   http://localhost:8001                 │
        │  ├─ Document Processing                 │
        │  ├─ Categorization                      │
        │  └─ Financial Insights                  │
        └─────────────────────────────────────────┘
```

## Development Workflow

1. **Frontend Development**: Edit components in `jimat-frontend/components/` or pages in `jimat-frontend/app/`
   - Changes auto-reload via Next.js HMR

2. **Backend Development**: Edit routes in `jimat/app/api/v1/routes/` or models in `jimat/app/models/`
   - Changes auto-reload via Uvicorn

3. **AI Development**: Edit routes in `jimat-ai/app/api/v1/routes/` or agents in `jimat-ai/app/agents/`
   - Changes auto-reload via Uvicorn

4. **Testing**: Run tests after significant changes

## Useful Resources

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## Support

For issues or questions about specific services, check the README in each project directory:
- `jimat/README.md` - Backend service details
- `jimat-ai/README.md` - AI service details
- `jimat-frontend/README.md` - Frontend details
