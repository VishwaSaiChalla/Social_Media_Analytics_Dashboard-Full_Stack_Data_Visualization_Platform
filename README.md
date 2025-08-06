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

#### Option 1: Local Development

1. **Start MongoDB**
   ```bash
   # Start MongoDB service
   mongod
   ```

2. **Run Backend API**
   ```bash
   # Navigate to backend directory
   cd backend
   
   # Run Flask application
   python app.py
   ```

3. **Run Frontend Dashboard**
   ```bash
   # Navigate to frontend directory
   cd frontend
   
   # Run Streamlit dashboard
   streamlit run visualization.py
   ```

4. **Access the Application**
   - Dashboard: http://localhost:8501
   - API: http://localhost:5000

#### Option 2: Docker Setup

1. **Start all services with Docker Compose**
   ```bash
   # Build and start all services
   docker-compose up -d
   ```

2. **Stop all services**
   ```bash
   # Stop and remove containers
   docker-compose down
   ```

3. **Access the Application**
   - Dashboard: http://localhost:8501
   - API: http://localhost:5000
   - MongoDB: localhost:27017

### Troubleshooting Common Issues

#### MongoDB Connection Issues
If you encounter "Failed to initialize database. Please check MongoDB connection":

1. **Start MongoDB with Docker** (Recommended):
   ```bash
   docker-compose up -d datastore
   ```

2. **Check MongoDB Status**:
   ```bash
   docker-compose ps
   docker-compose logs datastore
   ```

3. **Restart Backend**:
   ```bash
   docker-compose restart backend
   ```

#### Scheduler Data Ingestion Issues
If the scheduler fails to ingest data:

1. **Check Backend Logs**:
   ```bash
   docker-compose logs backend --tail=50
   ```

2. **Restart Services**:
   ```bash
   docker-compose restart
   ```

3. **Test API Endpoints**:
   ```bash
   curl -X POST http://localhost:5000/api/start-scheduler
   curl http://localhost:5000/health
   ```

### Alternative Docker Commands

```bash
# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and start
docker-compose up --build -d

# Check service status
docker-compose ps
```

## ☁️ AWS Cloud Deployment

### Prerequisites
- AWS Account with EC2 access
- SSH key pair for EC2 instance
- Git repository with project

### EC2 Instance Setup

1. **Create EC2 Instance**
   - **Instance Type**: t2.micro (free tier eligible)
   - **Operating System**: Amazon Linux Base (AMI)
   - **Storage**: 8 GiB
   - **Security Group**: Configure with ports 80, 8501, 5000

2. **Security Group Configuration**
   ```
   Port 80: HTTP
   Port 8501: Streamlit Dashboard
   Port 5000: Flask API
   Port 22: SSH (default)
   ```

### Deployment Steps

1. **Connect to EC2 Instance**
   ```bash
   ssh -i /path/to/your-key.pem ec2-user@<your-ec2-public-ip>
   ```

2. **Update System Packages**
   ```bash
   sudo dnf update -y
   ```

3. **Install Docker**
   ```bash
   # Install Docker Engine
   sudo dnf install docker -y
   
   # Start Docker service
   sudo systemctl start docker
   
   # Enable Docker on boot
   sudo systemctl enable docker
   
   # Add user to docker group
   sudo usermod -aG docker ec2-user
   ```

4. **Install Git and Clone Repository**
   ```bash
   # Install Git
   sudo dnf install git -y
   
   # Clone your repository
   git clone https://github.com/VishwaSaiChalla/Technology_Intern_Take_Home_Submission.git
   
   # Navigate to project directory
   cd Technology_Intern_Take_Home_Submission
   ```

5. **Install Docker Compose**
   ```bash
   # Download Docker Compose binary
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   
   # Make it executable
   sudo chmod +x /usr/local/bin/docker-compose
   ```

6. **Deploy Application**
   ```bash
   # Start all services
   docker-compose up -d
   
   # Check application status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   ```

7. **Test Application Health**
   ```bash
   # Test API health
   curl http://localhost:5000/health
   
   # Test dashboard access
   curl http://localhost:8501
   ```

### Elastic IP Configuration

1. **Allocate Elastic IP**
   - Navigate to AWS Console → EC2 → Elastic IPs
   - Click "Allocate Elastic IP address"
   - Select your region

2. **Associate with EC2 Instance**
   - Select the allocated Elastic IP
   - Click "Associate Elastic IP address"
   - Choose your running EC2 instance
   - Select the private IP to associate

3. **Update Security Groups**
   - Ensure your security group allows inbound traffic on required ports
   - Update any DNS records if applicable

