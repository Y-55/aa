# Thmanyah Assessment

## 🎯 My Solution Overview
حاولت اكتب عربي هنا عشان اصيد جوكم، بس والله ما عرفت كيف انسقه، صعب جدا وراح ياخذ وقت كثير، فخلاص بكتب انجليزي تحملوني دي المرة.

The assessment consists of several sub-challenges. I'll list each one and walk through my solution independently. After that, I'll demonstrate how to run the project and dive into the technical details.

But first, here’s a quick overview of the data stack I chose:

#### 🛠️ Tech Stack

- **Source Database**: PostgreSQL
- **Caching & In-Memory DB**: Redis
- **Messaging System**: Redpanda (Kafka-compatible) – Used for real-time event streaming and message queuing. _I chose Redpanda because I already had a Docker Compose setup from a previous project, I'm familiar with it, and it offers the same functionality as Kafka, being fully Kafka API-compatible._
- **Change Data Capture CDC**: Debezium-PostgreSQL Source Kafka Connector – Used for real-time data extraction from PostgreSQL. _I chose it because it's open-source, I have solid experience with it, and it supports backfilling as well._
- **OLAP Database**: Clickhouse. _I chose it because it's open-source, unlike BigQuery which requires a GCP account and additional setup. The main reason, however, is my solid experience with ClickHouse and its strong integration with Kafka._
- **Data Sink**: Redis Sink Kafka Connector - _straightforward and simple, especially compared to building and deploying a custom consumer application._
- **Stream Data Processing**: Tryied 2 different ways, -I'll talk about this in the next section-:
  - Clickhouse
  - Kafka Streams


#### 📊 Architecture Overview
<img width="3590" height="1404" alt="Arc 2025-07-20 21 56 46" src="https://github.com/user-attachments/assets/a41afec5-08f8-4720-b4fe-f1091a1aa745" />

#### 🏗️ Challenges Walk Through

1.  **Sync the data** in real-time from PostgreSQL DB **source** to Kafka
    - Here, I used Debezium, an open-source Kafka connector. It's commonly used behind many ETL tools to sync data from various databases into Kafka. I have experience with it, and it gets the job done reliably.
2.  **Process stream data** including join and aggregation operations.
       -  The first solution that came to mind was ClickHouse. ClickHouse has a Kafka engine table, which essentially acts as a Kafka consumer, continuously ingesting data from a Kafka topic. It can also do the reverse, pushing data back into a Kafka topic. This was the first approach I tried, but it wasn’t fast enough to meet the 5-second minimum requirement, as ClickHouse typically processes the data in about 4–8 seconds.That led me to explore other options, including Kafka Streams, which was the simplest option from the provided list.
3.  **Load the processed data to OLAP DB (Clickhouse).**
       - I really like ClickHouse — it's fast and cost-effective. What I don’t like about BigQuery is its complex pricing model and the fact that it only runs on GCP. ClickHouse offers more flexibility, lower costs, and faster performance. Even its Cloud version is significantly more affordable than BigQuery. The main downside, however, is that ClickHouse has less third-party tool support compared to BigQuery.
4.  **Load the processed data to Redis** for fast analytics delivery.
       - Oof, this one was a real headache. It was my first time working directly with Redis, usually the OLAP DB does the job, but seems you guys have an intresting usecase -hope to hear about it soon-.In the end, the fastest and most reliable approach was to use a Kafka connector and query the data using Redis' query engine, which allows for flexible aggregation and filtering.
5.  **Load the processed data to external system you don't control.**
    - Here I'm really confused, not a sigle hint or requiremnt about it, I can come up with many solutinos but it really depends on the use case, here is the list of solutions that we can apply:
      - Use the third system’s kafka connector directly – This is the most straightforward and preferred solution if available.
      - S3 Connector – If the third party is an enterprise, we could send the data to an S3 bucket they own using an S3 sink connector.
      - Webhook – If we're responsible for delivering the data reliably, a webhook might be a suitable option.
      - API – We could expose an API that reads from Kafka and forwards the data as needed.



