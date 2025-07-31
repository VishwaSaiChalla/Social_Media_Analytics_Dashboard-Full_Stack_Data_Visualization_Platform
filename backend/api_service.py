from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from typing import Dict, List, Any, Optional
from src.database_manager import DatabaseManager
from datetime import datetime

logger = logging.getLogger(__name__)

class APIService:
    """
    Class-based API service for social media analytics
    """
    
    def __init__(self, app_name: str = __name__):
        """
        Initialize API service
        
        Args:
            app_name: Flask application name
        """
        self.app = Flask(app_name)
        CORS(self.app)
        self.db_manager = DatabaseManager()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/data', methods=['GET'])
        def get_data():
            """Get all data from MongoDB"""
            try:
                with self.db_manager as db:
                    data = db.find_all(projection={'_id': 0})
                    return jsonify(data)
            except Exception as e:
                logger.error(f"Error in get_data: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get aggregated statistics"""
            try:
                with self.db_manager as db:
                    stats = db.get_stats()
                    return jsonify(stats)
            except Exception as e:
                logger.error(f"Error in get_stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/trends', methods=['GET'])
        def get_trends():
            """Get time-based trends"""
            try:
                with self.db_manager as db:
                    trends = db.get_trends()
                    return jsonify(trends)
            except Exception as e:
                logger.error(f"Error in get_trends: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/platform/<platform>', methods=['GET'])
        def get_platform_data(platform):
            """Get data for a specific platform"""
            try:
                with self.db_manager as db:
                    data = db.find_all(
                        filter_dict={'platform': platform},
                        projection={'_id': 0}
                    )
                    return jsonify(data)
            except Exception as e:
                logger.error(f"Error in get_platform_data: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/platform/<platform>/stats', methods=['GET'])
        def get_platform_stats(platform):
            """Get statistics for a specific platform"""
            try:
                with self.db_manager as db:
                    pipeline = [
                        {'$match': {'platform': platform}},
                        {'$group': {
                            '_id': None,
                            'total_posts': {'$sum': 1},
                            'avg_likes': {'$avg': '$likes'},
                            'avg_comments': {'$avg': '$comments'},
                            'avg_shares': {'$avg': '$shares'},
                            'total_engagement': {
                                '$sum': {'$add': ['$likes', '$comments', '$shares']}
                            }
                        }}
                    ]
                    stats = db.aggregate(pipeline)
                    return jsonify(stats[0] if stats else {})
            except Exception as e:
                logger.error(f"Error in get_platform_stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/post-types', methods=['GET'])
        def get_post_type_stats():
            """Get post type statistics"""
            try:
                with self.db_manager as db:
                    pipeline = [
                        {'$group': {
                            '_id': '$post_type',
                            'count': {'$sum': 1},
                            'avg_likes': {'$avg': '$likes'},
                            'avg_comments': {'$avg': '$comments'},
                            'avg_shares': {'$avg': '$shares'}
                        }},
                        {'$sort': {'count': -1}}
                    ]
                    stats = db.aggregate(pipeline)
                    return jsonify(stats)
            except Exception as e:
                logger.error(f"Error in get_post_type_stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/sentiment', methods=['GET'])
        def get_sentiment_analysis():
            """Get sentiment analysis"""
            try:
                with self.db_manager as db:
                    pipeline = [
                        {'$group': {
                            '_id': '$sentiment_score',
                            'count': {'$sum': 1},
                            'avg_engagement': {
                                '$avg': {'$add': ['$likes', '$comments', '$shares']}
                            }
                        }},
                        {'$sort': {'count': -1}}
                    ]
                    stats = db.aggregate(pipeline)
                    return jsonify(stats)
            except Exception as e:
                logger.error(f"Error in get_sentiment_analysis: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            try:
                with self.db_manager as db:
                    # Test database connection
                    db.find_all(limit=1)
                    return jsonify({
                        'status': 'healthy',
                        'database': 'connected',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = True):
        """
        Run the Flask application
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
        logger.info(f"Starting API service on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


class DataIngestionService:
    """
    Class-based data ingestion service
    """
    
    def __init__(self):
        """Initialize data ingestion service"""
        self.db_manager = DatabaseManager()
        self.scheduler = None
    
    def generate_mock_data(self, num_records: int) -> List[Dict[str, Any]]:
        """
        Generate mock social media data
        
        Args:
            num_records: Number of records to generate
            
        Returns:
            List of mock data records
        """
        import random
        from datetime import datetime, timedelta
        
        platforms = ["Facebook", "Twitter", "Instagram", "LinkedIn"]
        post_types = ["text", "image", "video", "poll", "carousel", "story"]
        sentiment_scores = ["positive", "negative", "neutral"]
        
        data = []
        for _ in range(num_records):
            platform = random.choice(platforms)
            post_type = random.choice(post_types)
            post_time = (datetime.now() - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23)
            )).isoformat()
            
            likes = random.randint(0, 1000)
            comments = random.randint(0, 500)
            shares = random.randint(0, 300)
            post_day = datetime.fromisoformat(post_time).strftime("%A")
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
        
        return data
    
    def ingest_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Ingest data into database
        
        Args:
            data: List of data records
            
        Returns:
            bool: True if ingestion successful
        """
        try:
            with self.db_manager as db:
                db.create_collection()
                success = db.insert_data(data)
                if success:
                    logger.info(f"Successfully ingested {len(data)} records")
                return success
        except Exception as e:
            logger.error(f"Failed to ingest data: {e}")
            return False
    
    def start_scheduled_ingestion(self, interval_minutes: int = 5):
        """
        Start scheduled data ingestion
        
        Args:
            interval_minutes: Interval between ingestion runs
        """
        from apscheduler.schedulers.background import BackgroundScheduler
        import time
        
        def scheduled_ingestion():
            """Scheduled ingestion job"""
            num_records = random.randint(10, 50)
            data = self.generate_mock_data(num_records)
            self.ingest_data(data)
        
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            scheduled_ingestion,
            'interval',
            minutes=interval_minutes,
            id='data_ingestion_job'
        )
        self.scheduler.start()
        logger.info(f"Scheduled data ingestion every {interval_minutes} minutes")
    
    def stop_scheduled_ingestion(self):
        """Stop scheduled data ingestion"""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Stopped scheduled data ingestion")


# Example usage
if __name__ == "__main__":
    # Start API service
    api_service = APIService()
    api_service.run() 