# Social Media Analytics Dashboard

A comprehensive social media analytics platform that provides real-time insights into social media engagement, sentiment analysis, and performance metrics across multiple platforms.

## 🚀 Features

### 📊 Analytics Dashboard
- **Real-time KPI Metrics**: Total posts, platform-specific post counts
- **Engagement Analytics**: Total engagement by platform and average engagement by day
- **Sentiment Analysis**: Sentiment distribution across platforms and post types
- **Trend Analysis**: Average likes, comments, and shares over time
- **Shares Analysis**: Detailed shares breakdown by post type
- **Decomposition Tree**: Hierarchical visualization with interactive filters

### 🔧 Technical Features
- **RESTful API**: Flask-based backend with comprehensive endpoints
- **MongoDB Integration**: Robust data storage with schema validation
- **Real-time Data Ingestion**: CSV data import and mock data generation
- **Interactive Visualizations**: Plotly Express charts with filtering capabilities
- **Auto-refresh**: Automatic dashboard updates every 30 seconds
- **Background Scheduler**: Continuous mock data generation

## 🏗️ Architecture

### Backend (Flask + MongoDB)
- **Flask Application**: RESTful API endpoints for data retrieval
- **MongoDB Database**: Document-based storage with schema validation
- **Data Transformation**: Automated date/time parsing and conversion
- **Background Tasks**: APScheduler for mock data generation

### Frontend (Streamlit + Plotly)
- **Streamlit Dashboard**: Interactive web interface
- **Plotly Express**: Rich visualizations with hover effects
- **Session Management**: State persistence across interactions
- **Error Handling**: Graceful error management and user feedback

## 📈 Visualizations

### 1. Engagement Analytics
- **Platform Engagement**: Stacked bar chart showing likes, comments, shares by platform
- **Daily Engagement**: Average engagement metrics by day of the week

### 2. Sentiment Analysis
- **Platform Sentiment**: Stacked bar chart showing sentiment distribution by platform
- **Post Type Sentiment**: Stacked column chart showing sentiment by post type
- **Donut Charts**: Individual sentiment breakdown for each platform

### 3. Trend Analysis
- **Average Likes Trend**: Line chart showing average likes over time by platform
- **Average Comments Trend**: Line chart showing average comments over time by platform
- **Average Shares Trend**: Line chart showing average shares over time by platform

### 4. Shares Analysis
- **Shares by Post Type**: Clustered bar chart showing total shares by post type
- **Average Shares Trend**: Line chart showing shares trend over time

### 5. Decomposition Tree (Treemap)
- **Hierarchical View**: Platform → Post Type → Sentiment Score
- **Interactive Filters**: Platform and post type filtering
- **Color Coding**: Based on total posts count
- **Hover Information**: Shows likes, comments, and shares at each level

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB
- Docker (optional)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd takehomeproject

# Install dependencies
pip install -r requirements.txt

# Start MongoDB (if not running)
mongod

# Run the application
python -m streamlit run frontend/visualization.py
```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📊 Data Structure

### Database Schema
```json
{
  "platform": "string",
  "post_type": "string", 
  "sentiment_score": "string",
  "likes": "number",
  "comments": "number",
  "shares": "number",
  "post_time": "string (ISO 8601)",
  "Posted_date": "string (YYYY-MM-DD)",
  "Posted_time": "string (HH:MM:SS)"
}
```

### Supported Platforms
- Facebook
- Twitter
- LinkedIn
- Instagram

### Supported Post Types
- Carousel
- Video
- Text
- Image
- Poll
- Story

### Sentiment Categories
- Positive
- Negative
- Neutral

## 🔌 API Endpoints

### Core Endpoints
- `GET /health` - Health check and database status
- `GET /api/stats` - Database statistics
- `POST /api/ingest-csv` - CSV data ingestion
- `POST /api/reset-database` - Database reset and re-ingestion

### Analytics Endpoints
- `GET /api/platform-engagement` - Platform engagement data
- `GET /api/engagement-by-day` - Daily engagement metrics
- `GET /api/sentiment-by-platform` - Sentiment by platform
- `GET /api/sentiment-by-post-type` - Sentiment by post type
- `GET /api/average-likes-by-date-platform` - Average likes trends
- `GET /api/average-comments-by-date-platform` - Average comments trends
- `GET /api/average-shares-by-date-platform` - Average shares trends
- `GET /api/shares-by-post-type` - Shares by post type
- `GET /api/decomposition-tree` - Hierarchical data for treemap

### Scheduler Endpoints
- `POST /api/start-scheduler` - Start mock data generation
- `POST /api/stop-scheduler` - Stop mock data generation

## 🎯 Usage

### Dashboard Navigation
1. **KPI Metrics**: View total posts and platform-specific counts
2. **Engagement Analytics**: Analyze engagement patterns across platforms
3. **Sentiment Analysis**: Explore sentiment distribution and trends
4. **Trend Analysis**: Monitor engagement metrics over time
5. **Shares Analysis**: Deep dive into shares performance
6. **Decomposition Tree**: Interactive hierarchical analysis with filters

### Filtering Options
- **Platform Filter**: Select specific platforms or view all
- **Post Type Filter**: Filter by content type
- **Date Range**: Automatic date-based filtering in trend charts
- **Real-time Updates**: Auto-refresh every 30 seconds

## 🔄 Data Flow

### Initial Setup
1. **Database Connection**: MongoDB connection establishment
2. **Schema Validation**: Automatic schema creation and validation
3. **CSV Ingestion**: Initial data import from CSV file
4. **Data Transformation**: Date/time parsing and conversion
5. **Dashboard Initialization**: Streamlit app startup

### Real-time Operations
1. **API Calls**: Frontend requests data from backend
2. **Data Processing**: MongoDB aggregation pipelines
3. **Visualization**: Plotly Express chart generation
4. **User Interaction**: Filter application and chart updates
5. **Auto-refresh**: Periodic data updates

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -c "from app import BackendApp; app = BackendApp(); print('Backend initialized successfully')"
```

### Frontend Testing
```bash
streamlit run frontend/visualization.py
```

## 📁 Project Structure

```
takehomeproject/
├── backend/
│   ├── app.py              # Flask application
│   ├── data_store.py       # MongoDB operations
│   ├── data_ingest.py      # Data ingestion logic
│   ├── transformation.py    # Data transformation utilities
│   └── Social_Media_Engagement.csv
├── frontend/
│   └── visualization.py     # Streamlit dashboard
├── requirements.txt         # Python dependencies
├── docker-compose.yml      # Docker configuration
├── Dockerfile             # Docker image definition
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation files
2. Review the API endpoints
3. Check MongoDB connection
4. Verify data ingestion status

## 🔮 Future Enhancements

- **Advanced Analytics**: Machine learning insights
- **Export Functionality**: PDF/Excel report generation
- **User Authentication**: Multi-user support
- **Real-time Streaming**: Live data ingestion
- **Mobile App**: Native mobile application
- **Advanced Filters**: Date range, custom metrics
- **Alert System**: Threshold-based notifications