## 📊 Key Components I Built

### **Complete Project Structure**
```
thmanyah_assessment/
├── 📁 configs/                           # Configuration files
│   ├── debezium_postgres_connect.json    # Debezium PostgreSQL connector config
│   ├── redis_connect.json                # Redis sink connector config
│   └── s3_connector.json                 # S3 connector config
│
├── 📁 scripts/                           # All automation and processing scripts
│   ├── 📁 postgres/                      # PostgreSQL related scripts
│   │   ├── init_db.py                    # Database schema and initial data setup
│   │   ├── simulate_data_ingestion.py    # Realistic event generation
│   │   ├── insert_debezium_signals.py    # Debezium signal insertion
│   │   └── clear_db.py                   # Database cleanup utilities
│   │
│   ├── 📁 clickhouse/                    # ClickHouse analytics scripts
│   │   ├── init_landing_tables.py        # CDC Tables Reading from Kafka
│   │   ├── kafka_transformation.py       # Stream processing logic
│   │   └── clear_db.py                   # ClickHouse cleanup utilities
│   │
│   ├── 📁 redis/                         # Redis operations
│   │   ├── init_redis.py                 # Redis index init
│   │   ├── queries.py                    # Redis agg query
│   │   └── clear_redis.py                # Redis cleanup utilities
│   │
│   ├── 📁 redpanda/                      # RedPanda/Kafka management
│   │   ├── init_postgres_connect.py      # Initialize Debezium connector
│   │   ├── init_redis_connect.py         # Initialize Redis sink connector
│   │   ├── clear_debezium_connectors.py  # Clean up Debezium connectors
│   │   ├── clear_redis_connectors.py     # Clean up Redis connectors
│   │   └── clear_topics.py               # Clean up Kafka topics
│   │
│   ├── 📁 kafka_streams_app/             # Kafka Streams Java application
│   │   ├── 📁 src/
│   │   │   ├── 📁 main/
│   │   │   │   ├── 📁 java/com/thmanyah/
│   │   │   │   │   └── App.java          # Main Kafka Streams application
│   │   ├── pom.xml                       # Maven project configuration
│   │   └── dependency-reduced-pom.xml    # Maven dependency management
│   │
│   ├── 📁 external/                      # External system integration
│   │   └── (empty)
│   │
│   ├── init.sh                          # Main initialization script calls all init scripts
│   ├── full_run.sh                      # Complete pipeline execution
│   ├── clear.sh                         # System cleanup script
│   └── simulate_data_ingestion.sh       # Data generation automation
│
├── 📁 volumes/                          # Docker volume mounts
│
├── docker-compose.yaml                  # Complete infrastructure setup
├── Dockerfile                           # Main application container
├── pyproject.toml                       # Python project configuration
├── poetry.lock                          # Python dependency lock file
├── .gitignore                           # Git ignore patterns
└── README.md                            # Project documentation
```

### **Infrastructure (`docker-compose.yaml`)**

The infrastructure is built using Docker Compose with 8 core services that work together to create a complete real-time data pipeline:

#### **🏗️ Core Services**

- **RedPanda Cluster** (`redpanda-1`)
  - Kafka-compatible streaming platform running on port 29092
  - Configured with 2GB memory and optimized for development

- **PostgreSQL Database** (`postgres`)
  - Primary source database with logical replication enabled
  - WAL level set to `logical` for CDC compatibility
  - Running on port 5432 with admin/password credentials
  - Configured for Debezium change data capture

- **ClickHouse Analytics Engine** (`clickhouse`)
  - Columnar OLAP database for real-time analytics
  - HTTP interface on port 8123, native on port 9000
  - Persistent data storage in `./volumes/clickhouse/`
  - Optimized file descriptors (262,144) for high throughput

- **Redis Server** (`redis`)
  - In-memory data store
  - Running on port 6379

#### **🔌 Data Integration Services**

- **Debezium Connect** (`connect-debezium`)
  - Kafka Connect cluster for CDC operations
  - REST API on port 8083 for connector management

