from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import sys
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_store import SocialMediaDataStore
from data_ingest import mock_data_generator, insert_data_to_mongodb

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackendApp:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.data_store = None
        self.scheduler = None
        
        # Initialize data store
        self._init_data_store()
        
        # Set up routes
        self._setup_routes()
    
    def _init_data_store(self):
        """Initialize the data store connection"""
        try:
            # Use environment variable for MongoDB URI, fallback to localhost
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            logger.info(f"Connecting to MongoDB at: {mongodb_uri}")
            
            self.data_store = SocialMediaDataStore(connection_string=mongodb_uri)
            if not self.data_store.connect():
                logger.error("Failed to connect to database")
                raise Exception("Database connection failed")
            
            if not self.data_store.create_collection():
                logger.error("Failed to create collection")
                raise Exception("Collection creation failed")
            
            # Check if database is empty and automatically ingest CSV data if needed
            self._auto_ingest_csv_if_empty()
                
            logger.info("Data store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize data store: {e}")
            raise
    
    def _auto_ingest_csv_if_empty(self):
        """Automatically ingest CSV data if database is empty"""
        try:
            # Check if database has data
            current_count = self.data_store.get_count()
            
            if current_count == 0:
                logger.info("Database is empty. Attempting to auto-ingest CSV data...")
                
                # Check if CSV file exists
                csv_path = os.path.join(os.path.dirname(__file__), 'Social_Media_Engagement.csv')
                
                if not os.path.exists(csv_path):
                    logger.warning(f"CSV file not found at: {csv_path}")
                    return
                
                # Ingest data from CSV
                success = self.data_store.ingest_data_from_csv(csv_path)
                
                if success:
                    count = self.data_store.get_count()
                    logger.info(f"Auto-ingestion completed successfully. Total records: {count}")
                else:
                    logger.error("Auto-ingestion failed")
            else:
                logger.info(f"Database already contains {current_count} records. Skipping auto-ingestion.")
                
        except Exception as e:
            logger.error(f"Error during auto-ingestion: {e}")
    
    def _setup_routes(self):
        """Set up API routes"""
        
        @self.app.route('/')
        def home():
            """Home endpoint"""
            return jsonify({
                'message': 'Social Media Analytics Backend',
                'status': 'running',
                'endpoints': {
                    'health': '/health',
                    'ingest_csv': '/api/ingest-csv',
                    'start_scheduler': '/api/start-scheduler',
                    'stop_scheduler': '/api/stop-scheduler',
                    'stats': '/api/stats'
                }
            })
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            try:
                if self.data_store and self.data_store.collection is not None:
                    count = self.data_store.get_count()
                    return jsonify({
                        'status': 'healthy',
                        'database_connected': True,
                        'total_records': count,
                        'scheduler_running': self.scheduler.running if self.scheduler else False
                    })
                else:
                    return jsonify({
                        'status': 'unhealthy',
                        'database_connected': False
                    }), 500
                    
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/ingest-csv', methods=['POST'])
        def ingest_csv():
            """Ingest data from CSV file"""
            try:
                # Check if CSV file exists
                csv_path = os.path.join(os.path.dirname(__file__), 'Social_Media_Engagement.csv')
                
                if not os.path.exists(csv_path):
                    return jsonify({'error': 'CSV file not found'}), 404
                
                # Check if database has data
                current_count = self.data_store.get_count()
                
                if current_count > 0:
                    # Database already has data, skip ingestion
                    return jsonify({
                        'success': True,
                        'message': f'Database already contains {current_count} records. CSV ingestion skipped.',
                        'total_records': current_count,
                        'ingestion_performed': False
                    })
                
                # Database is empty, proceed with ingestion
                success = self.data_store.ingest_data_from_csv(csv_path)
                
                if success:
                    count = self.data_store.get_count()
                    return jsonify({
                        'success': True,
                        'message': f'Data ingested successfully. Total records: {count}',
                        'total_records': count,
                        'ingestion_performed': True
                    })
                else:
                    return jsonify({'error': 'Failed to ingest data from CSV'}), 500
                    
            except Exception as e:
                logger.error(f"Error in ingest_csv: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/start-scheduler', methods=['POST'])
        def start_scheduler():
            """Start the scheduler for mock data ingestion"""
            try:
                if self.scheduler and self.scheduler.running:
                    return jsonify({'message': 'Scheduler is already running'})
                
                # Create scheduler
                self.scheduler = BackgroundScheduler()
                
                def insert_mock_data():
                    """Insert mock data every 2 minutes"""
                    try:
                        # Generate 5-15 new records each time
                        import random
                        num_records = random.randint(5, 15)
                        df = mock_data_generator(num_records, data_store=self.data_store)
                        
                        if insert_data_to_mongodb(self.data_store, df):
                            logger.info(f"Scheduled update: Added {num_records} new records")
                        else:
                            logger.error("Failed to insert scheduled data")
                            
                    except Exception as e:
                        logger.error(f"Error in scheduled insertion: {e}")
                
                # Schedule the job to run every 30 seconds
                self.scheduler.add_job(
                    insert_mock_data,
                    'interval',
                    seconds=30,
                    id='mock_data_insertion'
                )
                
                self.scheduler.start()
                logger.info("Scheduler started - mock data will be inserted every 30 seconds")
                
                return jsonify({
                    'success': True,
                    'message': 'Scheduler started successfully. Mock data will be inserted every 30 seconds.'
                })
                
            except Exception as e:
                logger.error(f"Error starting scheduler: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stop-scheduler', methods=['POST'])
        def stop_scheduler():
            """Stop the scheduler"""
            try:
                if self.scheduler and self.scheduler.running:
                    self.scheduler.shutdown()
                    self.scheduler = None
                    logger.info("Scheduler stopped")
                    return jsonify({'message': 'Scheduler stopped successfully'})
                else:
                    return jsonify({'message': 'Scheduler was not running'})
                    
            except Exception as e:
                logger.error(f"Error stopping scheduler: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get database statistics"""
            try:
                stats = self.data_store.get_stats()
                count = self.data_store.get_count()
                
                return jsonify({
                    'success': True,
                    'total_records': count,
                    'statistics': stats
                })
                
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/platform-engagement', methods=['GET'])
        def get_platform_engagement():
            """Get total engagement by platform"""
            try:
                engagement_data = self.data_store.get_platform_engagement()
                
                return jsonify({
                    'success': True,
                    'platform_engagement': engagement_data
                })
                
            except Exception as e:
                logger.error(f"Error getting platform engagement: {e}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/engagement-by-day', methods=['GET'])
        def get_engagement_by_day():
            """Get average engagement by day of the week"""
            try:
                day_data = self.data_store.get_engagement_by_day()
                
                return jsonify({
                    'success': True,
                    'engagement_by_day': day_data
                })
                
            except Exception as e:
                logger.error(f"Error getting engagement by day: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/sentiment-by-platform', methods=['GET'])
        def get_sentiment_by_platform():
            """Get sentiment distribution by platform"""
            try:
                sentiment_data = self.data_store.get_sentiment_by_platform()
                
                return jsonify({
                    'success': True,
                    'sentiment_by_platform': sentiment_data
                })
                
            except Exception as e:
                logger.error(f"Error getting sentiment by platform: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/sentiment-by-post-type', methods=['GET'])
        def get_sentiment_by_post_type():
            """Get sentiment distribution by post type"""
            try:
                sentiment_data = self.data_store.get_sentiment_by_post_type()
                
                return jsonify({
                    'success': True,
                    'sentiment_by_post_type': sentiment_data
                })
                
            except Exception as e:
                logger.error(f"Error getting sentiment by post type: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/average-likes-by-date-platform', methods=['GET'])
        def get_average_likes_by_date_platform():
            """Get average likes by date and platform"""
            try:
                likes_data = self.data_store.get_average_likes_by_date_platform()
                
                return jsonify({
                    'success': True,
                    'average_likes_by_date_platform': likes_data
                })
                
            except Exception as e:
                logger.error(f"Error getting average likes by date and platform: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/average-comments-by-date-platform', methods=['GET'])
        def get_average_comments_by_date_platform():
            """Get average comments by date and platform"""
            try:
                comments_data = self.data_store.get_average_comments_by_date_platform()
                
                return jsonify({
                    'success': True,
                    'average_comments_by_date_platform': comments_data
                })
                
            except Exception as e:
                logger.error(f"Error getting average comments by date and platform: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/average-shares-by-date-platform', methods=['GET'])
        def get_average_shares_by_date_platform():
            """Get average shares by date and platform"""
            try:
                shares_data = self.data_store.get_average_shares_by_date_platform()
                
                return jsonify({
                    'success': True,
                    'average_shares_by_date_platform': shares_data
                })
                
            except Exception as e:
                logger.error(f"Error getting average shares by date and platform: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/shares-by-post-type', methods=['GET'])
        def get_shares_by_post_type():
            """Get shares by post type"""
            try:
                shares_data = self.data_store.get_shares_by_post_type()
                
                return jsonify({
                    'success': True,
                    'shares_by_post_type': shares_data
                })
                
            except Exception as e:
                logger.error(f"Error getting shares by post type: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/decomposition-tree', methods=['GET'])
        def get_decomposition_tree():
            """Get decomposition tree data with optional filters"""
            try:
                # Get query parameters for filters
                platform_filter = request.args.get('platform')
                post_type_filter = request.args.get('post_type')
                
                tree_data = self.data_store.get_decomposition_tree_data(
                    platform_filter=platform_filter,
                    post_type_filter=post_type_filter
                )
                
                return jsonify({
                    'success': True,
                    'decomposition_tree_data': tree_data
                })
                
            except Exception as e:
                logger.error(f"Error getting decomposition tree data: {e}")
                return jsonify({'error': str(e)}), 500
        

    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the backend application"""
        logger.info(f"Starting backend application on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def shutdown(self):
        """Shutdown the application"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
        
        if self.data_store:
            self.data_store.disconnect()
        
        logger.info("Backend application shutdown complete")

def main():
    """Main function to run the backend application"""
    try:
        app = BackendApp()
        app.run(debug=True)
    except KeyboardInterrupt:
        logger.info("Shutting down backend application...")
        if 'app' in locals():
            app.shutdown()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()
