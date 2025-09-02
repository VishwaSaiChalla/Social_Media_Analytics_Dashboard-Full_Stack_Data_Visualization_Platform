from pymongo import MongoClient
import pandas as pd
import logging
from typing import Dict, List, Optional, Any

from transformation import DataTransformer

logger = logging.getLogger(__name__)


class SocialMediaDataStore:
    """
    Class-based data store for social media analytics
    """

    def __init__(
        self,
        connection_string: str = "mongodb://localhost:27017/",
        database_name: str = "social_media_analysis_db",
    ):
        """
        Initialize the data store

        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
        """
        logger.info(
            f"Initializing SocialMediaDataStore with database: {database_name}"
        )
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.collection = None

        # Schema definition
        self.database_schema = {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "platform",
                    "post_type",
                    "Posted_date",
                    "Posted_time",
                    "likes",
                    "comments",
                    "shares",
                    "sentiment_score",
                ],
                "properties": {
                    "post_id": {
                        "bsonType": "int",
                        "description": "Unique identifier for the post.",
                    },
                    "platform": {
                        "bsonType": "string",
                        "description": (
                            "Platform where the post was made "
                            "(e.g. Facebook, Twitter, etc.)."
                        ),
                        "enum": [
                            "Facebook", "Twitter", "Instagram", "LinkedIn"
                        ],
                    },
                    "post_type": {
                        "bsonType": "string",
                        "description": (
                            "Type of post (e.g. text, image, video)."
                        ),
                        "enum": [
                            "text", "image", "video", "poll", "carousel",
                            "story"
                        ],
                    },
                    "Posted_date": {
                        "bsonType": "string",
                        "description": (
                            "Date when the post was made (YYYY-MM-DD format)."
                        ),
                    },
                    "Posted_time": {
                        "bsonType": "string",
                        "description": (
                            "Time when the post was made (HH:MM:SS format)."
                        ),
                    },
                    "likes": {
                        "bsonType": "int",
                        "description": "Number of likes the post received.",
                        "minimum": 0,
                    },
                    "comments": {
                        "bsonType": "int",
                        "description": "Number of comments on the post.",
                        "minimum": 0,
                    },
                    "shares": {
                        "bsonType": "int",
                        "description": "Number of shares the post received.",
                        "minimum": 0,
                    },
                    "sentiment_score": {
                        "bsonType": "string",
                        "description": (
                            "Sentiment score of the post whether it is "
                            "postive, negative or neutral."
                        ),
                        "enum": ["positive", "negative", "neutral"],
                    },
                    "total_engagement": {
                        "bsonType": "int",
                        "description": (
                            "Total engagement (likes + comments + shares)."
                        ),
                        "minimum": 0,
                    },
                    "engagement_ratio": {
                        "bsonType": "double",
                        "description": (
                            "Engagement ratio ((comments + shares) / likes)."
                        ),
                    },
                    "posted_hour": {
                        "bsonType": "int",
                        "description": "Hour when the post was made (0-23).",
                        "minimum": 0,
                        "maximum": 23,
                    },
                    "posted_day_of_week": {
                        "bsonType": "string",
                        "description": (
                            "Day of the week when the post was made."
                        ),
                        "enum": [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday",
                            "Unknown",
                        ],
                    },
                    "posted_month": {
                        "bsonType": "string",
                        "description": "Month when the post was made.",
                        "enum": [
                            "January",
                            "February",
                            "March",
                            "April",
                            "May",
                            "June",
                            "July",
                            "August",
                            "September",
                            "October",
                            "November",
                            "December",
                            "Unknown",
                        ],
                    },
                    "is_weekend": {
                        "bsonType": "bool",
                        "description": (
                            "Whether the post was made on a weekend "
                            "(Saturday or Sunday)."
                        ),
                    },
                    "engagement_level": {
                        "bsonType": "string",
                        "description": (
                            "Engagement level category based on "
                            "total engagement."
                        ),
                        "enum": [
                            "Low", "Medium", "High", "Very High"
                        ],
                    },
                },
            }
        }
        logger.info("SocialMediaDataStore initialized successfully")

    def connect(self) -> bool:
        """
        Establish a connection to the MongoDB database.

        Returns:
            bool: True if connection successful, False otherwise
        """
        logger.info(
            f"Attempting to connect to MongoDB at: {self.connection_string}"
        )
        try:
            self.client = MongoClient(self.connection_string)
            if self.client is None:
                logger.error("Failed to create MongoDB client")
                return False
            self.db = self.client[self.database_name]
            self.collection = self.db["social_media_posts"]

            # Test connection
            self.client.admin.command("ping")
            logger.info(
                f"Database connection established successfully to database: "
                f"{self.database_name}"
            )
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
            if "social_media_posts" not in self.db.list_collection_names():
                self.db.create_collection(
                    "social_media_posts", validator=self.database_schema
                )
                logger.info(
                    "Collection 'social_media_posts' created with schema "
                    "validation successfully"
                )
            else:
                logger.info(
                    "Collection 'social_media_posts' already exists, "
                    "skipping creation"
                )
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def insert_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Insert data into the collection.

        Args:
            data: List of documents to insert

        Returns:
            bool: True if insertion successful
        """
        logger.info(
            f"Attempting to insert {len(data)} documents into collection"
        )
        logger.debug(
            f"Sample data to insert: {data[:2] if data else 'No data'}"
        )
        try:
            if self.collection is None:
                logger.error("Database not connected")
                raise ValueError("Database not connected")

            result = self.collection.insert_many(data)
            logger.info(
                f"Successfully inserted {len(result.inserted_ids)} documents"
            )
            logger.debug(
                f"Inserted document IDs: {result.inserted_ids[:5]}..."
            )
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
            logger.info(
                f"Successfully read CSV file with {len(df)} rows and "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"CSV columns: {list(df.columns)}")

            # Apply basic transformations before database ingestion
            logger.info("Applying basic transformations to data...")
            transformer = DataTransformer()
            df = transformer.perform_basic_transformations(df)
            logger.info("Basic transformations completed successfully")

            # The transformation should have created Posted_date and
            # Posted_time columns from post_time
            # Remove the original post_time column as it's not needed
            # in the database
            if "post_time" in df.columns:
                df = df.drop(columns=["post_time"])
                logger.info(
                    "Removed post_time column after transformation to "
                    "Posted_date/Posted_time"
                )

            # Filter columns to only include those defined in the schema
            logger.debug("Filtering DataFrame columns to match schema")
            allowed_columns = list(
                self.database_schema["$jsonSchema"]["properties"].keys()
            )
            # Remove _id from allowed columns as it's auto-generated
            allowed_columns = [col for col in allowed_columns if col != "_id"]

            # Keep only columns that exist in both DataFrame and schema
            available_columns = [
                col for col in df.columns if col in allowed_columns
            ]
            if not available_columns:
                logger.error(
                    "No valid columns found in CSV that match the "
                    "database schema"
                )
                return False

            df = df[available_columns]
            logger.info(
                f"Filtered DataFrame to {len(df.columns)} allowed columns: "
                f"{list(df.columns)}"
            )

            # Convert DataFrame to dictionary format for MongoDB insertion
            data_dict = df.to_dict("records")
            logger.info(
                f"Converted DataFrame to {len(data_dict)} dictionary records"
            )

            # Insert data into the MongoDB collection using insert_data method
            success = self.insert_data(data_dict)
            if success:
                logger.info(
                    f"Data ingested successfully from {file_path} into MongoDB"
                )
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
            Dict: Statistics including platform, post type, sentiment, and
            engagement stats
        """
        logger.info(
            "Attempting to retrieve aggregated statistics from collection"
        )
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return {}

            # Platform statistics
            logger.debug("Calculating platform statistics")
            platform_stats = list(
                self.collection.aggregate(
                    [{"$group": {"_id": "$platform", "count": {"$sum": 1}}}]
                )
            )
            logger.info(f"Retrieved platform stats: {platform_stats}")

            # Post type statistics
            logger.debug("Calculating post type statistics")
            post_type_stats = list(
                self.collection.aggregate(
                    [{"$group": {"_id": "$post_type", "count": {"$sum": 1}}}]
                )
            )
            logger.info(f"Retrieved post type stats: {post_type_stats}")

            # Sentiment statistics
            logger.debug("Calculating sentiment statistics")
            sentiment_stats = list(
                self.collection.aggregate(
                    [
                        {
                            "$group": {
                                "_id": "$sentiment_score",
                                "count": {"$sum": 1}
                            }
                        }
                    ]
                )
            )
            logger.info(f"Retrieved sentiment stats: {sentiment_stats}")

            # Engagement statistics
            logger.debug("Calculating engagement statistics")
            engagement_stats = list(
                self.collection.aggregate(
                    [
                        {
                            "$group": {
                                "_id": None,
                                "avg_likes": {"$avg": "$likes"},
                                "avg_comments": {"$avg": "$comments"},
                                "avg_shares": {"$avg": "$shares"},
                                "total_posts": {"$sum": 1},
                            }
                        }
                    ]
                )
            )
            logger.info(f"Retrieved engagement stats: {engagement_stats}")

            stats = {
                "platform_stats": platform_stats,
                "post_type_stats": post_type_stats,
                "sentiment_stats": sentiment_stats,
                "engagement_stats": (
                    engagement_stats[0] if engagement_stats else {}
                ),
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
            logger.info(
                f"Successfully counted {count} elements in the collection"
            )
            return count
        except Exception as e:
            logger.error(f"Failed to get count of elements: {e}")
            return 0

    def get_all_data(self) -> List[Dict]:
        """
        Get all data from the collection.

        Returns:
            List[Dict]: All documents in the collection
        """
        logger.info("Getting all data from collection")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            # Get all documents, excluding the MongoDB _id field
            all_data = list(self.collection.find({}, {"_id": 0}))
            logger.info(f"Retrieved {len(all_data)} documents from collection")
            return all_data
        except Exception as e:
            logger.error(f"Failed to get all data: {e}")
            return []

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
            max_doc = self.collection.find_one({}, sort=[("post_id", -1)])

            if max_doc and "post_id" in max_doc:
                max_post_id = max_doc["post_id"]
                logger.info(
                    f"Successfully found maximum post_id: {max_post_id}"
                )
                return max_post_id
            else:
                logger.info(
                    "No documents found or no post_id field, returning 0"
                )
                return 0
        except Exception as e:
            logger.error(f"Failed to get maximum post_id: {e}")
            return 0

    def get_platform_engagement(self) -> List[Dict]:
        """
        Get total engagement (likes, comments, shares) by platform.

        Returns:
            List[Dict]: Platform engagement data with total likes, comments,
            and shares
        """
        logger.info("Attempting to get platform engagement statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            pipeline = [
                {
                    "$group": {
                        "_id": "$platform",
                        "total_likes": {"$sum": "$likes"},
                        "total_comments": {"$sum": "$comments"},
                        "total_shares": {"$sum": "$shares"},
                        "post_count": {"$sum": 1},
                    }
                },
                {"$sort": {"total_likes": -1}},
            ]

            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved platform engagement data: {results}"
            )
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
                {
                    "$group": {
                        "_id": "$posted_day_of_week",
                        "avg_likes": {"$avg": "$likes"},
                        "avg_comments": {"$avg": "$comments"},
                        "avg_shares": {"$avg": "$shares"},
                        "post_count": {"$sum": 1},
                    }
                },
                {"$sort": {"_id": 1}},
            ]

            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved engagement by day data: {results}"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get engagement by day: {e}")
            return []

    def _get_sentiment_aggregation_pipeline(
        self, group_field: str
    ) -> List[Dict]:
        """
        Helper method to create sentiment aggregation pipeline.

        Args:
            group_field: Field to group by (e.g., 'platform', 'post_type')

        Returns:
            List[Dict]: MongoDB aggregation pipeline
        """
        return [
            {
                "$group": {
                    "_id": {
                        group_field: f"${group_field}",
                        "sentiment": "$sentiment_score",
                    },
                    "count": {"$sum": 1},
                }
            },
            {
                "$group": {
                    "_id": f"$_id.{group_field}",
                    "sentiments": {
                        "$push": {
                            "sentiment": "$_id.sentiment", "count": "$count"
                        }
                    },
                    "total_posts": {"$sum": "$count"},
                }
            },
            {"$sort": {"_id": 1}},
        ]

    def get_sentiment_by_platform(self) -> List[Dict]:
        """
        Get sentiment distribution by platform.

        Returns:
            List[Dict]: Platform sentiment data with counts for positive,
            negative, and neutral
        """
        logger.info("Attempting to get sentiment by platform statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            pipeline = self._get_sentiment_aggregation_pipeline("platform")
            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved sentiment by platform: {results}"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get sentiment by platform: {e}")
            return []

    def get_sentiment_by_post_type(self) -> List[Dict]:
        """
        Get sentiment distribution by post type.

        Returns:
            List[Dict]: Post type sentiment data with counts for positive,
            negative, and neutral
        """
        logger.info("Attempting to get sentiment by post type statistics")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            pipeline = self._get_sentiment_aggregation_pipeline("post_type")
            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved sentiment by post type: {results}"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get sentiment by post type: {e}")
            return []

    def get_average_metric_by_date_platform(self, metric: str) -> List[Dict]:
        """
        Generic method to get average metric count by date and platform.

        Args:
            metric: The metric to aggregate (likes, comments, shares)

        Returns:
            List[Dict]: Average metric data grouped by date and platform
        """
        logger.info(f"Attempting to get average {metric} by date and platform")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            pipeline = [
                {
                    "$group": {
                        "_id": {
                            "date": "$Posted_date",
                            "platform": "$platform"
                        },
                        f"avg_{metric}": {"$avg": f"${metric}"},
                        "total_posts": {"$sum": 1},
                    }
                },
                {"$sort": {"_id.date": 1, "_id.platform": 1}},
            ]

            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved average {metric} by date and "
                f"platform: "
                f"{len(results)} records"
            )
            return results
        except Exception as e:
            logger.error(
                f"Failed to get average {metric} by date and platform: {e}"
            )
            return []

    def get_average_likes_by_date_platform(self) -> List[Dict]:
        """Get average likes count by date and platform."""
        return self.get_average_metric_by_date_platform("likes")

    def get_average_comments_by_date_platform(self) -> List[Dict]:
        """Get average comments count by date and platform."""
        return self.get_average_metric_by_date_platform("comments")

    def get_average_shares_by_date_platform(self) -> List[Dict]:
        """Get average shares count by date and platform."""
        return self.get_average_metric_by_date_platform("shares")

    def get_shares_by_post_type(self) -> List[Dict]:
        """
        Get shares data grouped by post type.

        Returns:
            List[Dict]: Shares data grouped by post type
        """
        logger.info("Attempting to get shares by post type")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            pipeline = [
                {
                    "$group": {
                        "_id": "$post_type",
                        "total_shares": {"$sum": "$shares"},
                        "avg_shares": {"$avg": "$shares"},
                        "total_posts": {"$sum": 1},
                    }
                },
                {"$sort": {"total_shares": -1}},
            ]

            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved shares by post type: "
                f"{len(results)} records"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get shares by post type: {e}")
            return []

    def get_decomposition_tree_data(
        self,
        platform_filter: Optional[str] = None,
        post_type_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Get hierarchical data for decomposition tree (treemap).

        Args:
            platform_filter: Optional platform filter (Facebook, Twitter,
            LinkedIn, Instagram)
            post_type_filter: Optional post type filter (carousel, video,
            text, image, poll, story)

        Returns:
            List[Dict]: Hierarchical data for treemap visualization
        """
        logger.info("Attempting to get decomposition tree data")
        try:
            if self.collection is None:
                logger.error("Database not connected. Call connect() first.")
                return []

            # Build match stage for filters
            match_stage = {}
            if platform_filter:
                match_stage["platform"] = platform_filter
            if post_type_filter:
                match_stage["post_type"] = post_type_filter

            pipeline = []

            # Add match stage if filters are provided
            if match_stage:
                pipeline.append({"$match": match_stage})

            # Group by platform, post_type, and sentiment_score
            pipeline.extend(
                [
                    {
                        "$group": {
                            "_id": {
                                "platform": "$platform",
                                "post_type": "$post_type",
                                "sentiment_score": "$sentiment_score",
                            },
                            "total_posts": {"$sum": 1},
                            "total_likes": {"$sum": "$likes"},
                            "total_comments": {"$sum": "$comments"},
                            "total_shares": {"$sum": "$shares"},
                        }
                    },
                    {
                        "$sort": {
                            "_id.platform": 1,
                            "_id.post_type": 1,
                            "_id.sentiment_score": 1,
                        }
                    },
                ]
            )

            results = list(self.collection.aggregate(pipeline))
            logger.info(
                f"Successfully retrieved decomposition tree data: "
                f"{len(results)} records"
            )
            return results
        except Exception as e:
            logger.error(f"Failed to get decomposition tree data: {e}")
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
            logger.error(
                f"Exception occurred in context manager: {exc_type}, {exc_val}"
            )
        self.disconnect()


if __name__ == "__main__":
    # Configure logging for the main execution
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting SocialMediaDataStore example usage")

    # Example usage with class-based approach
    with SocialMediaDataStore() as data_store:
        # Create collection
        logger.info("Creating collection...")
        data_store.create_collection()

        # CSV ingestion using data_store
        file_path = r"../Social_Media_Engagement.csv"
        logger.info(f"Ingesting data from: {file_path}")
        data_store.ingest_data_from_csv(file_path)

        # Get statistics
        logger.info("Retrieving statistics...")
        stats = data_store.get_stats()
        print("Statistics:", stats)

        # Get statistics
        logger.info("Retrieving statistics...")
        stats = data_store.get_stats()
        print("Statistics:", stats)

    logger.info(
        "SocialMediaDataStore example usage completed"
    )
