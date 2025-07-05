from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
# Add these imports at the top of app.py (around line 6-8)
from book_recommendation_engine import BookRecommendationEngine
from utils.book_api import GoogleBooksAPI

# Import your existing recommendation classes/functions
# Assuming you have these from your previous work:
# from your_recommendation_module import YourRecommendationClass
# from your_book_api_module import YourBookAPIClass

app = Flask(__name__)
CORS(app)  # Enable CORS for API calls

# Initialize your recommendation system
# recommendation_system = YourRecommendationClass()
# book_api = YourBookAPIClass()

# Add these lines after 'CORS(app)' and before '@app.route('/')'
# Initialize your recommendation system
recommendation_engine = BookRecommendationEngine()
book_api = GoogleBooksAPI()
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/library')
def library():
    """Serve the library page"""
    return render_template('Library.html')

@app.route('/trending')
def trending():
    """Serve the trending books page"""
    return render_template('trending.html')

@app.route('/top-rated')
def top_rated():
    """Serve the top-rated books page"""
    return render_template('top-rated.html')

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Handle recommendation requests"""
    try:
        # Get data from the frontend
        data = request.json
        
        # Extract user preferences
        favorite_books = data.get('favoriteBooks', '')
        favorite_authors = data.get('favoriteAuthors', '')
        genres = data.get('genres', [])
        additional_preferences = data.get('additionalPreferences', '')
        
        # Validate input
        if not favorite_books and not favorite_authors and not genres:
            return jsonify({'error': 'Please provide at least one preference'}), 400
        
        # Create user preferences object
        user_preferences = {
            'favorite_books': favorite_books.split('\n') if favorite_books else [],
            'favorite_authors': favorite_authors.split('\n') if favorite_authors else [],
            'genres': genres,
            'additional_preferences': additional_preferences
        }
        
        # Get recommendations using the recommendation engine
        result = recommendation_engine.get_recommendations(user_preferences)
        
        # Return the complete result or just the recommendations
        if result.get('success', False):
            return jsonify({
                'success': True,
                'recommendations': result['recommendations'],
                'total_found': result.get('total_found', 0),
                'user_preferences': result.get('user_preferences', {})
            })
        else:
            return jsonify({
                'error': result.get('error', 'Failed to generate recommendations'),
                'recommendations': []
            }), 500
        
    except Exception as e:
        # Log error but don't print to terminal
        return jsonify({
            'error': 'Something went wrong while generating recommendations. Please try again.',
            'recommendations': []
        }), 500
def get_book_recommendations(user_preferences):
    """
    Get book recommendations using your existing AI + Google Books API integration
    """
    try:
        # Use your existing recommendation engine
        recommendations = recommendation_engine.get_recommendations(user_preferences)
        
        # The recommendations should already be enriched with Google Books data
        # from your existing integration
        return recommendations
        
    except Exception as e:
        print(f"Error getting recommendations: {str(e)}")
        # Return empty list if something goes wrong
        return []

@app.route('/api/trending', methods=['GET'])
def get_trending_books():
    """Get trending books with detailed information using AI + Google Books API"""
    try:
        # Get trending book titles from AI
        trending_titles = recommendation_engine.ai_recommender.get_trending_books()
        
        # Enrich with detailed information from Google Books API
        detailed_books = book_api.get_multiple_books(trending_titles)
        
        # Add trending indicators to the books
        for book in detailed_books:
            book['is_trending'] = True
            book['trending_rank'] = detailed_books.index(book) + 1
        
        return jsonify({
            'success': True,
            'books': detailed_books,
            'total_found': len(detailed_books)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch trending books: {str(e)}',
            'books': []
        }), 500

@app.route('/api/top-rated', methods=['GET'])
def get_top_rated_books():
    """Get top-rated books with detailed information using AI + Google Books API"""
    try:
        # Get top-rated book titles from AI
        top_rated_titles = recommendation_engine.ai_recommender.get_top_rated_books()
        
        # Enrich with detailed information from Google Books API
        detailed_books = book_api.get_multiple_books(top_rated_titles)
        
        # Add top-rated indicators to the books
        for book in detailed_books:
            book['is_top_rated'] = True
            book['top_rated_rank'] = detailed_books.index(book) + 1
        
        return jsonify({
            'success': True,
            'books': detailed_books,
            'total_found': len(detailed_books)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch top-rated books: {str(e)}',
            'books': []
        }), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Book Recommender API is running'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)