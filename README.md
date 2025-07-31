# Social Media Analytics Dashboard

A comprehensive data visualization project that demonstrates working with databases, data ingestion, and real-time analytics visualization.

## 🚀 Project Overview

This project implements a complete data pipeline for social media analytics:

- **Datastore**: MongoDB for flexible NoSQL data storage
- **Data Ingestion**: Real-time mock data generation with realistic patterns
- **Backend API**: Flask REST API serving data to the frontend
- **Frontend Dashboard**: Interactive Streamlit dashboard with real-time updates
- **Real-time Analytics**: Live data processing and insights
- **Containerization**: Docker setup for easy deployment

## 📋 Features

### Core Requirements ✅
- **Datastore Setup**: MongoDB with schema validation
- **Data Ingestion**: Mock data generation with realistic social media patterns
- **Visualization**: Interactive dashboard with multiple chart types
- **Documentation**: Comprehensive markdown files explaining each component

### Bonus Features 🔥
- **Docker Containerization**: Complete containerized setup
- **Real-time Analytics**: Live data processing and insights
- **Real-time Updates**: Live data ingestion and dashboard updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Datastore     │
│  (Streamlit)    │◄──►│   (Flask API)   │◄──►│   (MongoDB)     │
│   Port: 8501    │    │   Port: 5000    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Data Ingestion  │
                    │ (Real-time)     │
                    └─────────────────┘
```

## 🛠️ Technology Stack

- **Database**: MongoDB (NoSQL)
- **Backend**: Flask (Python)
- **Frontend**: Streamlit (Python)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Containerization**: Docker, Docker Compose
- **Real-time**: APScheduler

## 🚀 Quick Start

### Option 1: Docker (Recommended)

#### Method A: Single Container (Easiest)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd takehomeproject
   ```

2. **Run the application**
   
   **On Windows:**
   ```bash
   run-docker.bat start
   ```
   
   **On Linux/Mac:**
   ```bash
   chmod +x run-docker.sh
   ./run-docker.sh start
   ```

3. **Access the applications**
   - Dashboard: http://localhost:8501
   - API: http://localhost:5000/api/data
   - MongoDB: localhost:27017

#### Method B: Docker Compose (Multi-container)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd takehomeproject
   ```

2. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the applications**
   - Dashboard: http://localhost:8501
   - API: http://localhost:5000/api/data
   - MongoDB: localhost:27017

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start MongoDB**
   ```bash
   # Install MongoDB locally or use Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

3. **Run the backend API**
   ```bash
   cd backend
   python app.py
   ```

4. **Run data ingestion (in another terminal)**
   ```bash
   cd src
   python data_ingest.py
   ```

5. **Run the frontend dashboard**
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

## 📊 Dashboard Features

### Interactive Analytics
- **Real-time Metrics**: Live updates of engagement statistics
- **Platform Comparison**: Performance analysis across social media platforms
- **Time Series Analysis**: Trends over time with interactive charts
- **Sentiment Analysis**: Sentiment distribution and platform-specific insights
- **Data Filtering**: Filter by platform, date range, and search terms

### Visualization Types
- **Bar Charts**: Platform performance comparison
- **Pie Charts**: Post type and sentiment distribution
- **Line Charts**: Time series trends
- **Heatmaps**: Hourly performance patterns
- **Scatter Plots**: Engagement correlations

## 📁 Project Structure

```
takehomeproject/
├── backend/
│   └── app.py                 # Flask API server
├── frontend/
│   └── streamlit_app.py       # Streamlit dashboard
├── src/
│   ├── data_ingest.py         # Data ingestion script
│   ├── data_store.py          # MongoDB schema and setup
│   └── main.py                # Data ingestion trigger
├── docker-compose.yml         # Docker services configuration
├── Dockerfile                 # Application container
├── requirements.txt           # Python dependencies
├── datastore-setup.md        # Database setup documentation
├── data-ingestion.md         # Data ingestion documentation
├── visualization.md           # Visualization documentation
└── README.md                 # This file
```

## 🔧 API Endpoints

### Backend API (Flask)
- `GET /api/data` - Get all social media posts
- `GET /api/stats` - Get aggregated statistics
- `GET /api/trends` - Get time-based trends
- `GET /api/platform/<platform>` - Get data for specific platform

