import logging
import os
import random
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler

from backend.data_store import SocialMediaDataStore
from backend.transformation import DataTransformer

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def mock_data_generator(num_records, data_store=None, start_post_id=None):
    """
    Generate realistic social media mock data

    Args:
        num_records: Number of records to generate
        data_store: Optional SocialMediaDataStore instance to get current count
        start_post_id: Optional starting post_id (if not provided, will get
        from database)
    """
    platforms = ["Facebook", "Twitter", "Instagram", "LinkedIn"]
    post_types = ["text", "image", "video", "poll", "carousel", "story"]
    # days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    # "Saturday", "Sunday"]
    sentiment_scores = ["positive", "negative", "neutral"]

    # Platform-specific engagement patterns
    platform_patterns = {
        "Facebook": {
            "likes_range": (50, 800),
            "comments_range": (10, 200),
            "shares_range": (5, 150),
        },
        "Twitter": {
            "likes_range": (20, 500),
            "comments_range": (5, 100),
            "shares_range": (10, 300),
        },
        "Instagram": {
            "likes_range": (100, 1000),
            "comments_range": (15, 250),
            "shares_range": (2, 50),
        },
        "LinkedIn": {
            "likes_range": (30, 400),
            "comments_range": (8, 120),
            "shares_range": (15, 200),
        },
    }

    # Post type engagement multipliers
    post_type_multipliers = {
        "text": {"likes": 0.8, "comments": 1.2, "shares": 0.9},
        "image": {"likes": 1.3, "comments": 1.0, "shares": 1.1},
        "video": {"likes": 1.5, "comments": 1.3, "shares": 1.4},
        "poll": {"likes": 1.1, "comments": 1.5, "shares": 0.8},
        "carousel": {"likes": 1.2, "comments": 1.1, "shares": 1.2},
        "story": {"likes": 0.9, "comments": 0.7, "shares": 0.6},
    }

    # Determine starting post_id
    if start_post_id is not None:
        current_post_id = start_post_id
        logger.info(f"Using provided start_post_id: {current_post_id}")
    elif data_store is not None:
        try:
            # Get maximum post_id from database using the efficient method
            max_post_id = data_store.get_max_post_id()
            current_post_id = max_post_id + 1
            logger.info(
                f"Continuing from post_id: {current_post_id} "
                f"(max found: {max_post_id})"
            )
        except Exception as e:
            logger.warning(
                f"Could not get maximum post_id: {e}. Starting from post_id: 1"
            )
            current_post_id = 1
    else:
        current_post_id = 1
        logger.info("No data_store provided, starting from post_id: 1")

    data = []
    for i in range(num_records):
        platform = random.choice(platforms)
        post_type = random.choice(post_types)

        # Generate realistic post time (more posts during business hours)
        hour = random.choices(
            range(24),
            weights=[
                0.1,
                0.05,
                0.05,
                0.05,
                0.05,
                0.1,
                0.2,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.8,
                0.9,
                1.0,
                0.9,
                0.8,
                0.7,
                0.6,
                0.5,
                0.4,
                0.3,
                0.2,
                0.1,
            ],
        )[0]

        post_time = datetime.now() - timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        post_time = post_time.replace(hour=hour)

        # Generate engagement based on platform and post type
        base_pattern = platform_patterns[platform]
        multipliers = post_type_multipliers[post_type]

        likes = int(random.randint(*base_pattern["likes_range"]) * multipliers["likes"])
        comments = int(
            random.randint(*base_pattern["comments_range"]) * multipliers["comments"]
        )
        shares = int(
            random.randint(*base_pattern["shares_range"]) * multipliers["shares"]
        )

        # Sentiment based on engagement (higher engagement = more positive)
        total_engagement = likes + comments + shares
        if total_engagement > 500:
            sentiment_score = random.choices(sentiment_scores, weights=[0.7, 0.1, 0.2])[
                0
            ]
        elif total_engagement > 200:
            sentiment_score = random.choices(sentiment_scores, weights=[0.5, 0.2, 0.3])[
                0
            ]
        else:
            sentiment_score = random.choices(sentiment_scores, weights=[0.3, 0.3, 0.4])[
                0
            ]

        data.append(
            {
                "post_id": current_post_id + i,
                "platform": platform,
                "post_type": post_type,
                "post_time": post_time.strftime("%m/%d/%Y %H:%M"),
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "sentiment_score": sentiment_score,
            }
        )

    df = pd.DataFrame(data)

    # Use DataTransformer to add Posted_date and Posted_time columns
    transformer = DataTransformer()
    df = transformer.convert_post_time_to_date_time(df, "post_time")
    logger.info("Successfully added Posted_date and Posted_time columns to mock data")

    return df


