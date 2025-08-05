# Data Ingestion Documentation

## Overview

This document describes the comprehensive data ingestion system implemented in the Social Media Analytics Dashboard. The system supports multiple data sources and transformation workflows to ensure data quality and consistency.

## 🔄 Data Ingestion Workflows

### 1. CSV Data Ingestion

#### Initial Setup
- **Source**: `backend/Social_Media_Engagement.csv`
- **Format**: CSV with social media post data
- **Automatic Trigger**: On backend startup if database is empty
- **Manual Trigger**: Via `/api/ingest-csv` endpoint

#### Recent Fixes Applied
- **Date Format Consistency**: Fixed date conversion to ensure proper string format for MongoDB schema
- **Schema Validation**: Updated schema to handle "Unknown" values in day_of_week and month fields
- **Error Handling**: Enhanced error handling for date parsing failures with fallback mechanisms
- **Data Transformation**: Improved transformation pipeline to handle edge cases gracefully

#### CSV Data Structure
```csv
platform,post_type,sentiment_score,likes,comments,shares,post_time
Facebook,text,positive,150,25,10,8/17/2023 14:45
Twitter,image,negative,75,15,5,8/18/2023 09:30
LinkedIn,video,neutral,200,40,20,8/19/2023 16:20
```

#### Ingestion Process
1. **File Reading**: Pandas reads CSV file
2. **Data Validation**: Schema validation and type checking
3. **Date Transformation**: `post_time` conversion to separate date/time columns
4. **Database Insertion**: Bulk insert into MongoDB collection
5. **Status Reporting**: Success/failure feedback

#### API Endpoint
```bash
POST /api/ingest-csv
```
**Response:**
```json
{
  "success": true,
  "message": "Data ingested successfully",
  "records_ingested": 1000,
  "ingestion_performed": true
}
```

### 2. Mock Data Generation

#### Background Scheduler
- **Framework**: APScheduler
- **Frequency**: Every 30 seconds (updated from 2 minutes)
- **Records per batch**: 5-15 records (randomized)
- **Realistic Patterns**: Platform-specific engagement patterns

#### Recent Fixes Applied
- **Date Format Standardization**: Changed mock data generator to use CSV format (`%m/%d/%Y %H:%M`) for consistency
- **Enhanced Error Handling**: Added comprehensive try-catch blocks in scheduler functions
- **Better Logging**: Improved logging for debugging scheduler issues with detailed error messages
- **Data Transformation**: Fixed date conversion pipeline to handle mock data properly
- **Scheduler Management**: Improved start/stop scheduler functionality with better error handling

#### Mock Data Characteristics
- **Platforms**: Facebook, Twitter, LinkedIn, Instagram
- **Post Types**: carousel, video, text, image, poll, story
- **Sentiment Scores**: positive, negative, neutral
- **Engagement Patterns**: Realistic likes, comments, shares
- **Time Patterns**: Business hours optimization

#### Scheduler Control
```bash
# Start scheduler
POST /api/start-scheduler

# Stop scheduler  
POST /api/stop-scheduler
```

### 3. Data Transformation Pipeline

#### Date/Time Processing
The system includes a sophisticated data transformation pipeline that converts `post_time` into separate `Posted_date` and `Posted_time` columns for better analytics.

#### Transformation Workflow
1. **Input**: `post_time` column (various formats)
2. **Processing**: `DataTransformer.convert_post_time_to_date_time()`
3. **Output**: 
   - `Posted_date`: YYYY-MM-DD format
   - `Posted_time`: HH:MM:SS format
   - `post_time`: ISO 8601 string format

#### Supported Input Formats
- **CSV Format**: `MM/DD/YYYY HH:MM` (e.g., "8/17/2023 14:45")
- **ISO Format**: `YYYY-MM-DDTHH:MM:SS` (e.g., "2023-08-17T14:45:00")

