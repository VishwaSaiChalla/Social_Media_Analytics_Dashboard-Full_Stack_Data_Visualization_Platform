# Datastore Setup Documentation

## Overview

This document describes the comprehensive MongoDB datastore setup for the Social Media Analytics Dashboard. The system includes automatic schema management, data validation, and transformation workflows to ensure data integrity and consistency.

## 🗄️ Database Architecture

### MongoDB Configuration
- **Database**: `social_media_analytics`
- **Collection**: `posts`
- **Connection**: MongoDB URI with connection pooling
- **Schema Validation**: JSON Schema with strict validation rules

### Connection Management
```python
class SocialMediaDataStore:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('MONGODB_DATABASE', 'social_media_analytics')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'posts')
```

## 📋 Database Schema

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

### Schema Validation (Updated)
```python
database_schema = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": [
                "platform", "post_type", "sentiment_score", 
                "likes", "comments", "shares", "post_time",
                "Posted_date", "Posted_time"
            ],
            "properties": {
                "platform": {
                    "enum": ["Facebook", "Twitter", "LinkedIn", "Instagram"]
                },
                "post_type": {
                    "enum": ["carousel", "video", "text", "image", "poll", "story"]
                },
                "sentiment_score": {
                    "enum": ["positive", "negative", "neutral"]
                },
                "likes": {
                    "bsonType": "int",
                    "minimum": 0
                },
                "comments": {
                    "bsonType": "int",
                    "minimum": 0
                },
                "shares": {
                    "bsonType": "int",
                    "minimum": 0
                },
                "post_time": {
                    "bsonType": "string"
                },
                "Posted_date": {
                    "bsonType": "string"
                },
                "Posted_time": {
                    "bsonType": "string"
                },
                "posted_day_of_week": {
                    "bsonType": "string",
                    "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Unknown"]
                },
                "posted_month": {
                    "bsonType": "string",
                    "enum": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Unknown"]
                }
            }
        }
    }
}
```

## 🔄 Auto-Schema Management

### Schema Update Detection
The system automatically detects schema changes and handles database updates:

```python
def create_collection(self):
    """Create collection with schema validation and auto-update"""
    try:
        # Check if collection exists
        if self.collection_name in self.db.list_collection_names():
            # Get current validator
            current_validator = self.db.command("listCollections", 
                                              filter={"name": self.collection_name})
            
            # Compare schemas
            if self._schemas_differ(current_validator, self.database_schema):
                logger.info("Schema change detected. Recreating collection...")
                self.db.drop_collection(self.collection_name)
                self._create_collection_with_schema()
            else:
                logger.info("Schema unchanged. Using existing collection.")
        else:
            logger.info("Creating new collection with schema validation.")
            self._create_collection_with_schema()
            
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        raise
```

### Schema Comparison Logic
```python
def _schemas_differ(self, current_validator, new_schema):
    """Compare current and new schema definitions"""
    try:
        current_schema = current_validator[0]['options'].get('validator', {})
        return current_schema != new_schema.get('validator', {})
    except (KeyError, IndexError):
        return True  # Assume different if comparison fails
```

## 🔧 Database Operations

### Connection Management
```python
def connect(self):
    """Establish MongoDB connection with error handling"""
    try:
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.database_name]
        self.collection = self.db[self.collection_name]
        
        # Test connection
        self.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

def disconnect(self):
    """Close MongoDB connection"""
    if self.client:
        self.client.close()
        logger.info("MongoDB connection closed")
```

### Data Insertion
```python
def insert_data(self, data):
    """Insert data with validation and transformation"""
    try:
        # Transform data if needed
        if isinstance(data, pd.DataFrame):
            data = self._transform_dataframe(data)
        
        # Validate data against schema
        self._validate_data(data)
        
        # Insert data
        if isinstance(data, list):
            result = self.collection.insert_many(data)
        else:
            result = self.collection.insert_one(data)
            
        logger.info(f"Successfully inserted {len(data) if isinstance(data, list) else 1} records")
        return result
        
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        raise
```

### Data Transformation
```python
def _transform_dataframe(self, df):
    """Transform DataFrame to list of dictionaries"""
    # Apply date transformation
    transformer = DataTransformer()
    df = transformer.convert_post_time_to_date_time(df)
    
    # Convert to list of dictionaries
    return df.to_dict('records')
```

## 📊 Aggregation Pipelines

### Platform Engagement
```python
def get_platform_engagement(self):
    """Get total engagement by platform"""
    pipeline = [
        {'$group': {
            '_id': '$platform',
            'total_likes': {'$sum': '$likes'},
            'total_comments': {'$sum': '$comments'},
            'total_shares': {'$sum': '$shares'}
        }},
        {'$sort': {'total_likes': -1}}
    ]
    return list(self.collection.aggregate(pipeline))
```