- **Redis Kafka Connect** (`connect-redis`)
  - Kafka Connect cluster for Redis operations
  - REST API on port 8084 for Redis sink management

- **RedPanda Console** (`redpanda-console`)
  - Web-based management interface on port 8080
  - Topic management, consumer groups, and schema browsing
  - Connector monitoring for both CDC and Redis clusters
  - Real-time data exploration and debugging

#### **🛠️ Management & Orchestration**

- **Management Container** (`management`)
  - Centralized control plane for all operations
  - Mounts scripts, configs, and environment files

#### **🌐 Network Architecture**

- **Internal Network** (`internal_nw`)
  - Isolated bridge network for service communication

## 🔧 How My Solution Works

### **Step 0: Clone and Setup**
First, clone the repository and navigate to the project directory:
```bash
git clone https://github.com/Y-55/thmanyah_assessment.git
cd thmanyah_assessment
```

### **Step 1: Deploy Infrastructure**
First, you need to deploy all the Docker Compose tools:
```bash
docker-compose up -d
```
This starts all services: RedPanda, PostgreSQL, ClickHouse, Redis, Debezium Connect, and RedPanda Console.

### **Step 1.5: Attach to Management Container**
Attach to the management container to run the initialization scripts:
```bash
docker exec -it management bash
```

### **Step 2: Initialize System**
Next, you need to initialize all the tables and and topics -and kafka streams- put some initial data:
```bash
./scripts/init.sh
```
This script:
- Creates database schemas in PostgreSQL
- Initializes RedPanda PostgreSQL connector (Debezium)
- Sets up ClickHouse landing tables
- Initializes ClickHouse Kafka transformation
- Configures Redis Kafka connector
- Initializes Redis with starting index
- Runs initial data simulation (100 events) to create Debezium auto-generated topics
- Starts Kafka Streams application

### **Step 3: Run Data Simulation**
After initialization, you can run the data simulator and watch the system in action:
```bash
./scripts/simulate_data_ingestion.sh
```
This generates realistic user interaction events and streams them through the entire pipeline.

### **Step 4: Monitor & Clear (Optional)**
- **Monitor**: Use RedPanda Console at http://localhost:8080 to watch data flow
- **Clear**: If you want to start fresh, you can clear everything:
```bash
./scripts/clear.sh
```


## Data Explainations 


## 🚀 Additional Scripts

### **Redis Queries (`scripts/redis/queries.py`)**
```bash
python run scripts/redis/queries.py
```
This script executes a specific Redis Search aggregation query:
- Queries the `idx:content_engagement_time` index
- Groups data by content type
- Counts total events and sums engagement seconds
- Returns results sorted by total engagement time (descending)
- Used to get the required analytics query results (معرفة المحتويات الأكثر تفاعلًا في آخر عشر دقائق)

### **Debezium Signals (`scripts/postgres/insert_debezium_signals.py`)**
```bash
python run scripts/postgres/insert_debezium_signals.py
```
This is the backfilling logic. Debezium provides a way to trigger a snapshot, which essentially lets you send a signal to initiate the process. This signal can be configured to come from Kafka, a database table, or other sources. In my case, I used a database table. This script inserts a snapshot signal into that table, instructing Debezium to backfill the data.


## 🔧 If I had more time
- I wanted to test ksqlDB for stream processing— it seemed really simple and similar to writing SQL queries, but I didn’t get the chance to evaluate it.
- I wanted to compare the real-time capabilities of ClickHouse's SummingMergeTree table with Redis.
- I wanted to refactor and clean up the entire codebase.
- I hoped to dive deeper into Kafka Streams — honestly, about 70% of my implementation was vibe coding.
- I also wanted to create a detailed comparison of the different strategies and setups I tried.

---

**Built by**: Yousef Abdulwahab
**Assessment Date**: January 2024
**Technologies Used**: Python, RedPanda, ClickHouse, Redis, PostgreSQL, Docker, Kafka - KafkaSrreams - KafkaConnectors, Java.
**Total Implementation Time**: 2-4 days



