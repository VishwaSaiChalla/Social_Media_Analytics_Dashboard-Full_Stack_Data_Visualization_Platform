from pymongo import MongoClient
import json
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class SocialMediaDataStore:
    """
    Class-based data store for social media analytics
    """
    
    def __init__(self, connection_string: str = 'mongodb://localhost:27017/', 
                 database_name: str = 'social_media_analysis_db'):
        """
        Initialize the data store
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
        """
        logger.info(f"Initializing SocialMediaDataStore with database: {database_name}")
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.collection = None
        
        # Schema definition
        self.database_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["platform", "post_type", "post_time", "likes", "comments", "shares", "post_day", "sentiment_score"],
                "properties": {
                    "_id": {
                        "bsonType": "objectId",
                        "description": "Unique identifier for the document."
                    },
                    "post_id": {
                        "bsonType": "int",
                        "description": "Unique identifier for the post."
                    },
                    "platform": {
                        "bsonType": "string",
                        "description": "Platform where the post was made (e.g. Facebook, Twitter, etc.).",
                        "enum": ["Facebook", "Twitter", "Instagram", "LinkedIn"]
                    },
                    "post_type": {
                        "bsonType": "string",
                        "description": "Type of post (e.g. text, image, video).",
                        "enum": ["text", "image", "video", "poll", "carousel", "story"]
                    },
                    "post_time": {
                        "bsonType": "string",
                        "description": "Time when the post was made (in ISO 8601 format)."
                    },
                    "likes": {
                        "bsonType": "int",
                        "description": "Number of likes the post received.",
                        "minimum": 0
                    },
                    "comments": {
                        "bsonType": "int",
                        "description": "Number of comments on the post.",
                        "minimum": 0
                    },
                    "shares": {
                        "bsonType": "int",
                        "description": "Number of shares the post received.",
                        "minimum": 0
                    },
                    "post_day": {
                        "bsonType": "string",
                        "description": "Day of the week when the post was made (e.g. Monday,Tuesday, etc.).",
                        "enum": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                    },
                    "sentiment_score": {
                        "bsonType": "string",
                        "description": "Sentiment score of the post whether it is postive, negative or neutral.",
                        "enum": ["positive", "negative", "neutral"]
                    }
                }
            }
        }
        logger.info("SocialMediaDataStore initialized successfully")
    
    def connect(self) -> bool:
        """
        Establish a connection to the MongoDB database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        logger.info(f"Attempting to connect to MongoDB at: {self.connection_string}")
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db['social_media_posts']
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Database connection established successfully to database: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        logger.info("Attempting to disconnect from database")
        if self.client:
            self.client.close()
            logger.info("Database connection closed successfully")
        else:
            logger.warning("No active database connection to close")
    
    def create_collection(self) -> bool:
        """
        Create a collection in the database with the defined schema.
        
        Returns:
            bool: True if collection created successfully
        """
        logger.info("Attempting to create collection with schema validation")
        try:
            # Check if database is connected
            if self.db is None:
                logger.error("Database not connected. Call connect() first.")
                return False
                
            # Check if the collection already exists
            if 'social_media_posts' not in self.db.list_collection_names():
                self.db.create_collection('social_media_posts', validator=self.database_schema)
                logger.info("Collection 'social_media_posts' created with schema validation successfully")
            else:
                logger.info("Collection 'social_media_posts' already exists, skipping creation")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False
    
    def delete_collection(self) -> bool:
        """
        Delete the collection from the database.
        
        Returns:
            bool: True if deletion successful
        """
        logger.warning("Attempting to delete collection 'social_media_posts'")
        try:
            if self.db is None:
                logger.error("Database not connected. Call connect() first.")
                return False
                
            self.db.drop_collection('social_media_posts')
            logger.info("Collection 'social_media_posts' deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
    
    def delete_specific_post(self, post_id: int) -> bool:
        """
        Delete a specific post from the collection.
        
        Args:
            post_id: ID of the post to delete
            
        Returns:
            bool: True if deletion successful
        """
        logger.info(f"Attempting to delete post with ID: {post_id}")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return False
                
            result = self.collection.delete_one({"post_id": post_id})
            if result.deleted_count > 0:
                logger.info(f"Post with ID {post_id} deleted successfully")
            else:
                logger.warning(f"No post found with ID {post_id} to delete")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete post {post_id}: {e}")
            return False
    
    def update_post(self, post_id: int, update_data: Dict) -> bool:
        """
        Update a specific post in the collection.
        
        Args:
            post_id: ID of the post to update
            update_data: Data to update
            
        Returns:
            bool: True if update successful
        """
        logger.info(f"Attempting to update post with ID: {post_id}")
        logger.debug(f"Update data: {update_data}")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return False
                
            result = self.collection.update_one({"post_id": post_id}, {"$set": update_data})
            if result.modified_count > 0:
                logger.info(f"Post with ID {post_id} updated successfully")
            else:
                logger.warning(f"No post found with ID {post_id} to update")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update post {post_id}: {e}")
            return False
    
    def read_specific_post(self, post_id: int) -> Optional[Dict]:
        """
        Read a specific post from the collection.
        
        Args:
            post_id: ID of the post to read
            
        Returns:
            Dict or None: Post data if found, None otherwise
        """
        logger.info(f"Attempting to read post with ID: {post_id}")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return None
                
            post = self.collection.find_one({"post_id": post_id})
            if post:
                logger.info(f"Successfully retrieved post with ID {post_id}")
                logger.debug(f"Post data: {post}")
            else:
                logger.warning(f"No post found with ID {post_id}")
            return post if post else None
        except Exception as e:
            logger.error(f"Failed to read post {post_id}: {e}")
            return None
    
    def read_all_posts(self) -> List[Dict]:
        """
        Read all posts from the collection.
        
        Returns:
            List[Dict]: All posts in the collection
        """
        logger.info("Attempting to read all posts from collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            posts = list(self.collection.find())
            logger.info(f"Successfully retrieved {len(posts)} posts from collection")
            logger.debug(f"First few posts: {posts[:3] if posts else 'No posts found'}")
            return posts
        except Exception as e:
            logger.error(f"Failed to read posts: {e}")
            return []
    
    def insert_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Insert data into the collection.
        
        Args:
            data: List of documents to insert
            
        Returns:
            bool: True if insertion successful
        """
        logger.info(f"Attempting to insert {len(data)} documents into collection")
        logger.debug(f"Sample data to insert: {data[:2] if data else 'No data'}")
        try:
            if self.collection is None:
                logger.error("Database not connected")
                raise ValueError("Database not connected")
            
            result = self.collection.insert_many(data)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents")
            logger.debug(f"Inserted document IDs: {result.inserted_ids[:5]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            return False
    
    def ingest_data_from_csv(self, file_path: str) -> bool:
        """
        Ingests data from a CSV file into the MongoDB collection.
        
        Args:
            file_path: The path to the CSV file containing the data.
            
        Returns:
            bool: True if ingestion successful
        """
        logger.info(f"Attempting to ingest data from CSV file: {file_path}")
        try:
            # Check if database is connected
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return False
                
            # Read the CSV file into a DataFrame
            logger.debug(f"Reading CSV file: {file_path}")
            df = pd.read_csv(file_path)
            logger.info(f"Successfully read CSV file with {len(df)} rows and {len(df.columns)} columns")
            logger.debug(f"CSV columns: {list(df.columns)}")
            
            # Convert post_time to ISO 8601 string
            logger.debug("Converting post_time to ISO 8601 format")
            df['post_time'] = pd.to_datetime(df['post_time']).dt.strftime('%Y-%m-%dT%H:%M:%S')

            # Filter columns to only include those defined in the schema
            logger.debug("Filtering DataFrame columns to match schema")
            allowed_columns = list(self.database_schema['$jsonSchema']['properties'].keys())
            # Remove _id from allowed columns as it's auto-generated
            allowed_columns = [col for col in allowed_columns if col != '_id']
            
            # Keep only columns that exist in both DataFrame and schema
            available_columns = [col for col in df.columns if col in allowed_columns]
            if not available_columns:
                logger.error("No valid columns found in CSV that match the database schema")
                return False
                
            df = df[available_columns]
            logger.info(f"Filtered DataFrame to {len(df.columns)} allowed columns: {list(df.columns)}")

            # Convert DataFrame to dictionary format for MongoDB insertion
            data_dict = df.to_dict("records")
            logger.info(f"Converted DataFrame to {len(data_dict)} dictionary records")

            # Insert data into the MongoDB collection using insert_data method
            success = self.insert_data(data_dict)
            if success:
                logger.info(f"Data ingested successfully from {file_path} into MongoDB")
            else:
                logger.error(f"Failed to insert data from {file_path}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to ingest data from CSV {file_path}: {e}")
            return False
    

    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get aggregated statistics from the collection.
        
        Returns:
            Dict: Statistics including platform, post type, sentiment, and engagement stats
        """
        logger.info("Attempting to retrieve aggregated statistics from collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return {}
                
            # Platform statistics
            logger.debug("Calculating platform statistics")
            platform_stats = list(self.collection.aggregate([
                {'$group': {'_id': '$platform', 'count': {'$sum': 1}}}
            ]))
            logger.info(f"Retrieved platform stats: {platform_stats}")
            
            # Post type statistics
            logger.debug("Calculating post type statistics")
            post_type_stats = list(self.collection.aggregate([
                {'$group': {'_id': '$post_type', 'count': {'$sum': 1}}}
            ]))
            logger.info(f"Retrieved post type stats: {post_type_stats}")
            
            # Sentiment statistics
            logger.debug("Calculating sentiment statistics")
            sentiment_stats = list(self.collection.aggregate([
                {'$group': {'_id': '$sentiment_score', 'count': {'$sum': 1}}}
            ]))
            logger.info(f"Retrieved sentiment stats: {sentiment_stats}")
            
            # Engagement statistics
            logger.debug("Calculating engagement statistics")
            engagement_stats = list(self.collection.aggregate([
                {'$group': {
                    '_id': None,
                    'avg_likes': {'$avg': '$likes'},
                    'avg_comments': {'$avg': '$comments'},
                    'avg_shares': {'$avg': '$shares'},
                    'total_posts': {'$sum': 1}
                }}
            ]))
            logger.info(f"Retrieved engagement stats: {engagement_stats}")
            
            stats = {
                'platform_stats': platform_stats,
                'post_type_stats': post_type_stats,
                'sentiment_stats': sentiment_stats,
                'engagement_stats': engagement_stats[0] if engagement_stats else {}
            }
            logger.info("Successfully retrieved all aggregated statistics")
            return stats
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
        
    # Get count of elements in the collection
    def get_count(self) -> int:
        """
        Get the count of elements in the collection.
        
        Returns:
            int: Number of elements in the collection
        """
        logger.info("Attempting to get count of elements in the collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return 0
                
            count = self.collection.count_documents({})
            logger.info(f"Successfully counted {count} elements in the collection")
            return count
        except Exception as e:
            logger.error(f"Failed to get count of elements: {e}")
            return 0
    
    def get_max_post_id(self) -> int:
        """
        Get the maximum post_id from the collection.
        
        Returns:
            int: Maximum post_id value, or 0 if no documents exist
        """
        logger.info("Attempting to get maximum post_id from the collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return 0
                
            # Find the document with the highest post_id
            max_doc = self.collection.find_one(
                {}, 
                sort=[('post_id', -1)]
            )
            
            if max_doc and 'post_id' in max_doc:
                max_post_id = max_doc['post_id']
                logger.info(f"Successfully found maximum post_id: {max_post_id}")
                return max_post_id
            else:
                logger.info("No documents found or no post_id field, returning 0")
                return 0
        except Exception as e:
            logger.error(f"Failed to get maximum post_id: {e}")
            return 0
    
    def get_platform_engagement(self) -> List[Dict]:
        """
        Get total engagement (likes, comments, shares) by platform.
        
        Returns:
            List[Dict]: Platform engagement data with total likes, comments, and shares
        """
        logger.info("Attempting to get platform engagement statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            pipeline = [
                {'$group': {
                    '_id': '$platform',
                    'total_likes': {'$sum': '$likes'},
                    'total_comments': {'$sum': '$comments'},
                    'total_shares': {'$sum': '$shares'},
                    'post_count': {'$sum': 1}
                }},
                {'$sort': {'total_likes': -1}}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully retrieved platform engagement data: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to get platform engagement: {e}")
            return []
    
    def get_engagement_by_day(self) -> List[Dict]:
        """
        Get average engagement (likes, comments, shares) by day of the week.
        
        Returns:
            List[Dict]: Average engagement data by day of the week
        """
        logger.info("Attempting to get engagement by day statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            pipeline = [
                {'$group': {
                    '_id': '$post_day',
                    'avg_likes': {'$avg': '$likes'},
                    'avg_comments': {'$avg': '$comments'},
                    'avg_shares': {'$avg': '$shares'},
                    'post_count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully retrieved engagement by day data: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to get engagement by day: {e}")
            return []

    def get_sentiment_by_platform(self) -> List[Dict]:
        """
        Get sentiment distribution by platform.
        
        Returns:
            List[Dict]: Platform sentiment data with counts for positive, negative, and neutral
        """
        logger.info("Attempting to get sentiment by platform statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            pipeline = [
                {'$group': {
                    '_id': {
                        'platform': '$platform',
                        'sentiment': '$sentiment_score'
                    },
                    'count': {'$sum': 1}
                }},
                {'$group': {
                    '_id': '$_id.platform',
                    'sentiments': {
                        '$push': {
                            'sentiment': '$_id.sentiment',
                            'count': '$count'
                        }
                    },
                    'total_posts': {'$sum': '$count'}
                }},
                {'$sort': {'_id': 1}}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully retrieved sentiment by platform: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to get sentiment by platform: {e}")
            return []

    def get_sentiment_by_post_type(self) -> List[Dict]:
        """
        Get sentiment distribution by post type.
        
        Returns:
            List[Dict]: Post type sentiment data with counts for positive, negative, and neutral
        """
        logger.info("Attempting to get sentiment by post type statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            pipeline = [
                {'$group': {
                    '_id': {
                        'post_type': '$post_type',
                        'sentiment': '$sentiment_score'
                    },
                    'count': {'$sum': 1}
                }},
                {'$group': {
                    '_id': '$_id.post_type',
                    'sentiments': {
                        '$push': {
                            'sentiment': '$_id.sentiment',
                            'count': '$count'
                        }
                    },
                    'total_posts': {'$sum': '$count'}
                }},
                {'$sort': {'_id': 1}}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully retrieved sentiment by post type: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to get sentiment by post type: {e}")
            return []

    

    
    def get_trends(self) -> List[Dict]:
        """
        Get time-based trends from the collection.
        
        Returns:
            List[Dict]: Trend data grouped by date and platform
        """
        logger.info("Attempting to retrieve time-based trends from collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            pipeline = [
                {'$addFields': {
                    'date': {'$dateFromString': {'dateString': '$post_time'}}
                }},
                {'$group': {
                    '_id': {
                        'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}},
                        'platform': '$platform'
                    },
                    'avg_likes': {'$avg': '$likes'},
                    'avg_comments': {'$avg': '$comments'},
                    'avg_shares': {'$avg': '$shares'},
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id.date': 1}}
            ]
            
            logger.debug("Executing aggregation pipeline for trends")
            trends = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully retrieved {len(trends)} trend records")
            logger.debug(f"Sample trends: {trends[:3] if trends else 'No trends found'}")
            return trends
        except Exception as e:
            logger.error(f"Failed to get trends: {e}")
            return []
    
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Execute an aggregation pipeline on the collection.
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List[Dict]: Aggregation results
        """
        logger.info(f"Executing aggregation pipeline with {len(pipeline)} stages")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            results = list(self.collection.aggregate(pipeline))
            logger.info(f"Successfully executed aggregation pipeline, returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Failed to execute aggregation pipeline: {e}")
            return []
    
    def find_by_platform(self, platform: str) -> List[Dict]:
        """
        Find all posts for a specific platform.
        
        Args:
            platform: Platform name to filter by
            
        Returns:
            List[Dict]: Posts for the specified platform
        """
        logger.info(f"Attempting to find posts for platform: {platform}")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []
                
            posts = list(self.collection.find({'platform': platform}, {'_id': 0}))
            logger.info(f"Successfully retrieved {len(posts)} posts for platform {platform}")
            logger.debug(f"Sample posts for {platform}: {posts[:2] if posts else 'No posts found'}")
            return posts
        except Exception as e:
            logger.error(f"Failed to find posts by platform {platform}: {e}")
            return []
    
    def __enter__(self):
        """Context manager entry"""
        logger.info("Entering SocialMediaDataStore context manager")
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        logger.info("Exiting SocialMediaDataStore context manager")
        if exc_type:
            logger.error(f"Exception occurred in context manager: {exc_type}, {exc_val}")
        self.disconnect()


if __name__ == "__main__":
    # Configure logging for the main execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Starting SocialMediaDataStore example usage")
    
    # Example usage with class-based approach
    with SocialMediaDataStore() as data_store:
        # Create collection
        logger.info("Creating collection...")
        data_store.create_collection()
        
        # CSV ingestion using data_store
        file_path = r'../Social_Media_Engagement.csv'
        logger.info(f"Ingesting data from: {file_path}")
        data_store.ingest_data_from_csv(file_path)
        
        # Get statistics
        logger.info("Retrieving statistics...")
        stats = data_store.get_stats()
        print("Statistics:", stats)
        
        # Get trends
        logger.info("Retrieving trends...")
        trends = data_store.get_trends()
        print("Trends:", trends[:5])  # Show first 5 trends
    
    logger.info("SocialMediaDataStore example usage completed")