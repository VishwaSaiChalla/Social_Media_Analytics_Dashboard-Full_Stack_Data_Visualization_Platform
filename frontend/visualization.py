import logging
import os
import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API base URL - use environment variable for Docker, fallback to localhost
API_BASE_URL = os.getenv("BACKEND_API_URL", "http://localhost:5000")


class DashboardApp:
    def __init__(self):
        self.api_base_url = API_BASE_URL
        self.session_state = st.session_state

        # Initialize session state
        if "data_ingested" not in self.session_state:
            self.session_state.data_ingested = False
        if "scheduler_started" not in self.session_state:
            self.session_state.scheduler_started = False
        if "last_stats" not in self.session_state:
            self.session_state.last_stats = None
        if "last_update" not in self.session_state:
            self.session_state.last_update = None
        if "initial_setup_done" not in self.session_state:
            self.session_state.initial_setup_done = False

    def call_api(self, endpoint, method="GET", data=None):
        """Make API call to backend"""
        try:
            url = f"{self.api_base_url}{endpoint}"
            logger.info(f"Making API call to: {url}")

            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
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
            response = self.call_api(endpoint, method="GET")

            if response and response.get("success"):
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
        """Perform initial setup by checking database status and ingesting data
        if needed"""
        try:
            st.info("🔄 Checking database and performing initial setup...")

            # First check if database has data
            health_response = self.call_api("/health", method="GET")

            if health_response and health_response.get("database_connected"):
                total_records = health_response.get("total_records", 0)

                if total_records > 0:
                    # Database already has data
                    self.session_state.data_ingested = True
                    self.session_state.initial_setup_done = True
                    st.success(f"✅ Database is ready with {total_records} records")
                    return True
                else:
                    # Database is empty, try to ingest CSV data
                    st.info("📥 Database is empty. Attempting to ingest CSV data...")
                    response = self.call_api("/api/ingest-csv", method="POST")

                    if response and response.get("success"):
                        self.session_state.data_ingested = True
                        self.session_state.initial_setup_done = True

                        # Show appropriate message based on whether ingestion
                        # was performed
                        if response.get("ingestion_performed", False):
                            st.success(
                                f"✅ {response.get('message', 'Initial data ingestion completed!')}"
                            )
                        else:
                            st.info(
                                f"ℹ️ {response.get('message', 'Database already has data.')}"
                            )

                        return True
                    else:
                        error_msg = (
                            response.get("error", "Failed to setup database")
                            if response
                            else "API call failed"
                        )
                        st.error(f"❌ {error_msg}")
                        return False
            else:
                st.error(
                    "❌ Database connection failed. Please check MongoDB " "connection."
                )
                return False

        except Exception as e:
            st.error(f"❌ Error during initial setup: {str(e)}")
            return False

    def start_scheduler(self):
        """Start the scheduler for mock data ingestion"""
        try:
            st.info("🔄 Starting scheduler for mock data ingestion...")

            response = self.call_api("/api/start-scheduler", method="POST")

            if response and response.get("success"):
                self.session_state.scheduler_started = True
                st.success(
                    f"✅ {response.get('message', 'Scheduler started successfully!')}"
                )
                return True
            else:
                error_msg = (
                    response.get("error", "Failed to start scheduler")
                    if response
                    else "API call failed"
                )
                st.error(f"❌ {error_msg}")
                return False

        except Exception as e:
            st.error(f"❌ Error starting scheduler: {str(e)}")
            return False

    def get_database_stats(self):
        """Get database statistics"""
        response = self.call_api_with_error_handling(
            "/api/stats", "Failed to retrieve database statistics"
        )
        if response:
            self.session_state.last_stats = response
            self.session_state.last_update = datetime.now()
        return response

    def get_platform_engagement(self):
        """Get platform engagement data"""
        return self.call_api_with_error_handling(
            "/api/platform-engagement",
            "Failed to retrieve platform engagement data",
            "platform_engagement",
        )

    def get_engagement_by_day(self):
        """Get engagement by day data"""
        return self.call_api_with_error_handling(
            "/api/engagement-by-day",
            "Failed to retrieve engagement by day data",
            "engagement_by_day",
        )

    def get_sentiment_by_platform(self):
        """Get sentiment data by platform"""
        return self.call_api_with_error_handling(
            "/api/sentiment-by-platform",
            "Failed to retrieve sentiment data",
            "sentiment_by_platform",
        )

    def get_sentiment_by_post_type(self):
        """Get sentiment data by post type"""
        return self.call_api_with_error_handling(
            "/api/sentiment-by-post-type",
            "Failed to retrieve sentiment by post type data",
            "sentiment_by_post_type",
        )

    def get_average_likes_by_date_platform(self):
        """Get average likes data by date and platform"""
        return self.call_api_with_error_handling(
            "/api/average-likes-by-date-platform",
            "Failed to retrieve average likes by date and platform data",
            "average_likes_by_date_platform",
        )

    def get_average_comments_by_date_platform(self):
        """Get average comments data by date and platform"""
        return self.call_api_with_error_handling(
            "/api/average-comments-by-date-platform",
            "Failed to retrieve average comments by date and platform data",
            "average_comments_by_date_platform",
        )

    def get_average_shares_by_date_platform(self):
        """Get average shares data by date and platform"""
        return self.call_api_with_error_handling(
            "/api/average-shares-by-date-platform",
            "Failed to retrieve average shares by date and platform data",
            "average_shares_by_date_platform",
        )

    def get_shares_by_post_type(self):
        """Get shares data by post type"""
        return self.call_api_with_error_handling(
            "/api/shares-by-post-type",
            "Failed to retrieve shares by post type data",
            "shares_by_post_type",
        )

    def get_decomposition_tree_data(self, platform_filter=None, post_type_filter=None):
        """Get decomposition tree data with optional filters"""
        try:
            # Build query parameters
            params = {}
            if platform_filter:
                params["platform"] = platform_filter
            if post_type_filter:
                params["post_type"] = post_type_filter

            # Make API call with parameters
            url = f"{self.api_base_url}/api/decomposition-tree"
            if params:
                query_string = "&".join([f"{k}={v}" for k, v in params.items()])
                url += f"?{query_string}"

            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and data.get("success"):
                return data.get("decomposition_tree_data", [])
            else:
                st.error("❌ Failed to retrieve decomposition tree data")
                return None

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            return None

    def display_kpi_metrics(self, stats_data):
        """Display KPI metrics"""
        if not stats_data:
            st.warning("⚠️ No statistics data available")
            return

        total_records = stats_data.get("total_records", 0)

        # Get platform statistics to display individual platform counts
        platform_stats = stats_data.get("statistics", {}).get("platform_stats", [])

        # Create KPI cards
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(label="📊 Total Posts", value=total_records, delta=None)

        # Platform-specific metrics
        platform_counts = {}
        for platform in platform_stats:
            platform_counts[platform.get("_id", "Unknown")] = platform.get("count", 0)

        with col2:
            st.metric(
                label="📘 Facebook Posts",
                value=platform_counts.get("Facebook", 0),
                delta=None,
            )

        with col3:
            st.metric(
                label="🐦 Twitter Posts",
                value=platform_counts.get("Twitter", 0),
                delta=None,
            )

        with col4:
            st.metric(
                label="💼 LinkedIn Posts",
                value=platform_counts.get("LinkedIn", 0),
                delta=None,
            )

        with col5:
            st.metric(
                label="📷 Instagram Posts",
                value=platform_counts.get("Instagram", 0),
                delta=None,
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
                category = row["_id"]
                if chart_type == "platform":
                    chart_data.extend(
                        [
                            {
                                x_col: category,
                                "Engagement Type": "Likes",
                                "Count": row["total_likes"],
                            },
                            {
                                x_col: category,
                                "Engagement Type": "Comments",
                                "Count": row["total_comments"],
                            },
                            {
                                x_col: category,
                                "Engagement Type": "Shares",
                                "Count": row["total_shares"],
                            },
                        ]
                    )
                else:  # day chart
                    chart_data.extend(
                        [
                            {
                                x_col: category,
                                "Engagement Type": "Average Likes",
                                "Count": round(row["avg_likes"], 2),
                            },
                            {
                                x_col: category,
                                "Engagement Type": "Average Comments",
                                "Count": round(row["avg_comments"], 2),
                            },
                            {
                                x_col: category,
                                "Engagement Type": "Average Shares",
                                "Count": round(row["avg_shares"], 2),
                            },
                        ]
                    )

            chart_df = pd.DataFrame(chart_data)

            # Create the bar chart
            fig = px.bar(
                chart_df,
                x=x_col,
                y="Count",
                color="Engagement Type",
                title=title,
                barmode="group",
                color_discrete_map=color_map,
            )

            # Update layout for better appearance
            fig.update_layout(
                xaxis_title=x_col,
                yaxis_title="Count",
                legend_title="Engagement Type",
                height=500,
                showlegend=True,
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating {chart_type} chart: {str(e)}")

    def display_platform_engagement_chart(self, engagement_data):
        """Display platform engagement bar chart"""
        color_map = {"Likes": "#1f77b4", "Comments": "#ff7f0e", "Shares": "#2ca02c"}
        self.create_engagement_chart(
            engagement_data,
            "platform",
            "📊 Total Engagement by Platform",
            "Platform",
            "Count",
            color_map,
        )

    def display_engagement_by_day_chart(self, day_data):
        """Display average engagement by day of the week chart"""
        color_map = {
            "Average Likes": "#1f77b4",
            "Average Comments": "#ff7f0e",
            "Average Shares": "#2ca02c",
        }
        self.create_engagement_chart(
            day_data,
            "day",
            "📅 Average Engagement by Day of the Week",
            "Day",
            "Count",
            color_map,
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
                if item["_id"] == platform:
                    platform_data = item
                    break

            if not platform_data:
                st.warning(f"⚠️ No data available for {platform}")
                return

            # Extract sentiment data
            sentiments = platform_data.get("sentiments", [])
            if not sentiments:
                st.warning(f"⚠️ No sentiment data for {platform}")
                return

            # Create data for the donut chart
            labels = []
            values = []
            colors = []

            for sentiment_info in sentiments:
                sentiment = sentiment_info.get("sentiment", "Unknown")
                count = sentiment_info.get("count", 0)

                if count > 0:  # Only include sentiments with data
                    labels.append(sentiment.title())
                    values.append(count)

                    # Assign colors based on sentiment
                    if sentiment.lower() == "positive":
                        colors.append("#1f77b4")  # Blue
                    elif sentiment.lower() == "negative":
                        colors.append("#FFA500")  # Orange
                    elif sentiment.lower() == "neutral":
                        colors.append("#2ca02c")  # Green
                    else:
                        colors.append("#7f7f7f")  # Gray

            if not values:
                st.warning(f"⚠️ No valid sentiment data for {platform}")
                return

            # Create the donut chart
            fig = px.pie(
                values=values,
                names=labels,
                title=title,
                color_discrete_sequence=colors,
                hole=0.6,  # This creates the donut effect
            )

            # Update layout for better appearance
            fig.update_layout(
                height=300,
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                ),
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating donut chart for {platform}: {str(e)}")

    def create_sentiment_stacked_bar_chart(self, sentiment_data):
        """Create a stacked bar chart for sentiment scores by platform"""
        if not sentiment_data:
            st.warning("⚠️ No sentiment data available")
            return

        try:
            # Prepare data for stacked bar chart
            chart_data = []
            platforms = ["Facebook", "Twitter", "LinkedIn", "Instagram"]
            sentiments = ["positive", "negative", "neutral"]

            # Initialize data structure
            for platform in platforms:
                platform_data = next(
                    (item for item in sentiment_data if item["_id"] == platform), None
                )
                if platform_data:
                    sentiments_dict = {
                        s["sentiment"]: s["count"]
                        for s in platform_data.get("sentiments", [])
                    }
                    for sentiment in sentiments:
                        chart_data.append(
                            {
                                "Platform": platform,
                                "Sentiment": sentiment.title(),
                                "Count": sentiments_dict.get(sentiment, 0),
                            }
                        )
                else:
                    # If no data for platform, add zeros
                    for sentiment in sentiments:
                        chart_data.append(
                            {
                                "Platform": platform,
                                "Sentiment": sentiment.title(),
                                "Count": 0,
                            }
                        )

            # Create DataFrame
            df = pd.DataFrame(chart_data)

            # Create stacked bar chart
            fig = px.bar(
                df,
                x="Count",
                y="Platform",
                color="Sentiment",
                title="📊 Sentiment Distribution by Platform " "(Stacked Bar Chart)",
                barmode="stack",
                color_discrete_map={
                    "Positive": "#1f77b4",  # Blue
                    "Negative": "#FFA500",  # Orange
                    "Neutral": "#2ca02c",  # Green
                },
            )

            # Update layout for better appearance
            fig.update_layout(
                xaxis_title="Number of Posts",
                yaxis_title="Platform",
                legend_title="Sentiment",
                height=500,
                showlegend=True,
                barmode="stack",
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating stacked bar chart: {str(e)}")

    def create_sentiment_stacked_column_chart(self, sentiment_data):
        """Create a stacked column chart for sentiment scores by post type"""
        if not sentiment_data:
            st.warning("⚠️ No sentiment data available")
            return

        try:
            # Prepare data for stacked column chart
            chart_data = []
            post_types = ["carousel", "video", "text", "image", "poll", "story"]
            sentiments = ["positive", "negative", "neutral"]

            # Initialize data structure
            for post_type in post_types:
                post_type_data = next(
                    (item for item in sentiment_data if item["_id"] == post_type), None
                )
                if post_type_data:
                    sentiments_dict = {
                        s["sentiment"]: s["count"]
                        for s in post_type_data.get("sentiments", [])
                    }
                    for sentiment in sentiments:
                        chart_data.append(
                            {
                                "Post Type": post_type.title(),
                                "Sentiment": sentiment.title(),
                                "Count": sentiments_dict.get(sentiment, 0),
                            }
                        )
                else:
                    # If no data for post type, add zeros
                    for sentiment in sentiments:
                        chart_data.append(
                            {
                                "Post Type": post_type.title(),
                                "Sentiment": sentiment.title(),
                                "Count": 0,
                            }
                        )

            # Create DataFrame
            df = pd.DataFrame(chart_data)

            # Create stacked column chart
            fig = px.bar(
                df,
                x="Post Type",
                y="Count",
                color="Sentiment",
                title="📊 Sentiment Distribution by Post Type "
                "(Stacked Column Chart)",
                barmode="stack",
                color_discrete_map={
                    "Positive": "#1f77b4",  # Blue
                    "Negative": "#FFA500",  # Orange
                    "Neutral": "#2ca02c",  # Green
                },
            )

            # Update layout for better appearance
            fig.update_layout(
                xaxis_title="Post Type",
                yaxis_title="Number of Posts",
                legend_title="Sentiment",
                height=500,
                showlegend=True,
                barmode="stack",
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating stacked column chart: {str(e)}")

    def display_sentiment_donut_charts(self, sentiment_data):
        """Display sentiment donut charts for all platforms"""
        if not sentiment_data:
            st.warning("⚠️ No sentiment data available")
            return

        st.subheader("📊 Sentiment Distribution by Platform")

        # Create four columns for the four platforms
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            self.create_donut_chart(sentiment_data, "Facebook", "📘 Facebook Sentiment")

        with col2:
            self.create_donut_chart(sentiment_data, "Twitter", "🐦 Twitter Sentiment")

        with col3:
            self.create_donut_chart(sentiment_data, "LinkedIn", "💼 LinkedIn Sentiment")

        with col4:
            self.create_donut_chart(
                sentiment_data, "Instagram", "📷 Instagram Sentiment"
            )

    def create_line_chart(self, data, metric_name, title, y_label):
        """Generic method to create line charts for engagement metrics"""
        if not data:
            st.warning(f"⚠️ No {metric_name} data available")
            return

        try:
            # Map metric names to backend field names
            metric_mapping = {
                "Average Likes": "avg_likes",
                "Average Comments": "avg_comments",
                "Average Shares": "avg_shares",
            }

            backend_field = metric_mapping.get(metric_name)
            if not backend_field:
                st.error(f"❌ Unknown metric: {metric_name}")
                return

            # Convert to DataFrame for easier manipulation
            chart_data = []
            for item in data:
                chart_data.append(
                    {
                        "Date": item["_id"]["date"],
                        "Platform": item["_id"]["platform"],
                        metric_name: round(item[backend_field], 2),
                        "Total Posts": item["total_posts"],
                    }
                )

            df = pd.DataFrame(chart_data)

            # Convert date strings to datetime for proper sorting
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")

            # Create the line chart
            fig = px.line(
                df,
                x="Date",
                y=metric_name,
                color="Platform",
                title=title,
                markers=True,  # Add markers to the lines
                line_shape="linear",
            )

            fig.update_layout(
                xaxis_title="Date",
                yaxis_title=y_label,
                legend_title="Platform",
                height=500,
                showlegend=True,
                hovermode="x unified",
            )

            # Customize colors for each platform
            fig.update_traces(line=dict(width=3), marker=dict(size=6))

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating {metric_name} line chart: {str(e)}")

    def create_average_likes_line_chart(self, likes_data):
        """Create a line chart for average likes by date and platform"""
        self.create_line_chart(
            likes_data,
            "Average Likes",
            "📈 Average Likes Count by Date and Platform",
            "Average Likes Count",
        )

    def create_average_comments_line_chart(self, comments_data):
        """Create a line chart for average comments by date and platform"""
        self.create_line_chart(
            comments_data,
            "Average Comments",
            "💬 Average Comments Count by Date and Platform",
            "Average Comments Count",
        )

    def create_average_shares_line_chart(self, shares_data):
        """Create a line chart for average shares by date and platform"""
        self.create_line_chart(
            shares_data,
            "Average Shares",
            "📤 Average Shares Count by Date and Platform",
            "Average Shares Count",
        )

    def create_shares_by_post_type_clustered_chart(self, shares_data):
        """Create a clustered bar chart for shares by post type"""
        if not shares_data:
            st.warning("⚠️ No shares by post type data available")
            return

        try:
            # Convert to DataFrame for easier manipulation
            chart_data = []
            for item in shares_data:
                chart_data.append(
                    {
                        "Post Type": item["_id"].title(),
                        "Total Shares": item["total_shares"],
                        # 'Average Shares': round(item['avg_shares'], 2),
                        "Total Posts": item["total_posts"],
                    }
                )

            df = pd.DataFrame(chart_data)

            # Create a long format DataFrame for clustered bar chart
            chart_data_long = []
            for _, row in df.iterrows():
                chart_data_long.extend(
                    [
                        {
                            "Post Type": row["Post Type"],
                            "Metric": "Total Shares",
                            "Value": row["Total Shares"],
                        }  # ,
                        # {
                        #     'Post Type': row['Post Type'],
                        #     'Metric': 'Average Shares',
                        #     'Value': row['Average Shares']
                        # }
                    ]
                )

            chart_df = pd.DataFrame(chart_data_long)

            # Create the clustered bar chart
            fig = px.bar(
                chart_df,
                y="Post Type",
                x="Value",
                color="Metric",
                title="📤 Shares Analysis by Post Type (Clustered Bar Chart)",
                barmode="group",
                color_discrete_map={
                    "Total Shares": "#1f77b4",  # Blue
                    "Average Shares": "#ff7f0e",  # Orange
                },
            )

            fig.update_layout(
                yaxis_title="Post Type",
                xaxis_title="Shares Count",
                legend_title="Metric",
                height=500,
                showlegend=True,
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating shares by post type clustered chart: {str(e)}")

    def create_decomposition_treemap(self, tree_data):
        """Create a decomposition tree (treemap) visualization"""
        if not tree_data:
            st.warning("⚠️ No decomposition tree data available")
            return

        try:
            # Convert to DataFrame for easier manipulation
            chart_data = []
            for item in tree_data:
                chart_data.append(
                    {
                        "Platform": item["_id"]["platform"],
                        "Post Type": item["_id"]["post_type"].title(),
                        "Sentiment Score": item["_id"]["sentiment_score"].title(),
                        "Total Posts": item["total_posts"],
                        "Total Likes": item["total_likes"],
                        "Total Comments": item["total_comments"],
                        "Total Shares": item["total_shares"],
                    }
                )

            df = pd.DataFrame(chart_data)

            # Create hierarchical structure for treemap
            # Group by platform, then post type, then sentiment
            fig = px.treemap(
                df,
                path=["Platform", "Post Type", "Sentiment Score"],
                values="Total Posts",
                title="🌳 Decomposition Tree - Posts by Platform, "
                "Post Type, and Sentiment",
                color="Total Posts",
                color_continuous_scale="Blues",
                hover_data=["Total Likes", "Total Comments", "Total Shares"],
            )

            fig.update_layout(height=600, showlegend=False)

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error creating decomposition treemap: {str(e)}")

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
                st.error(
                    "❌ Failed to initialize database. Please check MongoDB "
                    "connection."
                )
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
                    response = self.call_api("/api/stop-scheduler", method="POST")
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
                st.caption(
                    f"Last updated: {self.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}"
                )

        # Get data for charts
        engagement_data = self.get_platform_engagement()
        day_data = self.get_engagement_by_day()
        sentiment_data = self.get_sentiment_by_platform()
        sentiment_by_post_type_data = self.get_sentiment_by_post_type()
        average_likes_data = self.get_average_likes_by_date_platform()
        average_comments_data = self.get_average_comments_by_date_platform()
        average_shares_data = self.get_average_shares_by_date_platform()
        shares_by_post_type_data = self.get_shares_by_post_type()

        # Display engagement charts side by side
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

        # Display charts side by side
        if sentiment_data or sentiment_by_post_type_data:
            st.subheader("📊 Sentiment Analysis")

            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)

            with col1:
                if sentiment_data:
                    st.subheader("📊 Sentiment by Platform")
                    self.create_sentiment_stacked_bar_chart(sentiment_data)
                else:
                    st.warning("⚠️ No sentiment data available")

            with col2:
                if sentiment_by_post_type_data:
                    st.subheader("📊 Sentiment by Post Type")
                    self.create_sentiment_stacked_column_chart(
                        sentiment_by_post_type_data
                    )
                else:
                    st.warning("⚠️ No sentiment by post type data available")

            # Display donut charts below
            if sentiment_data:
                self.display_sentiment_donut_charts(sentiment_data)

        # Display average likes and comments line charts side by side
        if average_likes_data or average_comments_data or average_shares_data:
            st.subheader("📈 Engagement Trend Analysis")

            # Create three columns for side-by-side display
            col1, col2 = st.columns(2)

            with col1:
                if average_likes_data:
                    st.subheader("📈 Average Likes Trend")
                    self.create_average_likes_line_chart(average_likes_data)
                else:
                    st.warning("⚠️ No average likes data available")

            with col2:
                if average_comments_data:
                    st.subheader("💬 Average Comments Trend")
                    self.create_average_comments_line_chart(average_comments_data)
                else:
                    st.warning("⚠️ No average comments data available")

            # with col3:
            #     if average_shares_data:
            #         st.subheader("📤 Average Shares Trend")
            #         self.create_average_shares_line_chart(average_shares_data)
            #     else:
            #         st.warning("⚠️ No average shares data available")

        # Display shares analysis charts side by side
        if shares_by_post_type_data or average_shares_data:
            st.subheader("📤 Shares Analysis")

            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)

            with col1:
                if shares_by_post_type_data:
                    st.subheader("📤 Shares by Post Type")
                    self.create_shares_by_post_type_clustered_chart(
                        shares_by_post_type_data
                    )
                else:
                    st.warning("⚠️ No shares by post type data available")

            with col2:
                if average_shares_data:
                    st.subheader("📤 Average Shares Trend")
                    self.create_average_shares_line_chart(average_shares_data)
                else:
                    st.warning("⚠️ No average shares data available")

        # Display decomposition treemap with filters
        st.subheader("🌳 Decomposition Tree Analysis")

        # Add filter controls
        with st.expander("🔧 Filter Options", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                platform_filter = st.selectbox(
                    "Select Platform:",
                    ["All Platforms", "Facebook", "Twitter", "LinkedIn", "Instagram"],
                    help="Filter by specific platform or view all platforms",
                )

            with col2:
                post_type_filter = st.selectbox(
                    "Select Post Type:",
                    [
                        "All Post Types",
                        "carousel",
                        "video",
                        "text",
                        "image",
                        "poll",
                        "story",
                    ],
                    help="Filter by specific post type or view all post types",
                )

        # Apply filters
        selected_platform = (
            None if platform_filter == "All Platforms" else platform_filter
        )
        selected_post_type = (
            None if post_type_filter == "All Post Types" else post_type_filter
        )

        # Get filtered decomposition tree data
        filtered_tree_data = self.get_decomposition_tree_data(
            platform_filter=selected_platform, post_type_filter=selected_post_type
        )

        if filtered_tree_data:
            # Show filter summary
            filter_summary = []
            if selected_platform:
                filter_summary.append(f"Platform: {selected_platform}")
            if selected_post_type:
                filter_summary.append(f"Post Type: {selected_post_type}")

            if filter_summary:
                st.info(f"📊 Showing data for: {' | '.join(filter_summary)}")

            self.create_decomposition_treemap(filtered_tree_data)
        else:
            st.warning("⚠️ No data available for the selected filters")

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
