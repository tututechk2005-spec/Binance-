# Binance AI Trader Pro

A production-ready AI-powered cryptocurrency trading platform with Smart Money Concepts, automated trading, real-time signals, and a full admin panel.

## Tech Stack

### Frontend
- **React 18** + **Vite 5** + **TypeScript**
- **TailwindCSS** with custom dark theme (Binance-inspired colors)
- **React Query** for server state management
- **Zustand** for client state (auth)
- **Recharts** for trading charts and analytics
- **React Router v6** for navigation
- **React Hook Form** + **Zod** for form validation

### Backend
- **Python 3.11** + **FastAPI**
- **SQLAlchemy** + **Alembic** (PostgreSQL)
- **Redis** + **Celery** for background tasks and caching
- **python-binance** for Binance Spot & Futures (Mainnet + Testnet)
- **JWT** authentication (access + refresh tokens)
- **WebSocket** for real-time price streaming
- **numpy / pandas / ta** for AI indicators

### Infrastructure
- **Docker Compose** (PostgreSQL, Redis, Nginx, API, Celery Worker, Celery Beat, Frontend)
- **Nginx** reverse proxy

## Features

### Trading
- Binance Spot & Futures — Mainnet and Testnet
- Auto-trading based on AI signals
- Manual trade management (open, close, monitor)
- Real-time WebSocket price streaming
- Position tracking with unrealized PNL

### AI Engine
- RSI, MACD, Bollinger Bands, EMA/SMA, ATR, Stochastic, OBV, VWAP
- Smart Money Concepts: Break of Structure (BOS), Change of Character (CHOCH), Fair Value Gaps (FVG), Order Blocks, Liquidity Sweeps
- Multi-timeframe analysis (15m, 30m, 1h, 4h, 1d)
- Confidence scoring (0–100%)
- Risk management with ATR-based stop loss and dynamic take-profit targets

### Payments
- **Stripe** (cards, SEPA, Stripe Checkout)
- **PayPal** webhooks
- **MTN Mobile Money** (Africa)
- **Airtel Money** (Africa)
- Subscription plans: Free → Basic → Pro → Enterprise

### Admin Panel
- User management (role, status, plan)
- Trade & signal monitoring
- Payment & revenue analytics
- Audit logs & system logs

## Quick Start

### 1. Clone the project

```bash
unzip binance-ai-trader-pro.zip
cd binance-ai-trader-pro
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Key environment variables:
```env
DATABASE_URL=postgresql://batpro:batpro_password@postgres:5432/batpro
SECRET_KEY=your-super-secret-key-change-this-in-production
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
STRIPE_SECRET_KEY=sk_live_...
```

### 3. Start with Docker Compose

```bash
docker compose up --build -d
```

Services:
- **Frontend**: http://localhost:80
- **API**: http://localhost:80/api/docs (Swagger)
- **Flower** (Celery monitor): http://localhost:5555

### 4. Run database migrations

```bash
docker compose exec api alembic upgrade head
```

### 5. Seed initial data (admin user + plans)

```bash
docker compose exec api python scripts/seed_db.py
```

Default admin credentials:
- Email: `admin@batpro.app`
- Password: `Admin@123456`

## Development

### Backend only

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:80/api/docs
- **ReDoc**: http://localhost:80/api/redoc

## Project Structure

```
binance-ai-trader-pro/
├── backend/
│   ├── ai_engine/         # AI signal generation & indicators
│   ├── api/               # FastAPI routers
│   ├── core/              # Config, security, DB, Redis, Celery
│   ├── database/          # SQLAlchemy models & migrations
│   ├── middleware/         # Auth & rate limiting
│   ├── tasks/             # Celery async tasks
│   ├── binance_client.py  # Binance SDK wrapper
│   └── main.py            # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── layouts/       # Page layouts (Dashboard, Auth, Admin)
│   │   ├── pages/         # Route pages
│   │   ├── services/      # API client (axios)
│   │   ├── store/         # Zustand auth store
│   │   └── types/         # TypeScript interfaces
│   └── package.json
├── nginx/                 # Nginx reverse proxy config
├── docker-compose.yml
└── .env.example
```

## Security

- JWT tokens (15min access + 7d refresh with rotation)
- Binance API keys encrypted at rest (AES-256 via Fernet)
- Rate limiting (per-IP and per-user)
- CORS configured for production domains
- Helmet-style security headers via Nginx

## License

MIT License. Use at your own risk. Cryptocurrency trading involves substantial risk of loss.
