
---

## 10) Example Log Files (what you submit)

> These are **sample formats**. When you run real orders, your logs will include real `orderId`, timestamps, etc.

### `logs/market_example.log`

```txt
2026-01-29 20:05:12 | INFO | trading_bot | HTTP POST /fapi/v1/order params={'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'MARKET', 'quantity': 0.001, 'newOrderRespType': 'RESULT', 'timestamp': 1706548512000, 'recvWindow': 5000, 'signature': '***redacted***'} signed=True
2026-01-29 20:05:13 | INFO | trading_bot | HTTP /fapi/v1/order -> 200 body={"orderId":123456789,"status":"NEW","executedQty":"0","avgPrice":"0.0"}
