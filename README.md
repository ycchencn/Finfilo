

# FinFilo

FinFilo is a comprehensive financial data analytics and investment portfolio management platform that provides stock, ETF, and market data APIs, integrated with multiple large language models (LLMs) for intelligent analysis.

## Features

### 📊 Data APIs

- **Market Data**: Real-time quotes, ETF information, index constituents
- **Stock Data**: Historical prices, company profiles, technical indicators, DCF research reports
- **Portfolio Management**: Investment portfolios, daily summaries, transaction records
- **Backtesting System**: Backtest task management, signal generation
- **Watchlist**: User watchlist management

### 🤖 AI-Powered Analysis

- **Multi-LLM Support**: Integrated with Qwen, Doubao, DeepSeek, Minimax, Zhipu, Siliconflow, and VolcEngine
- **Financial Analysis Reports**: Auto-generated DCF valuation reports
- **News Analysis**: Intelligent financial news parsing and sentiment analysis
- **Technical Analysis**: AI-powered stock technical analysis and trading signals
- **Market Overview**: AI-generated market summary reports

### 🖥️ Web Interface

- **Dashboard**: Portfolio performance visualization
- **Stock Monitor**: Real-time stock monitoring with AI signals
- **ETF Explorer**: ETF analysis and constituent tracking
- **News Feed**: Aggregated financial news with AI summaries
- **Market Temperature**: Market sentiment indicators

## Technology Stack

- **Backend**: Python 3.11 + Flask
- **Database**: MySQL + SQLAlchemy ORM
- **Caching**: Redis + Flask-Caching
- **Message Queue**: RabbitMQ
- **Frontend**: Vue.js 3 + PrimeVue
- **LLM Integration**: Alibaba Cloud, Volcano Engine, Siliconflow, Zhipu AI

## Requirements

- Python 3.8+
- MySQL 8.0+
- Redis 7.0+

## Installation

```bash
# Clone the repository
git clone https://gitee.com/yc-chan/finfilo.git
cd finfilo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your API keys and database credentials:

```
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/finfilo

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM API Keys (at least one required)
QWEEN_API_KEY=your_qwen_key
DOUBAO_API_KEY=your_doubao_key
DEEPSEEK_API_KEY=your_deepseek_key
ZHIPU_API_KEY=your_zhipu_key
```

## Running the Application

### Development Mode

```bash
python run_app.py
```

The API will be available at `http://localhost:5000`

### Docker Deployment

```bash
docker-compose up -d
```

## API Endpoints

### Stock APIs

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/st