### Access Your Application

- **Dashboard**: `http://<your-elastic-ip>:8501/`
- **API**: `http://<your-elastic-ip>:5000/`
- **Health Check**: `http://<your-elastic-ip>:5000/health`

### Production Considerations

- **Load Balancer**: Consider using Application Load Balancer for high availability
- **Auto Scaling**: Set up auto scaling groups for traffic spikes
- **Monitoring**: Enable CloudWatch monitoring
- **Backup**: Regular EBS snapshots for data persistence
- **SSL/TLS**: Configure HTTPS for secure access
- **Domain**: Point a custom domain to your Elastic IP

### Troubleshooting AWS Deployment

1. **Connection Issues**
   ```bash
   # Check if Docker is running
   sudo systemctl status docker
   
   # Check container status
   docker-compose ps
   
   # View detailed logs
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Port Access Issues**
   - Verify security group rules
   - Check if application is listening on correct ports
   - Test local access: `curl http://localhost:8501`

3. **Resource Issues**
   - Monitor CPU and memory usage
   - Consider upgrading instance type if needed
   - Check EBS volume space

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
- **Platform Filter**: Select specific platforms or view all platforms
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
│   ├── app.py                      # Flask application
│   ├── data_store.py               # MongoDB operations
│   ├── data_ingest.py              # Data ingestion logic
│   ├── transformation.py            # Data transformation utilities
│   └── Social_Media_Engagement.csv # Sample data file
├── frontend/
│   └── visualization.py             # Streamlit dashboard
├── environ/                         # Environment files
├── requirements.txt                 # Python dependencies
├── docker-compose.yml              # Docker services configuration
├── Dockerfile                      # Docker image definition
├── dashboard.png                   # Dashboard screenshot
├── data-ingestion.md              # Data ingestion documentation
├── datastore-setup.md             # Database setup documentation
├── visualization.md                # Visualization documentation
└── README.md                      # This file
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

## 🔧 Recent Fixes & Improvements

### MongoDB Schema Validation Fixes
- **Date Format Consistency**: Fixed date conversion issues in transformation pipeline
- **Schema Validation**: Updated MongoDB schema to handle "Unknown" values
- **Error Handling**: Enhanced error handling for date parsing failures
- **Data Type Validation**: Ensured proper string format for Posted_date and Posted_time fields

### Scheduler Data Ingestion Fixes
- **Date Format Standardization**: Changed mock data generator to use CSV format (`%m/%d/%Y %H:%M`)
- **Enhanced Error Handling**: Added comprehensive error handling in scheduler functions
- **Better Logging**: Improved logging for debugging scheduler issues
- **Data Transformation**: Fixed date conversion pipeline for mock data

### API Endpoint Improvements
- **Health Check Enhancement**: Better database connection validation
- **Error Response**: More detailed error messages for troubleshooting
- **Scheduler Management**: Improved start/stop scheduler functionality
- **Data Validation**: Enhanced validation before database insertion

## 🚀 Complete Development Journey & Implementation Steps

### Phase 1: Data Infrastructure & Database Setup

#### Dataset Selection & Initial Setup:
- **Source**: Selected Social_Media_Engagement.csv dataset from Kaggle
- **Database Choice**: MongoDB for flexibility with JSON-like documents
- **Schema Design**: Created comprehensive schema file for data validation
- **Connection**: Implemented PyMongo with MongoClient for database connectivity

#### Data Ingestion Implementation:
1. **CRUD Operations**: Implemented basic Create, Read, Update, Delete operations
2. **Testing**: Verified correct data insertion into database
3. **CSV Ingestion**: Developed `ingest_from_csv` method for CSV file loading
4. **Mock Data Generation**: Created method to generate random values for likes, comments, shares
5. **Scheduled Ingestion**: Implemented 30-second automated data ingestion
6. **Validation**: Ensured all incoming data adhered to schema validation rules

### Phase 2: Visualization & Frontend Development

#### Technology Stack Evolution:
- **Initial Approach**: Simple main functions with kernel testing
- **Advanced Integration**: REST API development skills integration
- **Modular Architecture**: Separated frontend and backend components
- **Frontend Choice**: Power BI dashboards for effective visualization

#### Power BI Implementation Process:

##### Database Connection Strategy:
1. **Challenge**: Power BI lacks native MongoDB connector
2. **Research**: Extensive investigation for viable solutions
3. **Solution**: BI Connector extension with ODBC connector
4. **Configuration**: MongoDB client connection through ODBC driver
5. **Advantage**: Real-time data refresh vs. static CSV approach