#### Transformation Code (Updated)
```python
def convert_post_time_to_date_time(self, df: pd.DataFrame, post_time_column: str = 'post_time') -> pd.DataFrame:
    """
    Convert post_time column into separate Posted_date and Posted_time columns.
    
    Args:
        df: Input DataFrame
        post_time_column: Name of the post_time column
        
    Returns:
        DataFrame with additional Posted_date and Posted_time columns
    """
    # Create temporary datetime column
    temp_datetime_col = f"temp_{post_time_column}"
    
    # Try CSV format first, then ISO format with better error handling
    try:
        df[temp_datetime_col] = pd.to_datetime(
            df[post_time_column], 
            format='%m/%d/%Y %H:%M',
            errors='coerce'
        )
    except Exception as e:
        logger.warning(f"Failed to parse with CSV format, trying ISO format: {e}")
        try:
            df[temp_datetime_col] = pd.to_datetime(
                df[post_time_column], 
                format='%Y-%m-%dT%H:%M:%S',
                errors='coerce'
            )
        except Exception as e2:
            logger.warning(f"Failed to parse with ISO format, trying auto-detect: {e2}")
            # Try auto-detect format
            df[temp_datetime_col] = pd.to_datetime(
                df[post_time_column], 
                errors='coerce'
            )
    
    # Check if conversion was successful and convert to string immediately
    if temp_datetime_col in df.columns and not df[temp_datetime_col].isna().all():
        # Extract date and time components and convert to string immediately
        df['Posted_date'] = df[temp_datetime_col].dt.strftime('%Y-%m-%d')
        df['Posted_time'] = df[temp_datetime_col].dt.strftime('%H:%M:%S')
        
        # Remove the temporary column
        df.drop(columns=[temp_datetime_col], inplace=True)
        
        logger.info(f"Successfully converted {post_time_column} to Posted_date and Posted_time columns")
    else:
        logger.warning(f"Failed to convert {post_time_column}, keeping original format")
        if temp_datetime_col in df.columns:
            df.drop(columns=[temp_datetime_col], inplace=True)
    
    return df
```

## 🗄️ Database Schema

### Collection Structure
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

### Schema Validation
```python
database_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["platform", "post_type", "sentiment_score", "likes", "comments", "shares", "post_time", "Posted_date", "Posted_time"],
            "properties": {
                "platform": {"enum": ["Facebook", "Twitter", "LinkedIn", "Instagram"]},
                "post_type": {"enum": ["carousel", "video", "text", "image", "poll", "story"]},
                "sentiment_score": {"enum": ["positive", "negative", "neutral"]},
                "likes": {"bsonType": "int", "minimum": 0},
                "comments": {"bsonType": "int", "minimum": 0},
                "shares": {"bsonType": "int", "minimum": 0},
                "post_time": {"bsonType": "string"},
                "Posted_date": {"bsonType": "string"},
                "Posted_time": {"bsonType": "string"}
            }
        }
    }
}
```

## 🔄 Auto-Ingestion Flow

### Backend Startup Process
1. **Database Connection**: Establish MongoDB connection
2. **Collection Check**: Verify if collection exists and has data
3. **Schema Validation**: Check if schema matches current definition
4. **Auto-Ingestion**: If collection is empty, automatically ingest CSV data
5. **Status Reporting**: Log ingestion results

### Frontend Integration
1. **Health Check**: Frontend calls `/health` endpoint
2. **Data Status**: Check if database has records
3. **Manual Trigger**: If needed, trigger `/api/ingest-csv`
4. **Status Update**: Update session state based on ingestion results

## 📊 Data Quality Assurance

### Validation Rules
- **Platform Validation**: Must be one of the 4 supported platforms
- **Post Type Validation**: Must be one of the 6 supported types
- **Sentiment Validation**: Must be positive, negative, or neutral
- **Engagement Validation**: Likes, comments, shares must be non-negative integers
- **Date Validation**: Posted_date must be in YYYY-MM-DD format
- **Time Validation**: Posted_time must be in HH:MM:SS format

### Error Handling
- **Missing Data**: Graceful handling of null/empty values
- **Format Errors**: Automatic format detection and conversion
- **Schema Violations**: Detailed error messages for validation failures
- **Connection Issues**: Retry logic for database connection problems

## 🔧 Configuration

### Environment Variables
```bash
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=social_media_analytics
MONGODB_COLLECTION=posts

# API Configuration  
BACKEND_API_URL=http://localhost:5000

# Scheduler Configuration
SCHEDULER_INTERVAL=120  # seconds
RECORDS_PER_BATCH=10
```

### File Paths
- **CSV File**: `backend/Social_Media_Engagement.csv`
- **Log Files**: Application logs with detailed ingestion tracking
- **Configuration**: Environment variables and configuration files

## 📈 Performance Optimization

### Bulk Operations
- **Batch Insertion**: Insert multiple records in single operation
- **Index Optimization**: MongoDB indexes on frequently queried fields
- **Memory Management**: Efficient DataFrame operations

### Caching Strategy
- **API Response Caching**: 5-minute cache for frequently accessed data
- **Session State**: Frontend session state for user preferences
- **Database Connection**: Connection pooling for better performance

## 🚨 Monitoring & Logging

### Ingestion Logs
```python
logger.info(f"Starting CSV ingestion from {csv_file}")
logger.info(f"Successfully ingested {records_ingested} records")
logger.error(f"Ingestion failed: {error_message}")
```

### Health Monitoring
- **Database Connection**: Regular health checks
- **Data Freshness**: Monitor last ingestion timestamp
- **Error Tracking**: Log and alert on ingestion failures

