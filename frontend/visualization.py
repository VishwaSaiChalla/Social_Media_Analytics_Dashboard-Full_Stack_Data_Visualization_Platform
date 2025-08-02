import streamlit as st
import requests
import pandas as pd
import time
import json
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API base URL - use environment variable for Docker, fallback to localhost
API_BASE_URL = os.getenv('BACKEND_API_URL', 'http://localhost:5000')

class DashboardApp:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.session_state = st.session_state
        
        # Initialize session state
        if 'data_ingested' not in self.session_state:
            self.session_state.data_ingested = False
        if 'scheduler_started' not in self.session_state:
            self.session_state.scheduler_started = False
        if 'last_stats' not in self.session_state:
            self.session_state.last_stats = None
        if 'last_update' not in self.session_state:
            self.session_state.last_update = None
        if 'initial_setup_done' not in self.session_state:
            self.session_state.initial_setup_done = False
    
    def call_api(self, endpoint, method='GET', data=None):
        """Make API call to backend"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            logger.info(f"Making API call to: {url}")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API call: {e}")
            return None
    
    def perform_initial_setup(self):
        """Perform initial setup by calling the smart ingest endpoint"""
        try:
            st.info("🔄 Checking database and performing initial setup...")
            
            response = self.call_api('/api/ingest-csv', method='POST')
            
            if response and response.get('success'):
                self.session_state.data_ingested = True
                self.session_state.initial_setup_done = True
                
                # Show appropriate message based on whether ingestion was performed
                if response.get('ingestion_performed', False):
                    st.success(f"✅ {response.get('message', 'Initial data ingestion completed!')}")
                else:
                    st.info(f"ℹ️ {response.get('message', 'Database already has data.')}")
                
                return True
            else:
                error_msg = response.get('error', 'Failed to setup database') if response else 'API call failed'
                st.error(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error during initial setup: {str(e)}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler for mock data ingestion"""
        try:
            st.info("🔄 Starting scheduler for mock data ingestion...")
            
            response = self.call_api('/api/start-scheduler', method='POST')
            
            if response and response.get('success'):
                self.session_state.scheduler_started = True
                st.success(f"✅ {response.get('message', 'Scheduler started successfully!')}")
                return True
            else:
                error_msg = response.get('error', 'Failed to start scheduler') if response else 'API call failed'
                st.error(f"❌ {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error starting scheduler: {str(e)}")
            return False
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            response = self.call_api('/api/stats', method='GET')
            
            if response and response.get('success'):
                self.session_state.last_stats = response
                self.session_state.last_update = datetime.now()
                return response
            else:
                st.error("❌ Failed to retrieve database statistics")
                return None
                
        except Exception as e:
            st.error(f"❌ Error getting stats: {str(e)}")
            return None
    
    def display_kpi_metrics(self, stats_data):
        """Display KPI metrics"""
        if not stats_data:
            st.warning("⚠️ No statistics data available")
            return
        
        total_records = stats_data.get('total_records', 0)
        
        # Get platform statistics to display individual platform counts
        platform_stats = stats_data.get('statistics', {}).get('platform_stats', [])
        
        # Create KPI cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                label="📊 Total Posts",
                value=total_records,
                delta=None
            )
        
        # Platform-specific metrics
        platform_counts = {}
        for platform in platform_stats:
            platform_counts[platform.get('_id', 'Unknown')] = platform.get('count', 0)
        
        with col2:
            st.metric(
                label="📘 Facebook Posts",
                value=platform_counts.get('Facebook', 0),
                delta=None
            )
        
        with col3:
            st.metric(
                label="🐦 Twitter Posts",
                value=platform_counts.get('Twitter', 0),
                delta=None
            )
        
        with col4:
            st.metric(
                label="💼 LinkedIn Posts",
                value=platform_counts.get('LinkedIn', 0),
                delta=None
            )
        
        with col5:
            st.metric(
                label="📷 Instagram Posts",
                value=platform_counts.get('Instagram', 0),
                delta=None
            )
    

    
    def run(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(
            page_title="Social Media Analytics Dashboard",
            page_icon="📊",
            layout="wide",
            # initial_sidebar_state="expanded"
        )
        
        # Title and description
        st.title("📊 Social Media Analytics Dashboard")
        st.markdown("---")
        
        # Perform initial setup if not done yet
        if not self.session_state.initial_setup_done:
            if not self.perform_initial_setup():
                st.error("❌ Failed to initialize database. Please check MongoDB connection.")
                return
        
        # Sidebar for controls
        with st.sidebar:
            st.header("🎛️ Controls")
            
            # Start/Stop Scheduler buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Start Scheduler"):
                    if self.start_scheduler():
                        st.rerun()
            
            with col2:
                if st.button("⏹️ Stop Scheduler"):
                    response = self.call_api('/api/stop-scheduler', method='POST')
                    if response:
                        self.session_state.scheduler_started = False
                        st.success("✅ Scheduler stopped successfully!")
                        st.rerun()
            
            # Status indicators
            st.markdown("---")
            st.subheader("📈 Status")
            
            if self.session_state.data_ingested:
                st.success("✅ CSV Data Ingested")
            else:
                st.warning("⚠️ CSV Data Not Ingested")
            
            if self.session_state.scheduler_started:
                st.success("✅ Scheduler Running")
            else:
                st.warning("⚠️ Scheduler Stopped")
            
            # Auto-refresh toggle
            auto_refresh = st.checkbox("🔄 Auto-refresh (every 30 seconds)", value=True)
        
        # Main content area
        if not self.session_state.data_ingested:
            st.warning("⚠️ Please wait for initial data ingestion to complete.")
            return
        
        # Get and display statistics
        stats_data = self.get_database_stats()
        
        if stats_data:
            # Display KPI metrics
            st.subheader("📊 Key Performance Indicators")
            self.display_kpi_metrics(stats_data)
            
            # Last update info
            if self.session_state.last_update:
                st.caption(f"Last updated: {self.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        

        
        # Auto-refresh functionality
        if auto_refresh:
            time.sleep(30)
            st.rerun()

def main():
    """Main function to run the dashboard"""
    try:
        app = DashboardApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Dashboard application error: {e}")

if __name__ == "__main__":
    main()
