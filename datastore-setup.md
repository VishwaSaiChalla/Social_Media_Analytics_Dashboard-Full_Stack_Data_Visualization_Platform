# Datastore Setup

## Choice of Datastore

For this project, I have chosen **MongoDB** as the datastore solution. The reasons for this choice are as follows:

1. **NoSQL Flexibility**: MongoDB is a NoSQL database that allows for flexible schema design, which is beneficial for handling varying data structures. This is particularly useful for our mock data, which may evolve over time.

2. **Scalability**: MongoDB is designed to scale horizontally, making it suitable for applications that may require handling large volumes of data in the future.

3. **Rich Query Language**: MongoDB provides a powerful query language that allows for complex queries and aggregations, which will be useful for data analysis and visualization.

4. **Community and Ecosystem**: MongoDB has a large community and a rich ecosystem of tools and libraries, making it easier to find resources and support during development.

## Setup Process

To set up MongoDB for this project, follow these steps:

1. **Install MongoDB**: Ensure that MongoDB is installed on your machine. You can download it from the [official MongoDB website](https://www.mongodb.com/try/download/community).

2. **Start MongoDB Server**: Run the MongoDB server using the command:
   ```
   mongod
   ```

3. **Create a Database**: Use the MongoDB shell or a GUI tool like MongoDB Compass to create a new database for this project. For example, you can create a database named `data_visualization`.

4. **Create a Collection**: Within the database, create a collection to store the mock data. For instance, you can create a collection named `data_entries`.

## Database Setup Script

Below is the script to set up the MongoDB database and collection:

```python
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)

# Create database
db = client['data_visualization']

# Create collection
collection = db['data_entries']

print("Database and collection setup complete.")
```

This script connects to a local MongoDB instance, creates a database named `data_visualization`, and a collection named `data_entries`. Make sure to run this script before ingesting data.