### Metrics Tracking
- **Records Processed**: Count of successfully ingested records
- **Processing Time**: Time taken for ingestion operations
- **Error Rate**: Percentage of failed ingestion attempts
- **Data Quality**: Validation success rate

## 🔄 Data Flow Diagram

```
CSV File → DataTransformer → Schema Validation → MongoDB
    ↓
Mock Data Generator → DataTransformer → Schema Validation → MongoDB
    ↓
Frontend Dashboard ← API Endpoints ← MongoDB Aggregation
```

## 🔧 Recent Fixes & Implementation Steps

### MongoDB Schema Validation Fixes

#### Issue: Date Format Validation Errors
**Problem**: MongoDB schema validation was failing because `Posted_date` was being sent as `datetime.date` objects instead of strings.

**Solution Applied**:
1. **Updated Transformation Code**: Changed date conversion to use `strftime()` instead of `.dt.date`
2. **Schema Updates**: Added "Unknown" values to enum lists for day_of_week and month fields
3. **Error Handling**: Enhanced error handling for date parsing failures

#### Implementation Steps:
```python
# Before (causing validation errors)
df['Posted_date'] = df[temp_datetime_col].dt.date
df['Posted_time'] = df[temp_datetime_col].dt.time

# After (fixed)
df['Posted_date'] = df[temp_datetime_col].dt.strftime('%Y-%m-%d')
df['Posted_time'] = df[temp_datetime_col].dt.strftime('%H:%M:%S')
```

### Scheduler Data Ingestion Fixes

#### Issue: Scheduler Failing to Generate Mock Data
**Problem**: Mock data generator was using ISO format dates but transformation expected CSV format.

**Solution Applied**:
1. **Date Format Standardization**: Changed mock data generator to use CSV format
2. **Enhanced Error Handling**: Added comprehensive try-catch blocks
3. **Better Logging**: Improved logging for debugging scheduler issues

#### Implementation Steps:
```python
# Before (inconsistent format)
"post_time": post_time.isoformat()

# After (consistent format)
"post_time": post_time.strftime('%m/%d/%Y %H:%M')
```

### API Endpoint Improvements

#### Enhanced Error Handling
- Added detailed error messages for troubleshooting
- Improved scheduler start/stop functionality
- Better health check validation

## 🛠️ Troubleshooting

### Common Issues

#### 1. CSV Ingestion Failures
```bash
# Check CSV file format
head -5 backend/Social_Media_Engagement.csv

# Verify file permissions
ls -la backend/Social_Media_Engagement.csv

# Test MongoDB connection
python -c "from backend.data_store import SocialMediaDataStore; store = SocialMediaDataStore(); store.connect()"
```

#### 2. Date Parsing Errors
```python
# Test date transformation
from backend.transformation import DataTransformer
import pandas as pd

df = pd.read_csv('backend/Social_Media_Engagement.csv')
transformer = DataTransformer()
result = transformer.convert_post_time_to_date_time(df)
print(result[['Posted_date', 'Posted_time']].head())
```

#### 3. Schema Validation Errors
```python
# Check schema compliance
from backend.data_store import SocialMediaDataStore
store = SocialMediaDataStore()
store.connect()
store.create_collection()  # This will validate schema
```

### Debug Commands
```bash
# Check MongoDB data
mongo social_media_analytics --eval "db.posts.count()"

# View recent records
mongo social_media_analytics --eval "db.posts.find().limit(5).pretty()"

# Check schema validation
mongo social_media_analytics --eval "db.getCollectionInfos()"
```

## 📋 Best Practices

### Data Ingestion
1. **Always validate data** before insertion
2. **Use bulk operations** for better performance
3. **Implement proper error handling** for all edge cases
4. **Log all operations** for debugging and monitoring
5. **Test with sample data** before production deployment

### Data Transformation
1. **Handle multiple date formats** gracefully
2. **Preserve original data** while adding derived fields
3. **Validate transformed data** before database insertion
4. **Use consistent naming conventions** for new fields
5. **Document transformation logic** for future maintenance

### Performance
1. **Use indexes** on frequently queried fields
2. **Implement connection pooling** for database operations
3. **Cache frequently accessed data** to reduce database load
4. **Monitor memory usage** during large data operations
5. **Use appropriate data types** for optimal storage

## 🔮 Future Enhancements

### Planned Features
- **Real-time Streaming**: Live data ingestion from external APIs
- **Data Versioning**: Track changes and maintain data history
- **Advanced Validation**: Machine learning-based data quality checks
- **Multi-source Ingestion**: Support for multiple data sources
- **Data Lineage**: Track data flow and transformations
- **Automated Testing**: Comprehensive test suite for ingestion workflows