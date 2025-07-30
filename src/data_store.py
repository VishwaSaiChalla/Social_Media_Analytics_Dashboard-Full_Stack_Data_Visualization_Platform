from pymongo import MongoClient
import json
import pandas as pd

# I am creating a schema for the MongoDB collection to store data.
# Columns include:
# platform
# post_type
# post_time
# likes
# comments
# shares
# post_day
# sentiment_score

database_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["platform", "post_type", "post_time", "likes", "comments", "shares", "post_day", "sentiment_score"],
        "properties": {
            "_id": {
                "bsonType": "objectId",
                "description": "Unique identifier for the document."
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


# Function to establish a connection to the MongoDB database
def database_connection():
    """
    Establish a connection to the MongoDB database.
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client['social_media_analysis_db']
    return db

# Function to create a collection with the defined schema
def create_collection(db):
    """
    Create a collection in the database with the defined schema.
    """
    # Check if the collection already exists
    if 'social_media_posts' not in db.list_collection_names():
        db.create_collection('social_media_posts', validator=database_schema)
        print("Collection 'social_media_posts' created with schema validation.")
    else:
        print("Collection 'social_media_posts' already exists, skipping creation.")
    return db

def ingest_data_from_csv(file_path, db):
    """
    Ingests data from a CSV file into the MongoDB collection.
    file_path (str): The path to the CSV file containing the data.
    """
    collection = db['social_media_posts']

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Drop 'post_id' column if it exists
    if 'post_id' in df.columns:
        df = df.drop(columns=['post_id'])
    
    # Convert post_time to ISO 8601 string
    df['post_time'] = pd.to_datetime(df['post_time']).dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Ensure the DataFrame matches the schema
    for column in df.columns:
        if column not in database_schema['$jsonSchema']['properties']:
            raise ValueError(f"Column '{column}' is not defined in the database schema.")
        
    # Remove columns not defined in the schema (e.g., post_id)
    allowed_columns = list(database_schema['$jsonSchema']['properties'].keys())
    df = df[[col for col in df.columns if col in allowed_columns]]

    # Convert DataFrame to dictionary format for MongoDB insertion
    data_dict = df.to_dict("records")

    # Insert data into the MongoDB collection
    collection.insert_many(data_dict)
    print(f"Data ingested successfully from {file_path} into MongoDB.")
    return collection

if __name__ == "__main__":
    # Establish a connection to the MongoDB database
    db = database_connection()
    print("Database connection established successfully.")
    # Create a collection with the defined schema
    create_collection(db)
    # Ingest data from the CSV file into the MongoDB collection
    file_path = r'../Social_Media_Engagement.csv'
    ingest_data_from_csv(file_path, db)