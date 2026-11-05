\# CryptoPulse — Data Source Documentation



\## 1. Data Source Overview



CryptoPulse uses the public market-data services provided by Binance to collect real-time cryptocurrency trading information.



The selected trading pair is \*\*BTCUSDT\*\*, representing Bitcoin traded against Tether (USDT).



The project uses Binance's public WebSocket market-data stream to receive aggregated trade events continuously. These events provide information about trade prices, quantities, timestamps and trade identifiers.



The collected events are normalized by a Python collector and stored locally in JSON Lines (JSONL) format.



\## 2. Why BTCUSDT Was Selected



BTCUSDT was selected as the initial market-data source because Bitcoin is one of the most actively traded cryptocurrency assets.



The trading pair provides a relevant basis for studying short-term price movements and market volatility.



Using one trading pair also simplifies the initial distributed streaming architecture while allowing future extensions to additional cryptocurrency markets.



\## 3. Communication Protocols



CryptoPulse uses two public Binance interfaces:



\### 3.1 REST API



The Binance REST API provides access to market information through HTTP requests.



A tested endpoint is:



`https://data-api.binance.vision/api/v3/ticker/price?symbol=BTCUSDT`



This endpoint returns the latest available BTCUSDT price.



REST is useful for retrieving individual snapshots of market information but does not provide the continuous event stream required by the project's real-time processing pipeline.



\### 3.2 WebSocket API



The project uses the following public WebSocket endpoint:



`wss://data-stream.binance.vision/ws/btcusdt@aggTrade`



WebSocket provides a persistent connection through which Binance delivers market events as they occur.



The collector uses Python's `websockets` library to establish the connection and asynchronously receive incoming JSON messages.



No API key is required for this public market-data stream.



\## 4. Selected Stream: Aggregated Trades



CryptoPulse subscribes to Binance's `aggTrade` stream for BTCUSDT.



An aggregated trade represents one or more trades associated with the same taker order.



Each event contains information about the aggregated trade, including its identifier, execution price, quantity, timestamps and buyer-maker indicator.



The stream is suitable for studying short-term market activity and constructing time-based price and volume features.



\## 5. Event Structure and Data Types



The Python collector normalizes Binance messages into a consistent JSON structure.



Example event:



```json

{

&#x20; "event\_type": "aggTrade",

&#x20; "symbol": "BTCUSDT",

&#x20; "trade\_id": 4106695783,

&#x20; "event\_time": 1793812279059,

&#x20; "event\_time\_utc": "2026-11-04T17:11:19.059000+00:00",

&#x20; "price": "80456.01000000",

&#x20; "quantity": "0.00015000",

&#x20; "first\_trade\_id": 6819894385,

&#x20; "last\_trade\_id": 6819894385,

&#x20; "trade\_time": 1793812279059,

&#x20; "buyer\_is\_maker": false

}

```



\### Field descriptions



| Field | Data type | Description |

|---|---|---|

| event\_type | String | Binance event type |

| symbol | String | Trading pair |

| trade\_id | Integer | Aggregated trade identifier |

| event\_time | Integer | Event timestamp in milliseconds |

| event\_time\_utc | String | UTC ISO 8601 representation of event time |

| price | String | Aggregated trade price |

| quantity | String | Aggregated trade quantity |

| first\_trade\_id | Integer | First underlying trade identifier |

| last\_trade\_id | Integer | Last underlying trade identifier |

| trade\_time | Integer | Trade execution timestamp in milliseconds |

| buyer\_is\_maker | Boolean | Indicates whether the buyer was the maker |



Price and quantity are preserved as strings to avoid losing decimal precision during initial data collection.



\## 6. Timestamp Management



The collector preserves two Binance timestamps:



\- `event\_time` (`E`): the event publication timestamp.

\- `trade\_time` (`T`): the trade execution timestamp.



Both timestamps are represented as Unix epoch milliseconds.



The collector converts the event timestamp into UTC using Python's timezone-aware datetime functionality and stores the resulting ISO 8601 representation in `event\_time\_utc`.



Maintaining UTC timestamps supports consistent event-time processing in downstream Spark Structured Streaming operations.



\## 7. Data Format and Storage



Incoming Binance messages are parsed from JSON and normalized into the project's event structure.



The collector stores events in JSON Lines format, with one JSON object per line.



Files are organized by UTC event date:



`data/raw/btcusdt\_YYYY-MM-DD.jsonl`



This organization supports incremental collection and subsequent historical processing.



The collector enforces a maximum total JSONL storage limit of 2 GB.



Raw market data is excluded from Git version control.



\## 8. Event Frequency and Traffic Characteristics



The WebSocket stream delivers events continuously as aggregated trades occur on Binance.



The event arrival rate is variable and depends on market activity, trading volume and market conditions.



No fixed event frequency or sustained throughput measurement is assumed.



The collector reports its cumulative event count during each execution every 1,000 newly accepted events.



\## 9. Reliability and Connection Management



The Python collector implements basic connection recovery mechanisms.



Its current behavior includes:



\- A 15-second WebSocket connection timeout.

\- WebSocket ping intervals of 20 seconds.

\- A 20-second ping timeout.

\- Automatic reconnection after supported connection or data errors.

\- A five-second delay before reconnecting.

\- Trade ID comparison to skip events whose identifiers are not greater than the last processed identifier.



The collector also tracks storage consumption and stops collection when its configured storage limit is reached.



These mechanisms provide basic operational resilience but do not guarantee complete recovery of events missed during connection interruptions.



\## 10. Data Source Limitations



The current data collection scope has several limitations:



\- Only BTCUSDT is collected.

\- The selected stream contains aggregated trades rather than every individual raw trade.

\- The public market-data stream does not require authentication, but remains subject to Binance service availability and applicable limits.

\- Events missed during disconnections are not automatically recovered through historical REST queries.

\- Trade ID filtering does not independently guarantee complete event delivery.

\- Observed event frequency varies with market activity.

\- Historical collection coverage depends on the collector's uptime and storage availability.



These limitations must be considered when developing the downstream streaming and volatility prediction pipeline.



\## 11. Role in the CryptoPulse Architecture



The Binance WebSocket stream is the initial external data source of the CryptoPulse architecture.



The Python collector receives and normalizes aggregated trade events before storing them in JSONL format.



The planned architecture will subsequently integrate Kafka for distributed event ingestion, Spark Structured Streaming for real-time processing and Hadoop HDFS for historical storage.



These downstream components are planned and must not be considered operational until their implementation and integration have been verified.

