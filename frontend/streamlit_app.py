import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# API base URL
API_BASE_URL = "http://localhost:5000/api"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_data(endpoint):
    """Fetch data from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching data: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def create_platform_engagement_totals_chart(platform_totals_data):
    """
    Create platform engagement totals bar chart
    """
    if not platform_totals_data or 'platform_engagement_totals' not in platform_totals_data:
        return None
    
    platform_totals = platform_totals_data['platform_engagement_totals']
    
    # Prepare data for plotting
    platforms = [p['platform'] for p in platform_totals]
    total_engagement = [p['total_engagement'] for p in platform_totals]
    total_likes = [p['total_likes'] for p in platform_totals]
    total_comments = [p['total_comments'] for p in platform_totals]
    total_shares = [p['total_shares'] for p in platform_totals]
    
    # Create the figure
    fig = go.Figure()
    
    # Add bars for each engagement type
    fig.add_trace(go.Bar(
        x=platforms,
        y=total_engagement,
        name='Total Engagement',
        marker_color='#1f77b4',
        text=[f'{x:,}' for x in total_engagement],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>' +
                     'Total Engagement: %{y:,}<br>' +
                     '<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=platforms,
        y=total_likes,
        name='Likes',
        marker_color='#ff7f0e',
        text=[f'{x:,}' for x in total_likes],
        textposition='inside',
        hovertemplate='<b>%{x}</b><br>' +
                     'Likes: %{y:,}<br>' +
                     '<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=platforms,
        y=total_comments,
        name='Comments',
        marker_color='#2ca02c',
        text=[f'{x:,}' for x in total_comments],
        textposition='inside',
        hovertemplate='<b>%{x}</b><br>' +
                     'Comments: %{y:,}<br>' +
                     '<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=platforms,
        y=total_shares,
        name='Shares',
        marker_color='#d62728',
        text=[f'{x:,}' for x in total_shares],
        textposition='inside',
        hovertemplate='<b>%{x}</b><br>' +
                     'Shares: %{y:,}<br>' +
                     '<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': '📊 Total Engagement by Platform',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#1f77b4'}
        },
        xaxis_title="Platform",
        yaxis_title="Total Engagement",
        barmode='group',
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    # Update axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='gray'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='lightgray',
        showline=True,
        linewidth=1,
        linecolor='gray'
    )
    
    return fig

def create_platform_comparison_chart(filtered_df):
    """
    Create platform comparison chart (averages)
    """
    # Platform engagement comparison
    platform_engagement = filtered_df.groupby('platform').agg({
        'likes': 'mean',
        'comments': 'mean',
        'shares': 'mean'
    }).reset_index()
    
    fig = go.Figure()
    
    for metric in ['likes', 'comments', 'shares']:
        fig.add_trace(go.Bar(
            name=metric.title(),
            x=platform_engagement['platform'],
            y=platform_engagement[metric],
            text=platform_engagement[metric].round(1),
            textposition='auto'
        ))
    
    fig.update_layout(
        title="Average Engagement by Platform",
        xaxis_title="Platform",
        yaxis_title="Average Engagement",
        barmode='group',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_post_type_distribution_chart(filtered_df):
    """
    Create post type distribution pie chart
    """
    post_type_counts = filtered_df['post_type'].value_counts()
    
    fig = px.pie(
        values=post_type_counts.values,
        names=post_type_counts.index,
        title="Post Type Distribution"
    )
    
    fig.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_date_based_chart(filtered_df):
    """
    Create date-based analysis chart
    """
    if 'post_date' not in filtered_df.columns:
        return None
    
    # Daily trends
    daily_trends = filtered_df.groupby('post_date').agg({
        'likes': 'mean',
        'comments': 'mean',
        'shares': 'mean',
        'platform': 'count'
    }).reset_index()
    daily_trends.columns = ['date', 'avg_likes', 'avg_comments', 'avg_shares', 'post_count']
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Date-based Engagement Trends', 'Daily Post Count'),
        vertical_spacing=0.1
    )
    
    # Engagement trends
    for metric in ['avg_likes', 'avg_comments', 'avg_shares']:
        fig.add_trace(
            go.Scatter(
                x=daily_trends['date'],
                y=daily_trends[metric],
                name=metric.replace('avg_', '').title(),
                mode='lines+markers'
            ),
            row=1, col=1
        )
    
    # Post count
    fig.add_trace(
        go.Bar(
            x=daily_trends['date'],
            y=daily_trends['post_count'],
            name='Post Count'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600, 
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_sentiment_analysis_charts(filtered_df):
    """
    Create sentiment analysis charts
    """
    # Sentiment distribution
    sentiment_counts = filtered_df['sentiment_score'].value_counts()
    
    fig_sentiment = px.bar(
        x=sentiment_counts.index,
        y=sentiment_counts.values,
        title="Sentiment Distribution",
        labels={'x': 'Sentiment', 'y': 'Count'}
    )
    
    fig_sentiment.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Sentiment by platform
    sentiment_platform = filtered_df.groupby(['platform', 'sentiment_score']).size().reset_index(name='count')
    
    fig_sentiment_platform = px.bar(
        sentiment_platform,
        x='platform',
        y='count',
        color='sentiment_score',
        title="Sentiment by Platform",
        barmode='group'
    )
    
    fig_sentiment_platform.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig_sentiment, fig_sentiment_platform

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Social Media Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for filters
    st.sidebar.header("🔍 Filters")
    
    # Fetch data
    data = fetch_data("data")
    stats = fetch_data("stats")
    trends = fetch_data("trends")
    
    if not data or not stats:
        st.error("Unable to fetch data. Please ensure the backend server is running.")
        return
    
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    
    # Platform filter
    platforms = df['platform'].unique()
    selected_platforms = st.sidebar.multiselect(
        "Select Platforms",
        platforms,
        default=platforms
    )
    
    # Date range filter
    if 'post_time' in df.columns:
        # Handle date parsing (extract only date part)
        try:
            # Parse datetime and extract only the date part (no time component)
            df['post_date'] = pd.to_datetime(df['post_time'], errors='coerce').dt.date
            # Remove rows with invalid dates
            df = df.dropna(subset=['post_date'])
            if len(df) == 0:
                st.error("No valid date data found. Please check your data source.")
                return
        except Exception as e:
            st.error(f"Error parsing dates: {e}")
            return
        
        # Check if we have valid dates
        if df['post_date'].isna().all():
            st.error("No valid date data found after parsing.")
            return
            
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['post_date'].min(), df['post_date'].max()),
            min_value=df['post_date'].min(),
            max_value=df['post_date'].max()
        )
    
    # Filter data based on selections
    filtered_df = df[df['platform'].isin(selected_platforms)]
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['post_date'] >= date_range[0]) &
            (filtered_df['post_date'] <= date_range[1])
        ]
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        st.metric(
            "Total Posts",
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):+,}"
        )
    
    with col2:
        avg_likes = filtered_df['likes'].mean()
        st.metric(
            "Avg Likes",
            f"{avg_likes:.1f}",
            delta=f"{avg_likes - df['likes'].mean():+.1f}"
        )
    
    with col3:
        avg_comments = filtered_df['comments'].mean()
        st.metric(
            "Avg Comments",
            f"{avg_comments:.1f}",
            delta=f"{avg_comments - df['comments'].mean():+.1f}"
        )
    
    with col4:
        avg_shares = filtered_df['shares'].mean()
        st.metric(
            "Avg Shares",
            f"{avg_shares:.1f}",
            delta=f"{avg_shares - df['shares'].mean():+.1f}"
        )
    
    # Charts section
    st.markdown("## 📈 Engagement Analysis")
    
    # Platform engagement totals bar chart
    st.markdown("### 📊 Total Engagement by Platform")
    
    # Fetch platform engagement totals data
    platform_totals_data = fetch_data("platform-engagement-totals")
    
    if platform_totals_data and 'platform_engagement_totals' in platform_totals_data:
        platform_totals = platform_totals_data['platform_engagement_totals']
        summary = platform_totals_data.get('summary', {})
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Total Platforms",
                summary.get('total_platforms', 0)
            )
        with col2:
            st.metric(
                "Grand Total Engagement",
                f"{summary.get('grand_total_engagement', 0):,}"
            )
        with col3:
            st.metric(
                "Total Posts",
                f"{summary.get('grand_total_posts', 0):,}"
            )
        
        # Create the bar chart
        if platform_totals:
            fig_totals = create_platform_engagement_totals_chart(platform_totals_data)
            
            if fig_totals:
                st.plotly_chart(fig_totals, use_container_width=True)
            else:
                st.error("Failed to create platform engagement chart")
            
            # Display detailed data table
            st.markdown("#### 📋 Detailed Platform Data")
            totals_df = pd.DataFrame(platform_totals)
            st.dataframe(
                totals_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.warning("No platform engagement data available.")
    else:
        st.error("Unable to fetch platform engagement totals data.")
    
    # Platform comparison (existing code)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Platform Performance (Averages)")
        
        fig_platform = create_platform_comparison_chart(filtered_df)
        st.plotly_chart(fig_platform, use_container_width=True)
    
    with col2:
        st.markdown("### Post Type Distribution")
        
        fig_post_type = create_post_type_distribution_chart(filtered_df)
        st.plotly_chart(fig_post_type, use_container_width=True)
    
    # Date-based analysis
    st.markdown("## 📅 Date-based Analysis")
    
    fig_trends = create_date_based_chart(filtered_df)
    if fig_trends:
        st.plotly_chart(fig_trends, use_container_width=True)
    else:
        st.warning("No date-based data available.")
    
    # Sentiment analysis
    st.markdown("## 😊 Sentiment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sentiment, _ = create_sentiment_analysis_charts(filtered_df)
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        _, fig_sentiment_platform = create_sentiment_analysis_charts(filtered_df)
        st.plotly_chart(fig_sentiment_platform, use_container_width=True)
    
    # Detailed data table
    st.markdown("## 📋 Raw Data")
    
    # Add search functionality
    search_term = st.text_input("Search in data (platform, post_type, sentiment_score)")
    
    if search_term:
        mask = (
            filtered_df['platform'].str.contains(search_term, case=False) |
            filtered_df['post_type'].str.contains(search_term, case=False) |
            filtered_df['sentiment_score'].str.contains(search_term, case=False)
        )
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Download functionality
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"social_media_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
