# Data Ingestion Documentation

This document explains how the data ingestion script (`data_ingest.py`) works in the social media analytics project. The script is responsible for generating and inserting realistic mock data into the MongoDB datastore.

## Overview

The data ingestion process involves creating synthetic social media data entries that consist of multiple fields:
- **Platform**: Social media platform (Facebook, Twitter, Instagram, LinkedIn)
- **Post Type**: Type of content (text, image, video, poll, carousel, story)
- **Post Time**: Timestamp when the post was made (ISO 8601 format)
- **Engagement Metrics**: Likes, comments, shares
- **Post Day**: Day of the week when posted
- **Sentiment Score**: Positive, negative, or neutral sentiment
- **Post ID**: Unique identifier for each post

## Data Generation Features

### Realistic Data Patterns
The script generates data with realistic social media patterns:

1. **Platform-Specific Engagement**: Different platforms have different engagement ranges:
   - Facebook: 50-800 likes, 10-200 comments, 5-150 shares
   - Twitter: 20-500 likes, 5-100 comments, 10-300 shares
   - Instagram: 100-1000 likes, 15-250 comments, 2-50 shares
   - LinkedIn: 30-400 likes, 8-120 comments, 15-200 shares

2. **Post Type Multipliers**: Different content types affect engagement:
   - Video: Highest engagement (1.5x likes, 1.3x comments, 1.4x shares)
   - Image: Good engagement (1.3x likes, 1.0x comments, 1.1x shares)
   - Text: Moderate engagement (0.8x likes, 1.2x comments, 0.9x shares)
   - Poll: High comments (1.1x likes, 1.5x comments, 0.8x shares)

3. **Time-Based Patterns**: More posts during business hours (9 AM - 5 PM)

4. **Sentiment Correlation**: Higher engagement correlates with more positive sentiment

### Data Fields Generated
- **post_id**: Unique identifier (integer)
- **platform**: Social media platform (string)
- **post_type**: Content type (string)
- **post_time**: ISO 8601 timestamp (string)
- **likes**: Number of likes (integer)
- **comments**: Number of comments (integer)
- **shares**: Number of shares (integer)
- **post_day**: Day of week (string)
- **sentiment_score**: Sentiment analysis (string)

## Ingestion Process

### 1. Database Connection
- Establishes connection to MongoDB using `SocialMediaDataStore`
- Creates collection with schema validation
- Handles connection errors gracefully

### 2. Mock Data Generation
- Generates specified number of records (default: 1000)
- Applies realistic engagement patterns
- Creates time-based distribution
- Correlates sentiment with engagement levels

### 3. Data Insertion
- Uses `data_store.insert_data()` for bulk insertion
- Validates data against MongoDB schema
- Provides detailed logging for monitoring
- Handles insertion errors with proper error messages

### 4. Real-Time Updates (Bonus Feature)
- Schedules periodic data insertion (every 2 minutes)
- Generates 10-50 new records per batch
- Continues until manually stopped
- Uses APScheduler for background processing

## Usage

### Basic Usage
```bash
python src/data_ingest.py
```

### Features
- **Initial Data**: Generates 1000 mock records
- **Real-Time Updates**: Adds 10-50 records every 2 minutes
- **Comprehensive Logging**: Detailed progress and error logs
- **Graceful Shutdown**: Ctrl+C to stop real-time updates

### Integration with Data Store
The script uses the `SocialMediaDataStore` class for all database operations:
```python
from data_store import SocialMediaDataStore
from data_ingest import mock_data_generator, insert_data_to_mongodb

# Initialize data store
data_store = SocialMediaDataStore()
data_store.connect()
data_store.create_collection()

# Generate and insert data
df = mock_data_generator(100)
insert_data_to_mongodb(data_store, df)
```

## CSV Data Ingestion

The script also supports ingesting data from CSV files:
```python
from data_ingest import ingest_data_from_csv

# Ingest CSV data
success = ingest_data_from_csv('path/to/data.csv', data_store)
```

## Error Handling

- **Connection Errors**: Graceful handling of MongoDB connection issues
- **Schema Validation**: Ensures data matches database schema
- **Insertion Errors**: Proper error messages and rollback
- **File Errors**: Handles missing or malformed CSV files

## Performance Features

- **Bulk Insertion**: Uses `insert_many()` for efficient data insertion
- **Batch Processing**: Real-time updates in manageable batches
- **Memory Efficient**: Processes data in chunks
- **Logging**: Comprehensive logging for monitoring and debugging

## Conclusion

This data ingestion script is a robust component of the social media analytics project, providing:
- ✅ Realistic mock data generation
- ✅ Multiple data ingestion methods (mock data + CSV)
- ✅ Real-time data updates
- ✅ Comprehensive error handling
- ✅ Integration with the data store layer
- ✅ Detailed documentation and logging

The script successfully meets all requirements for generating and inserting mock data with at least three fields (platform, engagement metrics, timestamp) and provides additional bonus features for enhanced functionality.