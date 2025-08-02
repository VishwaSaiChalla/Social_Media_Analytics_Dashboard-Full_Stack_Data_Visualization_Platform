import streamlit as st
import requests
import pandas as pd
import plotly.express as px
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
    
    def call_api_with_error_handling(self, endpoint, error_message, data_key=None):
        """Generic API call method with error handling"""
        try:
            response = self.call_api(endpoint, method='GET')
            
            if response and response.get('success'):
                if data_key:
                    return response.get(data_key, [])
                return response
            else:
                st.error(f"❌ {error_message}")
                return None
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
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
        response = self.call_api_with_error_handling('/api/stats', 'Failed to retrieve database statistics')
        if response:
            self.session_state.last_stats = response
            self.session_state.last_update = datetime.now()
        return response
    
    def get_platform_engagement(self):
        """Get platform engagement data"""
        return self.call_api_with_error_handling('/api/platform-engagement', 'Failed to retrieve platform engagement data', 'platform_engagement')
    
    def get_engagement_by_day(self):
        """Get engagement by day data"""
        return self.call_api_with_error_handling('/api/engagement-by-day', 'Failed to retrieve engagement by day data', 'engagement_by_day')
    
    def get_sentiment_by_platform(self):
        """Get sentiment data by platform"""
        return self.call_api_with_error_handling('/api/sentiment-by-platform', 'Failed to retrieve sentiment data', 'sentiment_by_platform')
    
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
    
    def create_engagement_chart(self, data, chart_type, title, x_col, y_col, color_map):
        """Generic method to create engagement charts"""
        if not data:
            st.warning(f"⚠️ No {chart_type} data available")
            return
        
        try:
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(data)
            
            # Create a long format DataFrame for plotting
            chart_data = []
            for _, row in df.iterrows():
                category = row['_id']
                if chart_type == 'platform':
                    chart_data.extend([
                        {x_col: category, 'Engagement Type': 'Likes', 'Count': row['total_likes']},
                        {x_col: category, 'Engagement Type': 'Comments', 'Count': row['total_comments']},
                        {x_col: category, 'Engagement Type': 'Shares', 'Count': row['total_shares']}
                    ])
                else:  # day chart
                    chart_data.extend([
                        {x_col: category, 'Engagement Type': 'Average Likes', 'Count': round(row['avg_likes'], 2)},
                        {x_col: category, 'Engagement Type': 'Average Comments', 'Count': round(row['avg_comments'], 2)},
                        {x_col: category, 'Engagement Type': 'Average Shares', 'Count': round(row['avg_shares'], 2)}
                    ])
            
            chart_df = pd.DataFrame(chart_data)
            
            # Create the bar chart
            fig = px.bar(
                chart_df,
                x=x_col,
                y='Count',
                color='Engagement Type',
                title=title,
                barmode='group',
                color_discrete_map=color_map
            )
            
            # Update layout for better appearance
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title="Count",
                legend_title="Engagement Type",
                height=500,
                showlegend=True
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error creating {chart_type} chart: {str(e)}")
    
    def display_platform_engagement_chart(self, engagement_data):
        """Display platform engagement bar chart"""
        color_map = {
            'Likes': '#1f77b4',
            'Comments': '#ff7f0e', 
            'Shares': '#2ca02c'
        }
        self.create_engagement_chart(
            engagement_data, 
            'platform', 
            '📊 Total Engagement by Platform',
            'Platform',
            'Count',
            color_map
        )
    
    def display_engagement_by_day_chart(self, day_data):
        """Display average engagement by day of the week chart"""
        color_map = {
            'Average Likes': '#1f77b4',
            'Average Comments': '#ff7f0e', 
            'Average Shares': '#2ca02c'
        }
        self.create_engagement_chart(
            day_data, 
            'day', 
            '📅 Average Engagement by Day of the Week',
            'Day',
            'Count',
            color_map
        )
    
    def create_donut_chart(self, data, platform, title):
        """Create a donut chart for sentiment distribution"""
        if not data:
            st.warning(f"⚠️ No sentiment data available for {platform}")
            return
        
        try:
            # Find the platform data
            platform_data = None
            for item in data:
                if item['_id'] == platform:
                    platform_data = item
                    break
            
            if not platform_data:
                st.warning(f"⚠️ No data available for {platform}")
                return
            
            # Extract sentiment data
            sentiments = platform_data.get('sentiments', [])
            if not sentiments:
                st.warning(f"⚠️ No sentiment data for {platform}")
                return
            
            # Create data for the donut chart
            labels = []
            values = []
            colors = []
            
            for sentiment_info in sentiments:
                sentiment = sentiment_info.get('sentiment', 'Unknown')
                count = sentiment_info.get('count', 0)
                
                if count > 0:  # Only include sentiments with data
                    labels.append(sentiment.title())
                    values.append(count)
                    
                    # Assign colors based on sentiment
                    if sentiment.lower() == 'positive':
                        colors.append('#1f77b4')  # Blue
                    elif sentiment.lower() == 'negative':
                        colors.append('#FFA500')  # Orange
                    elif sentiment.lower() == 'neutral':
                        colors.append('#2ca02c')  # Green
                    else:
                        colors.append('#7f7f7f')  # Gray
            
            if not values:
                st.warning(f"⚠️ No valid sentiment data for {platform}")
                return
            
            # Create the donut chart
            fig = px.pie(
                values=values,
                names=labels,
                title=title,
                color_discrete_sequence=colors,
                hole=0.6  # This creates the donut effect
            )
            
            # Update layout for better appearance
            fig.update_layout(
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error creating donut chart for {platform}: {str(e)}")
    
    def display_sentiment_donut_charts(self, sentiment_data):
        """Display sentiment donut charts for all platforms"""
        if not sentiment_data:
            st.warning("⚠️ No sentiment data available")
            return
        
        st.subheader("📊 Sentiment Distribution by Platform")
        
        # Create four columns for the four platforms
        col1, col2, col3, col4 = st.columns(4)
        
        platforms = ['Facebook', 'Twitter', 'LinkedIn', 'Instagram']
        
        with col1:
            self.create_donut_chart(sentiment_data, 'Facebook', '📘 Facebook Sentiment')
        
        with col2:
            self.create_donut_chart(sentiment_data, 'Twitter', '🐦 Twitter Sentiment')
        
        with col3:
            self.create_donut_chart(sentiment_data, 'LinkedIn', '💼 LinkedIn Sentiment')
        
        with col4:
            self.create_donut_chart(sentiment_data, 'Instagram', '📷 Instagram Sentiment')
    

    
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
        
        # Get engagement data for both charts
        engagement_data = self.get_platform_engagement()
        day_data = self.get_engagement_by_day()
        sentiment_data = self.get_sentiment_by_platform()
        
        # Display charts side by side
        if engagement_data or day_data:
            st.subheader("📊 Engagement Analytics")
            
            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)
            
            with col1:
                if engagement_data:
                    st.subheader("📊 Total Engagement by Platform")
                    self.display_platform_engagement_chart(engagement_data)
                else:
                    st.warning("⚠️ No platform engagement data available")
            
            with col2:
                if day_data:
                    st.subheader("📅 Average Engagement by Day")
                    self.display_engagement_by_day_chart(day_data)
                else:
                    st.warning("⚠️ No engagement by day data available")
        
        # Display sentiment donut charts
        if sentiment_data:
            self.display_sentiment_donut_charts(sentiment_data)
        

        
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
