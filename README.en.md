# FinFilo

FinFilo is a financial data analysis and portfolio management platform that provides APIs for stock, ETF, and market data, integrated with multiple large language models (LLMs) for intelligent analysis.

## Features

### 📊 Data APIs
- **Market Data**: Real-time quotes, ETF information, constituent stock queries
- **Stock Data**: Historical prices, stock profiles, technical analysis, DCF research reports
- **Portfolio**: Portfolio management, daily statistics, transaction records
- **Backtesting System**: Backtesting task management, signal generation
- **Watchlist**: Custom stock watchlist management

### 🤖 AI Intelligent Analysis
- Powered by LLMs such as Qwen, Doubao, VolcEngine, and Zhipu AI
- Automated generation of financial analysis reports
- Intelligent interpretation of financial news
- Generation of quantitative trading code
- Smart trading recommendations

## Technology Stack

- **Backend**: Python Flask
- **Caching**: Flask-Caching
- **LLM Integration**: Alibaba Cloud Qwen, ByteDance Doubao, VolcEngine, Zhipu AI

## Quick Start

### Prerequisites

- Python 3.8+
- Redis (for caching)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Copy `.env.example` to `.env` and configure the required API keys:

```bash
cp .env.example .env
```

### Start the Service

```bash
# Development environment
python run.py

# Or using Docker
docker-compose up -d
```

## API Endpoints

### Stock APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v |