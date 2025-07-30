from pymongo import MongoClient
import json
import pandas as pd

# I am creating a schema for the MongoDB collection to store data.
# Columns include:
# Age 
# Gender 
# Avg_Daily_Screen_Time_hr 
# Primary_Device 
# Exceeded_Recommended_Limit 
# Educational_to_Recreational_Ratio 
# Health_Impacts 
# Urban_or_Rural 


database_schema = {   
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "Age",
            "Gender",
            "Avg_Daily_Screen_Time_hr",
            "Primary_Device",
            "Exceeded_Recommended_Limit",
            "Educational_to_Recreational_Ratio",
            "Health_Impacts",
            "Urban_or_Rural"
        ],
        "properties": {
            "_id": {
                "bsonType": "objectId",
                "description": "MongoDB's default unique identifier for each document."
            },
            "Age": {
                "bsonType": "int",
                "description": "Age of the user in years, I am using kids age group from 8 to 18.",
                "minimum": 8,
                "maximum": 18
            },
            "Gender": {
                "bsonType": "string",
                "description": "Gender of the user, msut be either Male or Female.",
                "enum": ["Male", "Female"]
            },
            "Avg_Daily_Screen_Time_hr": {
                "bsonType": "double",
                "description": "Average daily screen time in hours, must be a positive number.",
                "minimum": 0.0
            },
            "Primary_Device": {
                "bsonType": "string",
                "description": "Primary device used by the user, must be one of the specified options.",
                "enum": ["Smartphone", "Tablet", "Laptop", "Desktop", "TV"]
            },
            "Exceeded_Recommended_Limit": {
                "bsonType": "bool",
                "description": "Indicates whether the user exceeded the recommended screen time limit."
            },
            "Educational_to_Recreational_Ratio": {
                "bsonType": "double",
                "description": "Ratio of educational to recreational screen time, must be a positive number.",
                "minimum": 0.0,
                "maximum": 1.0
            },
            "Health_Impacts": {
                "bsonType": "array",
                "items": {
                    "bsonType": "string",
                    "description": "List of health impacts experienced by the user, each item must be a string."
                },
                "description": "Array of health impacts, can include multiple items."
            },
            "Urban_or_Rural": {
                "bsonType": "string",
                "description": "Indicates whether the user lives in an urban or rural area.",
                "enum": ["Urban", "Rural"]
            }
        }
    }
}



# MongoDB Connection Setup Configuration Using pymongo
def get_database_connection():
    """
    Establishes a connection to the MongoDB database.
    Returns the database connection object.
    """
    # Currently MongoDB Client is connected to my local database.
    # There is another approach where Connection is made to the Mongo Cluster.
    # For this project, we are using a local MongoDB instance.
    # CONNECTION STRING: 'mongodb://localhost:27017/'
    # CONNECTION STRING FOR MONGO CLUSTER: 'mongodb+srv://<username>:<password>@cluster.mongodb.net/<dbname>?retryWrites=true&w=majority'

    client = MongoClient('mongodb://localhost:27017/')
    db = client['data_visualization_db']

    # Check if the collection exists, if not create it with the schema.

    if 'data_visualization' not in db.list_collection_names():
        db.create_collection('data_visualization', validator=database_schema)
    else:
        print("Collection already exists, skipping creation.")
    return db


def delete_collection():
    """
    Deletes the 'data_visualization' collection if it exists.
    """
    db = get_database_connection()
    if 'data_visualization' in db.list_collection_names():
        db.drop_collection('data_visualization')
        print("Collection 'data_visualization' deleted successfully.")
    else:
        print("Collection 'data_visualization' does not exist.")



# Data ingestion from CSV to MongoDB.
def ingest_data_from_csv(file_path, db):
    """
    Ingests data from a CSV file into the MongoDB collection.
    file_path (str): The path to the CSV file containing the data.
    """
    collection = db['data_visualization']

    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Transform 'Health_Impacts' from comma-separated string to list
    if 'Health_Impacts' in df.columns:
        df['Health_Impacts'] = df['Health_Impacts'].apply(
            lambda x: [item.strip() for item in str(x).split(',')] if pd.notnull(x) else []
        )

    # Ensure the DataFrame matches the schema
    for column in df.columns:
        if column not in database_schema['$jsonSchema']['properties']:
            raise ValueError(f"Column '{column}' is not defined in the database schema.")

    # Convert DataFrame to dictionary format for MongoDB insertion
    data_dict = df.to_dict("records")

    # Insert data into the MongoDB collection
    collection.insert_many(data_dict)
    print(f"Data ingested successfully from {file_path} into MongoDB.")
    return collection



# Main execution
if __name__ == "__main__":
    db = get_database_connection()
    print("Database connection established successfully.")

    # data ingestion
    file_path = r'C:\Users\cvish\Downloads\Take_Home_project\takehomeproject\Kids_Screen_Time.csv'
    #delete_collection()  # Drop the old collection and validator
    ingest_data_from_csv(file_path, db)
    print("Data ingestion completed successfully.")
