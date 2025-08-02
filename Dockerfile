# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install MongoDB (for standalone container)
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list \
    && apt-get update \
    && apt-get install -y mongodb-org \
    && mkdir -p /data/db \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /data/db

# Expose ports
EXPOSE 27017 5000 8501

# Create a comprehensive startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Starting Social Media Analytics Application..."\n\
echo "================================================"\n\
\n\
# Function to check if MongoDB is running\n\
check_mongodb() {\n\
    echo "🔍 Checking MongoDB connection..."\n\
    for i in {1..30}; do\n\
        if python -c "import pymongo; pymongo.MongoClient(\"mongodb://localhost:27017/\", serverSelectionTimeoutMS=1000).admin.command(\"ping\")" 2>/dev/null; then\n\
            echo "✅ MongoDB is running"\n\
            return 0\n\
        fi\n\
        echo "⏳ Waiting for MongoDB... (attempt $i/30)"\n\
        sleep 2\n\
    done\n\
    echo "❌ MongoDB failed to start"\n\
    return 1\n\
}\n\
\n\
# Function to check if backend is running\n\
check_backend() {\n\
    echo "🔍 Checking backend API..."\n\
    for i in {1..30}; do\n\
        if curl -f http://localhost:5000/api/data >/dev/null 2>&1; then\n\
            echo "✅ Backend API is running"\n\
            return 0\n\
        fi\n\
        echo "⏳ Waiting for backend API... (attempt $i/30)"\n\
        sleep 2\n\
    done\n\
    echo "❌ Backend API failed to start"\n\
    return 1\n\
}\n\
\n\
# Start MongoDB in background\n\
echo "🗄️  Starting MongoDB..."\n\
mongod --fork --logpath /app/logs/mongodb.log --dbpath /data/db\n\
\n\
# Wait for MongoDB to be ready\n\
if ! check_mongodb; then\n\
    echo "❌ Failed to start MongoDB"\n\
    exit 1\n\
fi\n\
\n\
# Initialize database and collections\n\
echo "📊 Initializing database..."\n\
cd /app/backend && python -c "\n\
from data_store import SocialMediaDataStore\n\
data_store = SocialMediaDataStore()\n\
if data_store.connect():\n\
    data_store.create_collection()\n\
    print(\"✅ Database initialized\")\n\
else:\n\
    print(\"❌ Failed to initialize database\")\n\
    exit(1)\n\
"\n\
\n\
# Start data ingestion in background\n\
echo "📊 Starting data ingestion..."\n\
cd /app/backend && python data_ingest.py &\n\
INGESTION_PID=$!\n\
echo "✅ Data ingestion started (PID: $INGESTION_PID)"\n\
\n\
# Wait a moment for data ingestion to initialize\n\
sleep 3\n\
\n\
# Start the backend API\n\
echo "🔧 Starting backend API..."\n\
cd /app/backend && python app.py &\n\
BACKEND_PID=$!\n\
echo "✅ Backend API started (PID: $BACKEND_PID)"\n\
\n\
# Wait for backend to be ready\n\
if ! check_backend; then\n\
    echo "❌ Backend failed to start"\n\
    kill $INGESTION_PID 2>/dev/null || true\n\
    exit 1\n\
fi\n\
\n\
# Start the Streamlit frontend\n\
echo "🎨 Starting Streamlit frontend..."\n\
cd /app/frontend && streamlit run visualization.py --server.port 8501 --server.address 0.0.0.0 &\n\
FRONTEND_PID=$!\n\
echo "✅ Streamlit frontend started (PID: $FRONTEND_PID)"\n\
\n\
echo ""\n\
echo "🎉 All services started successfully!"\n\
echo "================================================"\n\
echo "📊 Dashboard: http://localhost:8501"\n\
echo "🔧 API: http://localhost:5000/api/data"\n\
echo "🗄️  MongoDB: localhost:27017"\n\
echo "================================================"\n\
echo "💡 To stop all services, press Ctrl+C"\n\
echo ""\n\
\n\
# Function to cleanup processes\n\
cleanup() {\n\
    echo ""\n\
    echo "🛑 Stopping all services..."\n\
    kill $FRONTEND_PID 2>/dev/null || true\n\
    kill $BACKEND_PID 2>/dev/null || true\n\
    kill $INGESTION_PID 2>/dev/null || true\n\
    echo "✅ All services stopped"\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup SIGINT SIGTERM\n\
\n\
# Monitor processes and keep running\n\
while true; do\n\
    # Check if processes are still running\n\
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then\n\
        echo "❌ Frontend process stopped unexpectedly"\n\
        break\n\
    fi\n\
    if ! kill -0 $BACKEND_PID 2>/dev/null; then\n\
        echo "❌ Backend process stopped unexpectedly"\n\
        break\n\
    fi\n\
    if ! kill -0 $INGESTION_PID 2>/dev/null; then\n\
        echo "❌ Data ingestion process stopped unexpectedly"\n\
        break\n\
    fi\n\
    sleep 5\n\
done\n\
\n\
# If we reach here, something went wrong\n\
echo "❌ One or more services stopped unexpectedly"\n\
cleanup\n\
' > /app/start.sh && chmod +x /app/start.sh

# Create a simple health check script
RUN echo '#!/bin/bash\n\
# Check if all services are running\n\
backend_ok=$(curl -f http://localhost:5000/api/data >/dev/null 2>&1 && echo "OK" || echo "FAIL")\n\
frontend_ok=$(curl -f http://localhost:8501 >/dev/null 2>&1 && echo "OK" || echo "FAIL")\n\
mongodb_ok=$(python -c "import pymongo; pymongo.MongoClient(\"mongodb://localhost:27017/\", serverSelectionTimeoutMS=1000).admin.command(\"ping\")" >/dev/null 2>&1 && echo "OK" || echo "FAIL")\n\
\n\
if [ "$backend_ok" = "OK" ] && [ "$frontend_ok" = "OK" ] && [ "$mongodb_ok" = "OK" ]; then\n\
    echo "All services healthy"\n\
    exit 0\n\
else\n\
    echo "Service health check failed: Backend=$backend_ok, Frontend=$frontend_ok, MongoDB=$mongodb_ok"\n\
    exit 1\n\
fi\n\
' > /app/health_check.sh && chmod +x /app/health_check.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV MONGODB_URI=mongodb://localhost:27017/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/health_check.sh

# Default command
CMD ["/app/start.sh"] 