### Sentiment Analysis
```python
def get_sentiment_by_platform(self):
    """Get sentiment distribution by platform"""
    pipeline = [
        {'$group': {
            '_id': '$platform',
            'sentiments': {
                '$push': {
                    'sentiment': '$sentiment_score',
                    'count': 1
                }
            }
        }},
        {'$project': {
            'sentiments': {
                '$reduce': {
                    'input': '$sentiments',
                    'initialValue': [],
                    'in': {
                        '$concatArrays': [
                            '$$value',
                            [{'sentiment': '$$this.sentiment', 'count': 1}]
                        ]
                    }
                }
            }
        }}
    ]
    return list(self.collection.aggregate(pipeline))
```

### Trend Analysis
```python
def get_average_likes_by_date_platform(self):
    """Get average likes by date and platform"""
    pipeline = [
        {'$group': {
            '_id': {
                'date': '$Posted_date',
                'platform': '$platform'
            },
            'avg_likes': {'$avg': '$likes'},
            'total_posts': {'$sum': 1}
        }},
        {'$sort': {'_id.date': 1, '_id.platform': 1}}
    ]
    return list(self.collection.aggregate(pipeline))
```

### Decomposition Tree
```python
def get_decomposition_tree_data(self, platform_filter=None, post_type_filter=None):
    """Get hierarchical data for treemap"""
    pipeline = []
    
    # Add filters if provided
    match_stage = {}
    if platform_filter:
        match_stage['platform'] = platform_filter
    if post_type_filter:
        match_stage['post_type'] = post_type_filter
    
    if match_stage:
        pipeline.append({'$match': match_stage})
    
    # Group by hierarchy
    pipeline.extend([
        {'$group': {
            '_id': {
                'platform': '$platform',
                'post_type': '$post_type',
                'sentiment_score': '$sentiment_score'
            },
            'total_posts': {'$sum': 1},
            'total_likes': {'$sum': '$likes'},
            'total_comments': {'$sum': '$comments'},
            'total_shares': {'$sum': '$shares'}
        }},
        {'$sort': {
            '_id.platform': 1,
            '_id.post_type': 1,
            '_id.sentiment_score': 1
        }}
    ])
    
    return list(self.collection.aggregate(pipeline))
```

## 🔄 Database Reset Operations

### Complete Reset
```python
def reset_database_with_schema(self, csv_file_path):
    """Reset database and re-ingest data"""
    try:
        # Drop existing collection
        self.db.drop_collection(self.collection_name)
        logger.info("Dropped existing collection")
        
        # Recreate collection with current schema
        self._create_collection_with_schema()
        logger.info("Recreated collection with current schema")
        
        # Re-ingest data
        success = self.ingest_data_from_csv(csv_file_path)
        
        if success:
            logger.info("Database reset and re-ingestion completed successfully")
            return True
        else:
            logger.error("Database reset failed during re-ingestion")
            return False
            
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return False
```

### API Endpoint
```python
@self.app.route('/api/reset-database', methods=['POST'])
def reset_database():
    """Reset database and re-ingest data"""
    try:
        csv_file = 'backend/Social_Media_Engagement.csv'
        success = self.data_store.reset_database_with_schema(csv_file)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Database reset and re-ingestion completed successfully'
            })
        else:
            return jsonify({'error': 'Database reset failed'}), 500
            
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return jsonify({'error': str(e)}), 500
```

## 📈 Performance Optimization

### Indexing Strategy
```python
def create_indexes(self):
    """Create indexes for optimal query performance"""
    try:
        # Platform index for filtering
        self.collection.create_index("platform")
        
        # Date index for time-based queries
        self.collection.create_index("Posted_date")
        
        # Compound index for platform + date queries
        self.collection.create_index([("platform", 1), ("Posted_date", 1)])
        
        # Post type index
        self.collection.create_index("post_type")
        
        # Sentiment index
        self.collection.create_index("sentiment_score")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
```

### Connection Pooling
```python
def __init__(self):
    self.client = None
    self.db = None
    self.collection = None
    
    # Connection pooling configuration
    self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    self.database_name = os.getenv('MONGODB_DATABASE', 'social_media_analytics')
    self.collection_name = os.getenv('MONGODB_COLLECTION', 'posts')
    
    # Connection pool settings
    self.client_options = {
        'maxPoolSize': 10,
        'minPoolSize': 1,
        'maxIdleTimeMS': 30000,
        'serverSelectionTimeoutMS': 5000,
        'connectTimeoutMS': 10000
    }
```

## 🔧 Recent Fixes & Implementation Steps

### MongoDB Schema Validation Fixes

