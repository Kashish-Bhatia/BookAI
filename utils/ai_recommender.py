import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class BookRecommender:
    def __init__(self):
        """Initialize the AI book recommender"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    def generate_recommendations(self, user_preferences):
        """
        Generate book recommendations based on user preferences
        
        Args:
            user_preferences (dict): Contains 'genres', 'favorite_books', 'favorite_authors'
        
        Returns:
            list: List of recommended book titles
        """
        # Create a detailed prompt for the AI
        prompt = self._create_recommendation_prompt(user_preferences)
        
        try:
            response = self.model.generate_content(prompt)
            recommendations = self._parse_recommendations(response.text)
            return recommendations
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return self._get_fallback_recommendations(user_preferences)
    
    def _create_recommendation_prompt(self, preferences):
        """Create a detailed prompt for AI recommendations"""
        genres = ', '.join(preferences.get('genres', []))
        favorite_books = ', '.join(preferences.get('favorite_books', []))
        favorite_authors = ', '.join(preferences.get('favorite_authors', []))
        
        prompt = f"""
        You are an expert book recommender. Based on the following user preferences, recommend 5 books that they would love to read.

        User Preferences:
        - Favorite Genres: {genres if genres else 'Not specified'}
        - Favorite Books: {favorite_books if favorite_books else 'Not specified'}
        - Favorite Authors: {favorite_authors if favorite_authors else 'Not specified'}

        Instructions:
        1. Recommend 5 different books
        2. Each book should match the user's taste based on their preferences
        3. Include a mix of popular and lesser-known gems
        4. Don't recommend books they already mentioned as favorites
        5. Format your response as a simple list of book titles, one per line
        6. Only provide the book title, no descriptions or explanations

        Format example:
        The Silent Patient
        Where the Crawdads Sing
        The Seven Husbands of Evelyn Hugo
        Educated
        The Midnight Library

        Your recommendations:
        """
        
        return prompt
    
    def _parse_recommendations(self, ai_response):
        """Parse AI response to extract book titles"""
        # Split response into lines and clean up
        lines = ai_response.strip().split('\n')
        recommendations = []
        
        for line in lines:
            # Clean up the line (remove numbers, bullets, extra spaces)
            clean_line = line.strip()
            if clean_line and not clean_line.startswith('Your recommendations:'):
                # Remove common prefixes like "1.", "•", "-", etc.
                import re
                clean_line = re.sub(r'^\d+\.\s*', '', clean_line)
                clean_line = re.sub(r'^[•\-\*]\s*', '', clean_line)
                clean_line = clean_line.strip()
                
                if clean_line and len(clean_line) > 3:  # Basic validation
                    recommendations.append(clean_line)
        
        # Return first 5 recommendations
        return recommendations[:5]
    
    def _get_fallback_recommendations(self, preferences):
        """Provide fallback recommendations if AI fails"""
        genres = preferences.get('genres', [])
        
        fallback_books = {
            'fiction': ['The Seven Husbands of Evelyn Hugo', 'Where the Crawdads Sing'],
            'mystery': ['The Silent Patient', 'Gone Girl'],
            'romance': ['Beach Read', 'The Hating Game'],
            'fantasy': ['The Name of the Wind', 'The Way of Kings'],
            'science fiction': ['Klara and the Sun', 'Project Hail Mary'],
            'non-fiction': ['Educated', 'Becoming'],
            'thriller': ['The Girl with the Dragon Tattoo', 'The Guest List'],
        }
        
        recommendations = []
        for genre in genres:
            genre_lower = genre.lower()
            if genre_lower in fallback_books:
                recommendations.extend(fallback_books[genre_lower])
        
        # If no genre matches, provide general popular books
        if not recommendations:
            recommendations = [
                'The Midnight Library',
                'Atomic Habits',
                'The Thursday Murder Club',
                'Circe',
                'The Invisible Life of Addie LaRue'
            ]
        
        return recommendations[:5]
    
    def get_trending_books(self, max_results=12):
        """
        Get trending books using Gemini AI based on current popularity and engagement
        
        Returns:
            list: List of trending book titles
        """
        prompt = f"""
        You are a book industry expert with access to current reading trends and popularity data.
        
        Provide {max_results} currently trending books that are:
        1. Popular on social media and book communities
        2. Frequently discussed in book clubs
        3. Have high engagement and buzz in 2024
        4. Include bestsellers and viral book recommendations
        5. Mix of fiction and non-fiction
        6. Include both recent releases and books gaining renewed popularity
        
        Consider books that are:
        - BookTok favorites
        - Award winners and nominees from recent years
        - Books with high social media engagement
        - Celebrity book club picks
        - Books trending on Goodreads
        
        Format your response as a simple list of book titles, one per line.
        Only provide the book title, no descriptions or explanations.
        
        Example format:
        Fourth Wing
        Tomorrow, and Tomorrow, and Tomorrow
        Book Lovers
        
        Your trending book recommendations:
        """
        
        try:
            response = self.model.generate_content(prompt)
            trending_books = self._parse_recommendations(response.text)
            return trending_books[:max_results]
        except Exception as e:
            print(f"Error generating trending books: {e}")
            return self._get_fallback_trending_books(max_results)
    
    def get_top_rated_books(self, max_results=12):
        """
        Get top-rated books using Gemini AI based on critical acclaim and ratings
        
        Returns:
            list: List of top-rated book titles
        """
        prompt = f"""
        You are a literary critic and book expert with knowledge of the highest-rated books.
        
        Provide {max_results} top-rated books that have:
        1. Excellent average ratings (4.5+ stars) on platforms like Goodreads
        2. Critical acclaim from literary reviewers
        3. Awards and recognition from prestigious literary organizations
        4. Consistently high reader satisfaction
        5. Strong literary merit and quality writing
        6. Both classic and contemporary highly-rated books
        
        Consider books that are:
        - Winners of major literary awards (Pulitzer, Booker, etc.)
        - Books with outstanding Goodreads ratings
        - Critically acclaimed modern classics
        - Books consistently appearing on "best of" lists
        - Highly rated across different reader demographics
        
        Focus on books known for exceptional quality, brilliant writing, and universal appeal.
        
        Format your response as a simple list of book titles, one per line.
        Only provide the book title, no descriptions or explanations.
        
        Example format:
        The Seven Husbands of Evelyn Hugo
        Educated
        Where the Crawdads Sing
        
        Your top-rated book recommendations:
        """
        
        try:
            response = self.model.generate_content(prompt)
            top_rated_books = self._parse_recommendations(response.text)
            return top_rated_books[:max_results]
        except Exception as e:
            print(f"Error generating top-rated books: {e}")
            return self._get_fallback_top_rated_books(max_results)
    
    def _get_fallback_trending_books(self, max_results):
        """Fallback trending books if AI fails"""
        trending_books = [
            'Fourth Wing',
            'Tomorrow, and Tomorrow, and Tomorrow', 
            'Book Lovers',
            'The Seven Moons of Maali Almeida',
            'The Atlas Six',
            'People We Meet on Vacation',
            'The Song of Achilles',
            'It Ends with Us',
            'The House in the Cerulean Sea',
            'Mexican Gothic',
            'The Invisible Life of Addie LaRue',
            'Klara and the Sun'
        ]
        return trending_books[:max_results]
    
    def _get_fallback_top_rated_books(self, max_results):
        """Fallback top-rated books if AI fails"""
        top_rated_books = [
            'The Seven Husbands of Evelyn Hugo',
            'Educated',
            'Where the Crawdads Sing',
            'The Midnight Library',
            'Circe',
            'The Silent Patient',
            'Atomic Habits',
            'Becoming',
            'The Thursday Murder Club',
            'Project Hail Mary',
            'The Guest List',
            'Normal People'
        ]
        return top_rated_books[:max_results]

# Test function
def test_recommender():
    """Test the book recommender"""
    recommender = BookRecommender()
    
    # Test with sample preferences
    test_preferences = {
        'genres': ['Mystery', 'Thriller'],
        'favorite_books': ['Gone Girl', 'The Girl on the Train'],
        'favorite_authors': ['Gillian Flynn', 'Agatha Christie']
    }
    
    print("Testing Book Recommender...")
    print(f"User preferences: {test_preferences}")
    
    recommendations = recommender.generate_recommendations(test_preferences)
    
    print("\nRecommended books:")
    for i, book in enumerate(recommendations, 1):
        print(f"{i}. {book}")

if __name__ == "__main__":
    test_recommender()
    