### Example Usage
```bash
# Get all data
curl http://localhost:5000/api/data

# Get statistics
curl http://localhost:5000/api/stats

# Get trends
curl http://localhost:5000/api/trends
```

## 📈 Data Schema

### Social Media Posts Collection
```json
{
  "platform": "Facebook|Twitter|Instagram|LinkedIn",
  "post_type": "text|image|video|poll|carousel|story",
  "post_time": "2024-01-01T10:30:00",
  "likes": 150,
  "comments": 25,
  "shares": 10,
  "post_day": "Monday",
  "sentiment_score": "positive|negative|neutral"
}
```

## 🔄 Real-time Features

### Data Ingestion
- **Scheduled Updates**: New data every 2 minutes
- **Realistic Patterns**: Platform-specific engagement patterns
- **Time-based Generation**: More posts during business hours
- **Sentiment Correlation**: Higher engagement correlates with positive sentiment

### Dashboard Updates
- **Live Metrics**: Real-time engagement statistics
- **Auto-refresh**: Dashboard updates automatically
- **Caching**: Optimized data fetching with 5-minute cache

## 🐳 Docker Services

### Services Overview
1. **datastore**: MongoDB database
2. **backend**: Flask API server
3. **frontend**: Streamlit dashboard
4. **data_ingestion**: Real-time data generation

### Docker Commands

#### Single Container Commands
```bash
# Build and start the application
./run-docker.sh start          # Linux/Mac
run-docker.bat start           # Windows

# View application logs
./run-docker.sh logs           # Linux/Mac
run-docker.bat logs            # Windows

# Check application status
./run-docker.sh status         # Linux/Mac
run-docker.bat status          # Windows

# Stop the application
./run-docker.sh stop           # Linux/Mac
run-docker.bat stop            # Windows

# Restart the application
./run-docker.sh restart        # Linux/Mac
run-docker.bat restart         # Windows
```

#### Docker Compose Commands
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build
```

## 📊 Sample Data

The system generates realistic social media data with:
- **4 Platforms**: Facebook, Twitter, Instagram, LinkedIn
- **6 Post Types**: text, image, video, poll, carousel, story
- **Realistic Engagement**: Platform-specific patterns
- **Time Patterns**: Business hours optimization
- **Sentiment Analysis**: Engagement-based sentiment

## 🔍 Monitoring & Logs

### Application Logs
```bash
# View all container logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs data_ingestion
```

### Health Checks
- Backend API: http://localhost:5000/api/data
- Frontend Dashboard: http://localhost:8501
- MongoDB: localhost:27017

## 🛠️ Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :5000
   netstat -tulpn | grep :8501
   ```

2. **MongoDB Connection**
   ```bash
   # Test MongoDB connection
   docker exec -it mongo_db mongosh
   ```

3. **Dependencies Issues**
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose up --build
   ```

### Performance Optimization
- **Data Caching**: 5-minute cache for API responses
- **Batch Processing**: Efficient bulk data insertion
- **Indexing**: MongoDB indexes on frequently queried fields

## 📚 Documentation Files

- **datastore-setup.md**: MongoDB setup and schema details
- **data-ingestion.md**: Data generation and ingestion process
- **visualization.md**: Dashboard features and usage

## 🎯 Key Achievements

✅ **Complete Data Pipeline**: End-to-end data flow from generation to visualization
✅ **Real-time Updates**: Live data ingestion and dashboard updates
✅ **Interactive Dashboard**: Rich visualizations with filtering capabilities
✅ **Containerized Setup**: Easy deployment with Docker
✅ **Real-time Analytics**: Live data processing and insights
✅ **Scalable Architecture**: Microservices design with clear separation

## 🚀 Next Steps

Potential enhancements:
- **Authentication**: User login and role-based access
- **Advanced Analytics**: Machine learning insights
- **Data Export**: Multiple format support (CSV, JSON, Excel)
- **Alerts**: Custom notification system
- **Multi-tenancy**: Support for multiple organizations

---

**Built with ❤️ using Python, MongoDB, Flask, Streamlit, and Docker**