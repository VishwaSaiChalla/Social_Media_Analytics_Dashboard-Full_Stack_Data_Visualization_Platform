from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import pandas as pd
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['social_media_analysis_db']
collection = db['social_media_posts']

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get all data from MongoDB"""
    try:
        data = list(collection.find({}, {'_id': 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get aggregated statistics"""
    try:
        # Platform statistics
        platform_stats = list(collection.aggregate([
            {'$group': {'_id': '$platform', 'count': {'$sum': 1}}}
        ]))
        
        # Post type statistics
        post_type_stats = list(collection.aggregate([
            {'$group': {'_id': '$post_type', 'count': {'$sum': 1}}}
        ]))
        
        # Sentiment statistics
        sentiment_stats = list(collection.aggregate([
            {'$group': {'_id': '$sentiment_score', 'count': {'$sum': 1}}}
        ]))
        
        # Engagement statistics
        engagement_stats = list(collection.aggregate([
            {'$group': {
                '_id': None,
                'avg_likes': {'$avg': '$likes'},
                'avg_comments': {'$avg': '$comments'},
                'avg_shares': {'$avg': '$shares'},
                'total_posts': {'$sum': 1}
            }}
        ]))
        
        return jsonify({
            'platform_stats': platform_stats,
            'post_type_stats': post_type_stats,
            'sentiment_stats': sentiment_stats,
            'engagement_stats': engagement_stats[0] if engagement_stats else {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/platform-engagement-totals', methods=['GET'])
def get_platform_engagement_totals():
    """Get total engagement (likes, comments, shares) per platform"""
    try:
        # Aggregate total engagement metrics per platform
        pipeline = [
            {'$group': {
                '_id': '$platform',
                'total_likes': {'$sum': '$likes'},
                'total_comments': {'$sum': '$comments'},
                'total_shares': {'$sum': '$shares'},
                'total_engagement': {'$sum': {'$add': ['$likes', '$comments', '$shares']}},
                'post_count': {'$sum': 1}
            }},
            {'$sort': {'total_engagement': -1}}  # Sort by total engagement descending
        ]
        
        platform_totals = list(collection.aggregate(pipeline))
        
        # Format the response
        formatted_data = []
        for platform in platform_totals:
            formatted_data.append({
                'platform': platform['_id'],
                'total_likes': platform['total_likes'],
                'total_comments': platform['total_comments'],
                'total_shares': platform['total_shares'],
                'total_engagement': platform['total_engagement'],
                'post_count': platform['post_count']
            })
        
        return jsonify({
            'platform_engagement_totals': formatted_data,
            'summary': {
                'total_platforms': len(formatted_data),
                'grand_total_engagement': sum(p['total_engagement'] for p in formatted_data),
                'grand_total_posts': sum(p['post_count'] for p in formatted_data)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trends', methods=['GET'])
def get_trends():
    """Get time-based trends"""
    try:
        # Convert string dates to datetime for aggregation
        pipeline = [
            {'$addFields': {
                'date': {'$dateFromString': {'dateString': '$post_time'}}
            }},
            {'$group': {
                '_id': {
                    'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$date'}},
                    'platform': '$platform'
                },
                'avg_likes': {'$avg': '$likes'},
                'avg_comments': {'$avg': '$comments'},
                'avg_shares': {'$avg': '$shares'},
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id.date': 1}}
        ]
        
        trends = list(collection.aggregate(pipeline))
        return jsonify(trends)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/platform/<platform>', methods=['GET'])
def get_platform_data(platform):
    """Get data for a specific platform"""
    try:
        data = list(collection.find({'platform': platform}, {'_id': 0}))
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
