# Indian Judiciary Legal AI Platform

An AI-powered legal research and drafting system for Indian laws, designed for lawyers, corporate teams, and citizens.

## 🚀 Features

- **Conversational Legal AI**: ChatGPT-style interface for Indian legal queries
- **Document Analysis**: Upload and analyze FIRs, contracts, NDAs, legal notices
- **Legal Drafting**: AI-powered document generation
- **Case Law Research**: Search and analyze publicly available judgments
- **Corporate & Labour Law**: Specialized modules for compliance
- **Cyber Law Analysis**: IT Act, digital crime, data breach analysis
- **Outcome Simulation**: Predict case outcomes based on precedents

## 📁 Project Structure

```
indian-legal-ai/
├── frontend/                 # Next.js + React frontend
│   ├── app/                 # App router pages
│   ├── components/          # Reusable components
│   ├── lib/                 # Utilities and helpers
│   └── public/              # Static assets
├── backend/                 # FastAPI backend
│   ├── api/                 # API routes
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   ├── ai/                  # AI/ML services
│   └── utils/               # Utilities
└── docs/                    # Documentation
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS, shadcn/ui
- **State Management**: React Query, Zustand
- **Forms**: React Hook Form + Zod
- **Rich Text**: TipTap Editor
- **File Upload**: React Dropzone
- **PDF Viewer**: react-pdf

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with Prisma/SQLAlchemy
- **AI/ML**: OpenAI API, LangChain, ChromaDB (vector store)
- **Authentication**: JWT with bcrypt
- **File Storage**: AWS S3 / MinIO
- **Task Queue**: Celery + Redis
- **Cache**: Redis

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional but recommended)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/indian-legal-ai.git
cd indian-legal-ai

# Copy environment files
cp frontend/.env.example frontend/.env.local
cp backend/.env.example backend/.env

# Start all services
docker-compose up -d

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev

# Build for production
npm run build
npm start
```

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# For production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 🌐 Deployment Guide

### Step 1: Prepare Code

```bash
# Initialize Git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/indian-legal-ai.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Frontend to Vercel

1. **Sign up at [Vercel](https://vercel.com)**

2. **Import Project**:
   - Click "New Project"
   - Import from GitHub
   - Select `indian-legal-ai` repository
   - Set root directory to `frontend`

3. **Configure Build Settings**:
   ```
   Framework Preset: Next.js
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

4. **Environment Variables** (Add in Vercel Dashboard):
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
   NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   ```

5. **Deploy**: Click "Deploy"

### Step 3: Deploy Backend to Render

1. **Sign up at [Render](https://render.com)**

2. **Create PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `indian-legal-ai-db`
   - Plan: Free tier or Starter
   - Note the Internal Database URL

3. **Create Redis Instance**:
   - Click "New +" → "Redis"
   - Name: `indian-legal-ai-redis`
   - Plan: Free tier

4. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Settings:
     ```
     Name: indian-legal-ai-backend
     Region: Choose closest to users
     Branch: main
     Root Directory: backend
     Runtime: Python 3
     Build Command: pip install -r requirements.txt
     Start Command: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
     ```

5. **Environment Variables** (in Render Dashboard):
   ```
   DATABASE_URL=<from step 2>
   REDIS_URL=<from step 3>
   SECRET_KEY=<generate strong random key>
   OPENAI_API_KEY=<your openai key>
   AWS_ACCESS_KEY_ID=<your aws key>
   AWS_SECRET_ACCESS_KEY=<your aws secret>
   S3_BUCKET_NAME=indian-legal-ai-uploads
   FRONTEND_URL=https://your-app.vercel.app
   ENVIRONMENT=production
   ```

6. **Deploy**: Click "Create Web Service"

### Step 4: Database Setup

```bash
# Connect to Render shell
render shell indian-legal-ai-backend

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py
```

### Step 5: Configure Custom Domain (Optional)

**Vercel (Frontend)**:
- Go to Project Settings → Domains
- Add your custom domain (e.g., legalai.in)
- Update DNS records as instructed

**Render (Backend)**:
- Go to Service Settings → Custom Domains
- Add API subdomain (e.g., api.legalai.in)
- Update DNS records

### Step 6: Set Up Monitoring

1. **Vercel Analytics**: Enable in project settings
2. **Render Monitoring**: Built-in metrics available
3. **Sentry** (Error Tracking):
   ```bash
   # Add to both frontend and backend
   npm install @sentry/nextjs  # Frontend
   pip install sentry-sdk[fastapi]  # Backend
   ```

## 🔒 Security Considerations

- ✅ Environment variables never committed
- ✅ API keys stored securely
- ✅ CORS configured properly
- ✅ Rate limiting enabled
- ✅ Input validation and sanitization
- ✅ Encrypted data at rest and in transit
- ✅ Regular security updates

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Frontend
curl https://your-app.vercel.app/api/health

# Backend
curl https://your-backend.onrender.com/health
```

### Logs

```bash
# Vercel logs
vercel logs

# Render logs
# Available in Render dashboard → Logs tab
```

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test
npm run test:e2e

# Backend tests
cd backend
pytest
pytest --cov=app tests/
```

## 📝 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/legal_ai
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 📞 Support

For support, email support@legalai.in or join our Slack channel.

## 🙏 Acknowledgments

- Indian Kanoon for case law database
- India Code for Bare Acts
- Supreme Court of India for judgments
- e-Courts Services for case status
