#!/usr/bin/env python3
"""
Data transformation utilities for social media analytics.
This module provides a simple method to transform social media data before database ingestion.
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
    
    def perform_basic_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform basic transformations on social media data before database ingestion.
        
        Args:
            df: DataFrame containing the social media data
            
        Returns:
            pd.DataFrame: Transformed DataFrame ready for database ingestion
        """
        logger.info("Starting basic data transformations")
        
        try:
            transformed_df = df.copy()
            
            # 1. Clean data - remove duplicates and handle missing values
            logger.info("Cleaning data...")
            initial_rows = len(transformed_df)
            transformed_df = transformed_df.drop_duplicates()
            logger.info(f"Removed {initial_rows - len(transformed_df)} duplicate rows")
            
            # Fill missing values
            numeric_columns = ['likes', 'comments', 'shares']
            for col in numeric_columns:
                if col in transformed_df.columns:
                    median_val = transformed_df[col].median()
                    transformed_df[col] = transformed_df[col].fillna(median_val)
                    logger.info(f"Filled missing values in {col} with median: {median_val}")
            
            # Fill missing text data
            text_columns = ['platform', 'post_type', 'sentiment_score']
            for col in text_columns:
                if col in transformed_df.columns:
                    transformed_df[col] = transformed_df[col].fillna('Unknown')
            
            # 2. Convert post_time to separate date and time columns
            logger.info("Converting post_time to separate date and time columns...")
            if 'post_time' in transformed_df.columns:
                transformed_df = self.convert_post_time_to_date_time(transformed_df, 'post_time')
            
            # 3. Create basic engagement metrics
            logger.info("Creating basic engagement metrics...")
            if all(col in transformed_df.columns for col in ['likes', 'comments', 'shares']):
                # Total engagement (likes + comments + shares)
                transformed_df['total_engagement'] = transformed_df['likes'] + transformed_df['comments'] + transformed_df['shares']
                
                # Engagement ratio (comments + shares) / likes (avoid division by zero)
                transformed_df['engagement_ratio'] = transformed_df.apply(
                    lambda row: (row['comments'] + row['shares']) / row['likes'] if row['likes'] > 0 else 0, 
                    axis=1
                )
                
                logger.info("Successfully created engagement metrics")
            
            # 4. Add basic time features
            logger.info("Adding basic time features...")
            if 'Posted_date' in transformed_df.columns:
                try:
                    # Convert string date back to datetime for processing
                    temp_datetime = pd.to_datetime(transformed_df['Posted_date'])
                    
                    # Extract basic time components
                    transformed_df['posted_hour'] = temp_datetime.dt.hour
                    transformed_df['posted_day_of_week'] = temp_datetime.dt.day_name()
                    transformed_df['posted_month'] = temp_datetime.dt.month_name()
                    
                    # Weekend vs weekday
                    transformed_df['is_weekend'] = temp_datetime.dt.weekday >= 5
                    
                    logger.info("Successfully added time features")
                except Exception as e:
                    logger.warning(f"Failed to add time features: {e}")
                    # Set default values
                    transformed_df['posted_hour'] = 12
                    transformed_df['posted_day_of_week'] = 'Unknown'
                    transformed_df['posted_month'] = 'Unknown'
                    transformed_df['is_weekend'] = False
            
            # 5. Create basic categories
            logger.info("Creating basic categories...")
            if 'total_engagement' in transformed_df.columns:
                try:
                    # Simple engagement level based on quartiles
                    engagement_quartiles = transformed_df['total_engagement'].quantile([0.25, 0.5, 0.75])
                    
                    # Check if we have valid quartiles
                    if not engagement_quartiles.isna().any():
                        transformed_df['engagement_level'] = pd.cut(
                            transformed_df['total_engagement'],
                            bins=[0, engagement_quartiles[0.25], engagement_quartiles[0.5], 
                                  engagement_quartiles[0.75], transformed_df['total_engagement'].max()],
                            labels=['Low', 'Medium', 'High', 'Very High']
                        )
                    else:
                        # Fallback to simple categories
                        transformed_df['engagement_level'] = pd.cut(
                            transformed_df['total_engagement'],
                            bins=4,
                            labels=['Low', 'Medium', 'High', 'Very High']
                        )
                    
                    logger.info("Successfully created engagement categories")
                except Exception as e:
                    logger.warning(f"Failed to create engagement categories: {e}")
                    # Set default category
                    transformed_df['engagement_level'] = 'Medium'
            
            logger.info(f"Basic transformations completed. Final shape: {transformed_df.shape}")
            return transformed_df
            
        except Exception as e:
            logger.error(f"Error during basic transformations: {e}")
            return df

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
                except Exception as e:
                    logger.warning(f"Failed to parse with CSV format, trying ISO format: {e}")
                    try:
                        transformed_df[temp_datetime_col] = pd.to_datetime(
                            transformed_df[post_time_column], 
                            format='%Y-%m-%dT%H:%M:%S',
                            errors='coerce'
                        )
                    except Exception as e2:
                        logger.warning(f"Failed to parse with ISO format, trying auto-detect: {e2}")
                        # Try auto-detect format
                        transformed_df[temp_datetime_col] = pd.to_datetime(
                            transformed_df[post_time_column], 
                            errors='coerce'
                        )
            
            # Check if conversion was successful
            if temp_datetime_col in transformed_df.columns and not transformed_df[temp_datetime_col].isna().all():
                # Extract date and time components and convert to string immediately
                transformed_df['Posted_date'] = transformed_df[temp_datetime_col].dt.strftime('%Y-%m-%d')
                transformed_df['Posted_time'] = transformed_df[temp_datetime_col].dt.strftime('%H:%M:%S')
                
                # Remove the temporary column
                transformed_df.drop(columns=[temp_datetime_col], inplace=True)
                
                logger.info(f"Successfully converted {post_time_column} to Posted_date and Posted_time columns")
                logger.debug(f"Sample transformed data: {transformed_df[['Posted_date', 'Posted_time']].head()}")
            else:
                logger.warning(f"Failed to convert {post_time_column}, keeping original format")
                if temp_datetime_col in transformed_df.columns:
                    transformed_df.drop(columns=[temp_datetime_col], inplace=True)
            
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