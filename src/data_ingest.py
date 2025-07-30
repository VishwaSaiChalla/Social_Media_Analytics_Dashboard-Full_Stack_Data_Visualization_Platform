from pymongo import MongoClient
import json
import random
import pandas as pd
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# I am trying to create a Mock Data Generator and insert data into MongoDB.
# Columns include:
# platform : Facebook, Twitter, Instagram, LinkedIn.
# post_type : text, image, video, poll, carousel, story. 
# post_time : random date and time in ISO 8601 format with dates starts in 2024.
# likes : random integer between 0 and 1000.
# comments : random integer between 0 and 500.
# shares : random integer between 0 and 300.
# post_day : random day of the week.
# sentiment_score : random values from positive, negative, neutral.

def mock_data_generator(num_records):

    platforms = ["Facebook", "Twitter", "Instagram", "LinkedIn"]
    post_types = ["text", "image", "video", "poll", "carousel", "story"]
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    sentiment_scores = ["positive", "negative", "neutral"]

    data = []
    for _ in range(num_records):
        platform = random.choice(platforms)
        post_type = random.choice(post_types)
        post_time = (datetime.now() + timedelta(days=random.randint(0, 365))).isoformat()
        likes = random.randint(0, 1000)
        comments = random.randint(0, 500)
        shares = random.randint(0, 300)
        post_day = random.choice(days_of_week)
        sentiment_score = random.choice(sentiment_scores)

        data.append({
            "platform": platform,
            "post_type": post_type,
            "post_time": post_time,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "post_day": post_day,
            "sentiment_score": sentiment_score
        })

    return pd.DataFrame(data)

# I need to create a insert function where it inserts the mock data into MongoDB. 
# Intervel of inserting data is 2 minute using schedular code

def schedule_data_insertion(db, collection_name, df):
    scheduler = BackgroundScheduler()
    
    def insert_data():
        try:
            collection = db[collection_name]
            records = df.to_dict('records')
            collection.insert_many(records)
            print(f"Inserted {len(records)} records into {collection_name} collection.")
        except Exception as e:
            print(f"Error inserting data: {e}")

    scheduler.add_job(insert_data, 'interval', minutes=5)
    scheduler.start()
    print("Data insertion scheduled every 2 minutes.")


if __name__ == "__main__":
    
    print("Generating mock data...")
    df = mock_data_generator(1000)  # Generate 1000 records
    print(df.head())  # Display the first few records
    print("Mock data generated successfully.")