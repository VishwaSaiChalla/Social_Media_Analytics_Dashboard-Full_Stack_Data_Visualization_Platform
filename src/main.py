from data_ingest import mock_data_generator, schedule_data_insertion
from data_store import database_connection, create_collection, ingest_data_from_csv

if __name__ == "__main__":
    # Establish a connection to the MongoDB database
    db = database_connection()
    print("Database connection established successfully.")
    
    # Create a collection with the defined schema
    create_collection(db)
    
    # Ingest data from the CSV file into the MongoDB collection
    file_path = '../Social_Media_Engagement.csv'
    ingest_data_from_csv(file_path, db)

    # Generate mock data and schedule its insertion
    print("Generating mock data...")
    mock_data = mock_data_generator(1000)  # Generate 1000 records
    print(mock_data.head())  # Display the first few records
    schedule_data_insertion(db, 'social_media_posts', mock_data)
    print("Mock data generated and scheduled for insertion every 5 minutes.")