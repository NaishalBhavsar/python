# Binance Futures Testnet Trading Bot (USDT-M) — Python

A simplified Python 3.x CLI app that places MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).

## Features
- Places **MARKET** and **LIMIT** orders (BUY/SELL)
- Bonus order type: **STOP_LIMIT**
- Clean structure (client/API layer + order logic + validators + CLI)
- Input validation with clear error messages
- Logging to a file (requests, responses, errors)
- Handles API errors, invalid input, and network failures

---

## Setup

### 1) Create Testnet Account + API Keys
- Register / login to Binance Futures Testnet
- Generate API key/secret

Testnet Base URL (used by default):
`https://testnet.binancefuture.com`

### 2) Install Dependencies
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