def insert_data_to_mongodb(data_store: SocialMediaDataStore, df: pd.DataFrame) -> bool:
    """
    Insert data into MongoDB using data_store

    Args:
        data_store: Instance of SocialMediaDataStore
        df: DataFrame containing data to insert

    Returns:
        bool: True if insertion successful
    """
    try:
        # Apply basic transformations before insertion
        logger.info("Applying basic transformations to mock data...")
        transformer = DataTransformer()
        transformed_df = transformer.perform_basic_transformations(df)
        logger.info("Basic transformations completed successfully")

        # Remove post_time column as it's been converted to Posted_date and
        # Posted_time
        if "post_time" in transformed_df.columns:
            transformed_df = transformed_df.drop(columns=["post_time"])
            logger.info(
                "Removed post_time column after transformation to "
                "Posted_date/Posted_time"
            )

        records = transformed_df.to_dict("records")

        # Insert data using data_store
        success = data_store.insert_data(records)
        if success:
            logger.info(
                f"Successfully inserted {len(records)} transformed records "
                f"using data_store."
            )
        else:
            logger.error("Failed to insert data using data_store")

        return success
    except Exception as e:
        logger.error(f"Error inserting data: {e}")
        return False


def schedule_data_insertion(data_store: SocialMediaDataStore, interval_seconds=30):
    """
    Schedule periodic data insertion using data_store

    Args:
        data_store: Instance of SocialMediaDataStore
        interval_seconds: Interval between data insertions in seconds
    """
    scheduler = BackgroundScheduler()

    def insert_batch():
        """Insert a batch of new data using data_store"""
        try:
            # Generate 10-50 new records each time
            num_records = random.randint(10, 50)
            logger.info(f"Generating {num_records} new mock records...")

            # Generate mock data with better error handling
            try:
                df = mock_data_generator(num_records, data_store=data_store)
                logger.info(f"Successfully generated {len(df)} mock records")
            except Exception as gen_error:
                logger.error(f"Failed to generate mock data: {gen_error}")
                return

            # Insert data with better error handling
            try:
                if insert_data_to_mongodb(data_store, df):
                    logger.info(
                        f"Real-time update: Added {num_records} new records "
                        f"using data_store"
                    )
                else:
                    logger.error("Failed to insert real-time data using data_store")
            except Exception as insert_error:
                logger.error(f"Failed to insert data: {insert_error}")

        except Exception as e:
            logger.error(f"Error in scheduled insertion: {e}")
            logger.exception("Full traceback:")

    # Schedule the job
    scheduler.add_job(
        insert_batch, "interval", seconds=interval_seconds, id="data_insertion_job"
    )

    scheduler.start()
    logger.info(
        f"Data insertion scheduled every {interval_seconds} seconds "
        f"using data_store."
    )
    return scheduler


def main():
    """
    Main function to set up data ingestion using data_store
    """
    logger.info("Starting data ingestion process using data_store...")

    # Initialize data_store
    data_store = SocialMediaDataStore()

    # Connect to database
    if not data_store.connect():
        logger.error("Failed to connect to database. Exiting.")
        return

    logger.info("Connected to database successfully using data_store.")

    # Create collection if it doesn't exist
    if not data_store.create_collection():
        logger.error("Failed to create collection. Exiting.")
        return

    # Generate initial data
    logger.info("Generating initial mock data...")
    initial_df = mock_data_generator(100, data_store=data_store)

    # Insert initial data using data_store
    if insert_data_to_mongodb(data_store, initial_df):
        logger.info("Initial data inserted successfully using data_store.")

        # Display sample of the data
        logger.info("Sample of generated data:")
        print(initial_df.head())

        # Start real-time updates
        logger.info("Starting real-time data updates using data_store...")
        scheduler = schedule_data_insertion(data_store, interval_seconds=30)

        try:
            # Keep the script running
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Stopping data ingestion...")
            scheduler.shutdown()
            logger.info("Data ingestion stopped.")

    else:
        logger.error("Failed to insert initial data using data_store.")

    # Disconnect from database
    data_store.disconnect()


if __name__ == "__main__":
    main()
