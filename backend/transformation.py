#!/usr/bin/env python3
"""
Data transformation utilities for social media analytics.
This module provides a method to transform post_time data into separate date and time components.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DataTransformer:
    """
    Class for transforming social media data for better visualization and analysis.
    """
    
    def __init__(self):
        """Initialize the DataTransformer"""
        logger.info("Initializing DataTransformer")
    
    def convert_post_time_to_date_time(self, df: pd.DataFrame, post_time_column: str = 'post_time') -> pd.DataFrame:
        """
        Convert post_time column into separate Posted_date and Posted_time columns.
        
        Args:
            df: DataFrame containing the social media data
            post_time_column: Name of the column containing post time data (default: 'post_time')
            
        Returns:
            pd.DataFrame: DataFrame with additional Posted_date and Posted_time columns
        """
        logger.info(f"Converting {post_time_column} to separate date and time columns")
        
        try:
            # Create a copy to avoid modifying the original DataFrame
            transformed_df = df.copy()
            
            # Check if the post_time column exists
            if post_time_column not in transformed_df.columns:
                logger.error(f"Column '{post_time_column}' not found in DataFrame")
                return transformed_df
            
            # Create a temporary datetime column for processing
            temp_datetime_col = f"temp_{post_time_column}"
            
            # Convert post_time to datetime (handle both CSV format first, then ISO format)
            if transformed_df[post_time_column].dtype == 'object':
                # Try CSV format first (8/17/2023 14:45), then ISO format (2023-08-17T14:45:00)
                try:
                    transformed_df[temp_datetime_col] = pd.to_datetime(
                        transformed_df[post_time_column], 
                        format='%m/%d/%Y %H:%M',
                        errors='coerce'
                    )
                except:
                    transformed_df[temp_datetime_col] = pd.to_datetime(
                        transformed_df[post_time_column], 
                        format='%Y-%m-%dT%H:%M:%S',
                        errors='coerce'
                    )
            
            # Extract date and time components
            transformed_df['Posted_date'] = transformed_df[temp_datetime_col].dt.date
            transformed_df['Posted_time'] = transformed_df[temp_datetime_col].dt.time
            
            # Convert to string format for better compatibility
            transformed_df['Posted_date'] = transformed_df['Posted_date'].astype(str)
            transformed_df['Posted_time'] = transformed_df['Posted_time'].astype(str)
            
            # Remove the temporary column
            transformed_df.drop(columns=[temp_datetime_col], inplace=True)
            
            logger.info(f"Successfully converted {post_time_column} to Posted_date and Posted_time columns")
            logger.debug(f"Sample transformed data: {transformed_df[['Posted_date', 'Posted_time']].head()}")
            
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error converting post_time to date and time: {e}")
            return df


if __name__ == "__main__":
    # Configure logging for the main execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("DataTransformer module loaded successfully") 