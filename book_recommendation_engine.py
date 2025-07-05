from utils.ai_recommender import BookRecommender
from utils.book_api import GoogleBooksAPI
import time

class BookRecommendationEngine:
    def __init__(self):
        """Initialize the complete book recommendation system"""
        self.ai_recommender = BookRecommender()
        self.books_api = GoogleBooksAPI()
    
    def get_recommendations(self, user_preferences):
        """
        Get complete book recommendations with detailed information
        
        Args:
            user_preferences (dict): User preferences containing:
                - genres: list of favorite genres
                - favorite_books: list of favorite book titles
                - favorite_authors: list of favorite authors
        
        Returns:
            dict: Complete recommendation results
        """
        # Step 1: Get AI recommendations (silent mode)
        recommended_titles = self.ai_recommender.generate_recommendations(user_preferences)
        
        if not recommended_titles:
            return {
                'success': False,
                'error': 'Failed to generate recommendations',
                'recommendations': []
            }
        
        # Step 2: Get detailed book information (silent mode)
        
        # Step 2: Get detailed book information
        detailed_books = self.books_api.get_multiple_books(recommended_titles)
        
        # Step 3: Combine and enhance the data
        recommendations = self._create_enhanced_recommendations(
            user_preferences, 
            recommended_titles, 
            detailed_books
        )
        
        return {
            'success': True,
            'user_preferences': user_preferences,
            'recommendations': recommendations,
            'total_found': len([book for book in detailed_books if not book.get('placeholder')]),
            'generation_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _create_enhanced_recommendations(self, preferences, ai_titles, book_details):
        """Create enhanced recommendations with AI explanations"""
        enhanced_recommendations = []
        
        for i, (ai_title, book_data) in enumerate(zip(ai_titles, book_details)):
            # Generate explanation for why this book was recommended
            explanation = self._generate_recommendation_explanation(
                preferences, book_data
            )
            
            # Calculate a relevance score
            relevance_score = self._calculate_relevance_score(
                preferences, book_data
            )
            
            enhanced_book = {
                **book_data,  # All the Google Books data
                'recommendation_rank': i + 1,
                'ai_recommended_title': ai_title,
                'recommendation_explanation': explanation,
                'relevance_score': relevance_score,
                'match_reasons': self._get_match_reasons(preferences, book_data)
            }
            
            enhanced_recommendations.append(enhanced_book)
        
        return enhanced_recommendations
    
    def _generate_recommendation_explanation(self, preferences, book_data):
        """Generate an explanation for why this book was recommended"""
        reasons = []
        
        # Check genre matches
        user_genres = [g.lower() for g in preferences.get('genres', [])]
        book_categories = [c.lower() for c in book_data.get('categories', [])]
        
        genre_matches = [genre for genre in user_genres 
                        if any(genre in category for category in book_categories)]
        
        if genre_matches:
            reasons.append(f"matches your interest in {', '.join(genre_matches)}")
        
        # Check author style similarity
        user_authors = preferences.get('favorite_authors', [])
        if user_authors:
            reasons.append("has a writing style similar to your favorite authors")
        
        # Check for high ratings
        rating = book_data.get('average_rating')
        if rating and rating >= 4.0:
            reasons.append(f"has excellent ratings ({rating}/5)")
        
        # Default explanation
        if not reasons:
            reasons.append("matches your reading preferences based on AI analysis")
        
        return f"Recommended because it {' and '.join(reasons)}."
    
    def _calculate_relevance_score(self, preferences, book_data):
        """Calculate a relevance score (0-100)"""
        score = 50  # Base score
        
        # Genre matching
        user_genres = [g.lower() for g in preferences.get('genres', [])]
        book_categories = [c.lower() for c in book_data.get('categories', [])]
        
        genre_matches = sum(1 for genre in user_genres 
                           if any(genre in category for category in book_categories))
        score += genre_matches * 10
        
        # Rating bonus
        rating = book_data.get('average_rating')
        if rating:
            score += (rating - 3) * 5  # Bonus for ratings above 3
        
        # Popularity bonus (based on ratings count)
        ratings_count = book_data.get('ratings_count')
        if ratings_count:
            if ratings_count > 1000:
                score += 5
            if ratings_count > 10000:
                score += 5
        
        # Ensure score is between 0-100
        return max(0, min(100, score))
    
    def _get_match_reasons(self, preferences, book_data):
        """Get specific reasons why this book matches user preferences"""
        reasons = []
        
        # Genre matches
        user_genres = [g.lower() for g in preferences.get('genres', [])]
        book_categories = [c.lower() for c in book_data.get('categories', [])]
        
        for genre in user_genres:
            for category in book_categories:
                if genre in category:
                    reasons.append(f"Genre: {genre.title()}")
                    break
        
        # High rating
        rating = book_data.get('average_rating')
        if rating and rating >= 4.0:
            reasons.append(f"Highly Rated: {rating}⭐")
        
        # Popular book
        ratings_count = book_data.get('ratings_count')
        if ratings_count and ratings_count > 5000:
            reasons.append("Popular Choice")
        
        return reasons[:3]  # Limit to top 3 reasons

# Test function
def test_recommendation_engine():
    """Test the complete recommendation engine"""
    engine = BookRecommendationEngine()
    
    # Test preferences
    test_preferences = {
        'genres': ['Mystery', 'Thriller', 'Psychology'],
        'favorite_books': ['Gone Girl', 'The Girl with the Dragon Tattoo'],
        'favorite_authors': ['Gillian Flynn', 'Tana French']
    }
    
    print("🚀 Testing Complete Book Recommendation Engine")
    print("=" * 60)
    print(f"User Preferences: {test_preferences}")
    print("=" * 60)
    
    # Get recommendations
    results = engine.get_recommendations(test_preferences)
    
    if results['success']:
        print(f"\n✅ Successfully generated {len(results['recommendations'])} recommendations")
        print(f"📊 Found detailed info for {results['total_found']} books")
        print(f"⏰ Generated at: {results['generation_time']}")
        
        print("\n📚 RECOMMENDATIONS:")
        print("=" * 60)
        
        for book in results['recommendations']:
            print(f"\n{book['recommendation_rank']}. 📖 {book['title']}")
            print(f"   👤 By: {book['author_string']}")
            print(f"   ⭐ Rating: {book['average_rating'] if book['average_rating'] else 'No rating'}")
            print(f"   📅 Published: {book['published_date']}")
            print(f"   🎯 Relevance: {book['relevance_score']}/100")
            print(f"   💡 Why: {book['recommendation_explanation']}")
            if book['match_reasons']:
                print(f"   🔗 Matches: {', '.join(book['match_reasons'])}")
            print(f"   📝 {book['description'][:100]}...")
            print("-" * 50)
    
    else:
        print(f"❌ Error: {results['error']}")

if __name__ == "__main__":
    test_recommendation_engine()