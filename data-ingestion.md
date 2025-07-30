# Data Ingestion Documentation

This document explains how the data ingestion script (`data_ingest.py`) works in the data visualization project. The script is responsible for generating and inserting mock data into the chosen datastore.

## Overview

The data ingestion process involves creating synthetic data entries that consist of three fields:
- **Category**: A string representing the category of the data point (e.g., "Sales", "Marketing", "Development").
- **Value**: A numerical value associated with the category, which can represent metrics such as revenue, expenses, or other relevant figures.
- **Timestamp**: A date-time value indicating when the data point was recorded, allowing for time-based analysis.

## Data Generation

The script generates a specified number of data entries, each with random values for the category, value, and timestamp. The categories are predefined, and the values are generated using random number generation techniques to simulate realistic data.

## Ingestion Process

1. **Connect to the Datastore**: The script establishes a connection to the chosen datastore using appropriate credentials and configurations.
2. **Generate Mock Data**: It creates mock data entries based on the defined structure.
3. **Insert Data**: The generated data is then inserted into the datastore in bulk to optimize performance and reduce the number of write operations.

## Usage

To run the data ingestion script, execute the following command in the terminal:

```
python src/data_ingest.py
```

Ensure that the datastore is running and accessible before executing the script. The script will output logs indicating the success of the data insertion process.

## Conclusion

This data ingestion script is a crucial component of the data visualization project, enabling the generation of synthetic data for analysis and visualization. By automating the data creation process, it allows for efficient testing and development of the visualization features.