##### ETL Process Implementation:
1. **Data Cleaning**: Removed duplicates and standardized formats
2. **Field Renaming**: Enhanced clarity for better visualization
3. **Date/Time Splitting**: Separated fields for granular analysis
4. **Data Dictionary**: Comprehensive field documentation and context

##### Dashboard Architecture:
**Modular Design Approach**:
1. **Engagement Analysis Module**:
   - KPI metrics and performance indicators
   - Clustered bar charts for platform engagement
   - Day-of-week engagement patterns
   - Temporal trend analysis with date hierarchies
   - Heatmaps for pattern visualization

2. **Sentiment Analysis Module**:
   - Donut charts for platform-specific sentiment distribution
   - Bar charts for post-type sentiment analysis
   - Line charts for engagement trends by platform
   - Sentiment correlation analysis

3. **Content Performance Module**:
   - Bar charts for content type performance
   - Tree-maps for platform hierarchy visualization
   - Content effectiveness metrics
   - Performance benchmarking

##### DAX Measures Implementation:
- **Dynamic Platform Counts**: Platform-specific aggregation logic
- **Intelligent Metrics**: Business logic-driven calculations
- **Contextual Measures**: Time-based and categorical analysis
- **Performance Indicators**: Engagement ratios and growth metrics

### Phase 3: Frontend Integration & Real-time Features

#### Streamlit Integration:
- **Technology**: Plotly for interactive visualizations
- **Layout Design**: Automatic database initialization at startup
- **API Integration**: Multiple endpoints for data verification and loading
- **Real-time Updates**: 30-second automatic page refresh

#### Scheduler Implementation:
- **Technology**: Python APScheduler for automated data insertion
- **Frequency**: 30-second intervals for mock data generation
- **User Control**: Manual trigger buttons for data insertion
- **Live Updates**: Real-time visualization updates

### Phase 4: Code Architecture & Development Workflow

#### Modular Structure:
```
Frontend: visualization.py (Streamlit + Plotly)
Backend: app.py (API routing and processing)
Data Layer: data_store.py (MongoDB queries with PyMongo)
```

#### Development Environment Setup:
1. **Virtual Environment**: Dedicated Python environment
2. **Dependencies**: Comprehensive requirements.txt documentation
3. **Multi-terminal Development**: MongoDB, Frontend, Backend separation
4. **Containerization**: Docker implementation for streamlined deployment

### Phase 5: Containerization & Cloud Deployment

#### Docker Implementation:
- **Frontend Container**: Streamlit application containerization
- **Backend Container**: Flask API containerization
- **Database Container**: MongoDB containerization
- **Orchestration**: docker-compose.yml for multi-container management

#### AWS Cloud Deployment:

##### EC2 Instance Setup:
- **Instance Name**: "Social_Media_Analysis"
- **Operating System**: Amazon Linux Base (AMI)
- **Instance Type**: t2.micro
- **Storage**: 8 GiB configuration
- **Security Group**: Ports 80, 8501, 5000 enabled

##### Server Configuration:
```bash
# System updates
sudo dnf update -y

# Docker installation and setup
sudo dnf install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Git installation and repository cloning
sudo dnf install git -y
git clone https://github.com/VishwaSaiChalla/Technology_Intern_Take_Home_Submission.git

# Docker Compose setup
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

##### Application Deployment:
- **Container Launch**: `docker compose up -d`
- **Health Monitoring**: `docker-compose logs -f`
- **Port Exposure**: `http://<EC2_Private_IP_Address>:8501`

##### Elastic IP Configuration:
- **Static IP Allocation**: AWS Management Console configuration
- **IP Association**: Persistent public IP for reliable access
- **DNS Integration**: Domain name linking capability
- **Security Configuration**: Inbound traffic allowance on necessary ports

### Phase 6: Testing & Optimization

#### Performance Testing:
- **Load Testing**: Container performance under various loads
- **Database Performance**: MongoDB query optimization
- **API Response Times**: Endpoint performance monitoring
- **Real-time Updates**: Scheduler and refresh mechanism testing

#### User Experience Optimization:
- **Interface Refinement**: Streamlit layout improvements
- **Responsive Design**: Multi-device compatibility
- **Error Handling**: Graceful failure management
- **Documentation**: Complete technical and user guides

## 🔮 Future Enhancements

- **Advanced Analytics**: Machine learning insights
- **Export Functionality**: PDF/Excel report generation
- **User Authentication**: Multi-user support
- **Real-time Streaming**: Live data ingestion
- **Mobile App**: Native mobile application
- **Advanced Filters**: Date range, custom metrics
- **Alert System**: Threshold-based notifications