#### Issue: Document Validation Errors
**Problem**: MongoDB was rejecting documents due to schema validation errors, specifically:
- `Posted_date` being sent as `datetime.date` objects instead of strings
- Missing "Unknown" values in enum lists for day_of_week and month fields

**Solution Applied**:
1. **Date Format Fix**: Updated transformation code to convert dates to strings immediately
2. **Schema Updates**: Added "Unknown" values to enum lists for better error handling
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

### Data Transformation Improvements

#### Enhanced Date Conversion
- Added multiple format detection (CSV, ISO, auto-detect)
- Improved error handling with fallback mechanisms
- Better logging for debugging transformation issues

#### Schema Validation Updates
- Added "Unknown" values to enum lists for day_of_week and month fields
- Enhanced validation to handle edge cases gracefully
- Improved error messages for validation failures

### Connection Management Improvements

#### Better Error Handling
- Enhanced connection error messages
- Improved retry logic for connection failures
- Better logging for debugging connection issues

## 🚨 Error Handling

### Connection Errors
```python
def handle_connection_error(self, error):
    """Handle MongoDB connection errors"""
    if "Connection refused" in str(error):
        logger.error("MongoDB server is not running")
        return "MongoDB server is not running. Please start MongoDB."
    elif "Authentication failed" in str(error):
        logger.error("MongoDB authentication failed")
        return "MongoDB authentication failed. Check credentials."
    else:
        logger.error(f"Unknown connection error: {error}")
        return f"Database connection error: {error}"
```

### Schema Validation Errors
```python
def handle_validation_error(self, error):
    """Handle schema validation errors"""
    if "Document failed validation" in str(error):
        logger.error("Data validation failed")
        return "Data validation failed. Check data format and required fields."
    else:
        logger.error(f"Validation error: {error}")
        return f"Data validation error: {error}"
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoint
```python
@self.app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        self.data_store.client.admin.command('ping')
        
        # Get collection stats
        total_records = self.data_store.collection.count_documents({})
        
        return jsonify({
            'status': 'healthy',
            'database_connected': True,
            'total_records': total_records,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'database_connected': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
```

### Database Statistics
```python
def get_database_stats(self):
    """Get comprehensive database statistics"""
    try:
        # Basic stats
        total_records = self.collection.count_documents({})
        
        # Platform distribution
        platform_stats = list(self.collection.aggregate([
            {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        # Post type distribution
        post_type_stats = list(self.collection.aggregate([
            {'$group': {'_id': '$post_type', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        # Sentiment distribution
        sentiment_stats = list(self.collection.aggregate([
            {'$group': {'_id': '$sentiment_score', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]))
        
        return {
            'total_records': total_records,
            'statistics': {
                'platform_stats': platform_stats,
                'post_type_stats': post_type_stats,
                'sentiment_stats': sentiment_stats
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return None
```

## 🛠️ Setup Instructions

### 1. Install MongoDB
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# macOS
brew install mongodb-community

# Windows
# Download from https://www.mongodb.com/try/download/community
```

### 2. Start MongoDB
```bash
# Linux/macOS
sudo systemctl start mongod

# macOS (Homebrew)
brew services start mongodb-community

# Windows
# Start MongoDB service from Services
```

### 3. Verify Connection
```bash
# Test MongoDB connection
mongo --eval "db.runCommand('ping')"

# Check database
mongo social_media_analytics --eval "db.posts.count()"
```

### 4. Environment Configuration
```bash
# Set environment variables
export MONGODB_URI=mongodb://localhost:27017
export MONGODB_DATABASE=social_media_analytics
export MONGODB_COLLECTION=posts
```

## 📋 Best Practices

### Database Design
1. **Use appropriate data types** for optimal storage and query performance
2. **Implement schema validation** to ensure data integrity
3. **Create indexes** on frequently queried fields
4. **Use connection pooling** for better performance
5. **Monitor database size** and implement archiving strategies

### Performance Optimization
1. **Use aggregation pipelines** for complex queries
2. **Implement proper indexing** strategy
3. **Use bulk operations** for data insertion
4. **Monitor query performance** with explain plans
5. **Implement caching** for frequently accessed data

### Data Integrity
1. **Validate data** before insertion
2. **Use transactions** for critical operations
3. **Implement backup strategies** for data protection
4. **Monitor data quality** with regular checks
5. **Document schema changes** for team awareness

## 🔮 Future Enhancements

### Planned Features
- **Data Archiving**: Automatic archiving of old data
- **Sharding**: Horizontal scaling for large datasets
- **Replication**: High availability with replica sets
- **Advanced Analytics**: Machine learning integration
- **Real-time Streaming**: Change streams for live updates
- **Data Versioning**: Track schema and data changes over time