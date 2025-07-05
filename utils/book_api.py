import requests
import time

class GoogleBooksAPI:
    def __init__(self):
        """Initialize Google Books API client"""
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        self.session = requests.Session()
    
    def search_book(self, title, author=None):
        """
        Search for a single book by title and optionally author
        
        Args:
            title (str): Book title
            author (str, optional): Author name
        
        Returns:
            dict: Book information or None if not found
        """
        # Create search query
        query = f'intitle:"{title}"'
        if author:
            query += f' inauthor:"{author}"'
        
        params = {
            'q': query,
            'maxResults': 1,
            'printType': 'books'
        }
        
        try:
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items'):
                return self._extract_book_info(data['items'][0])
            else:
                # Try a broader search if exact search fails
                return self._fallback_search(title)
        
        except Exception as e:
            print(f"Error searching for '{title}': {e}")
            return None
    
    def get_multiple_books(self, book_titles):
        """
        Get information for multiple books
        
        Args:
            book_titles (list): List of book titles
        
        Returns:
            list: List of book information dictionaries
        """
        books = []
        
        for title in book_titles:
            book_info = self.search_book(title)
            
            if book_info:
                books.append(book_info)
            else:
                # Add a placeholder for books not found
                books.append(self._create_placeholder_book(title))
            
            # Small delay to be respectful to the API
            time.sleep(0.5)
        
        return books
    
    def _extract_book_info(self, book_item):
        """Extract relevant information from Google Books API response"""
        volume_info = book_item.get('volumeInfo', {})
        
        # Extract basic information
        title = volume_info.get('title', 'Unknown Title')
        authors = volume_info.get('authors', ['Unknown Author'])
        published_date = volume_info.get('publishedDate', 'Unknown')
        description = volume_info.get('description', 'Description not available.')
        
        # Extract ratings
        average_rating = volume_info.get('averageRating')
        ratings_count = volume_info.get('ratingsCount')
        
        # Extract categories/genres
        categories = volume_info.get('categories', [])
        
        # Extract cover image
        image_links = volume_info.get('imageLinks', {})
        thumbnail = image_links.get('thumbnail', image_links.get('smallThumbnail', ''))
        
        # Replace HTTP with HTTPS for security
        if thumbnail and thumbnail.startswith('http:'):
            thumbnail = thumbnail.replace('http:', 'https:')
        
        # Extract page count
        page_count = volume_info.get('pageCount')
        
        # Extract publisher
        publisher = volume_info.get('publisher', 'Unknown Publisher')
        
        # Create clean description (limit length)
        if description and len(description) > 500:
            description = description[:497] + "..."
        
        return {
            'title': title,
            'authors': authors,
            'author_string': ', '.join(authors),
            'published_date': published_date,
            'description': description,
            'average_rating': average_rating,
            'ratings_count': ratings_count,
            'categories': categories,
            'thumbnail': thumbnail,
            'page_count': page_count,
            'publisher': publisher,
            'google_books_id': book_item.get('id'),
            'preview_link': volume_info.get('previewLink', ''),
            'info_link': volume_info.get('infoLink', '')
        }
    
    def _fallback_search(self, title):
        """Try a broader search if exact search fails"""
        # Remove common words and try again
        clean_title = title.replace('The ', '').replace('A ', '').replace('An ', '')
        words = clean_title.split()
        
        if len(words) > 1:
            # Try searching with just the first few words
            fallback_query = ' '.join(words[:3])
            
            params = {
                'q': fallback_query,
                'maxResults': 5,
                'printType': 'books'
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('items'):
                    # Return the first result that seems relevant
                    for item in data['items']:
                        item_title = item.get('volumeInfo', {}).get('title', '').lower()
                        if any(word.lower() in item_title for word in words[:2]):
                            return self._extract_book_info(item)
            
            except Exception as e:
                print(f"Fallback search failed: {e}")
        
        return None
    
    def _create_placeholder_book(self, title):
        """Create a placeholder for books that couldn't be found"""
        return {
            'title': title,
            'authors': ['Unknown Author'],
            'author_string': 'Unknown Author',
            'published_date': 'Unknown',
            'description': 'Book information not available. This might be a lesser-known title or the search didn\'t find an exact match.',
            'average_rating': None,
            'ratings_count': None,
            'categories': [],
            'thumbnail': '',
            'page_count': None,
            'publisher': 'Unknown Publisher',
            'google_books_id': None,
            'preview_link': '',
            'info_link': '',
            'placeholder': True  # Flag to indicate this is a placeholder
        }
    
    def get_trending_books(self, max_results=12):
        """Get trending books based on popularity metrics"""
        # Define popular/trending search terms and topics
        trending_queries = [
            'bestseller 2024',
            'popular fiction',
            'trending books',
            'award winning books',
            'book club picks',
            'new releases'
        ]
        
        trending_books = []
        books_per_query = max_results // len(trending_queries)
        
        for query in trending_queries:
            params = {
                'q': query,
                'maxResults': books_per_query + 2,  # Get a few extra to filter
                'printType': 'books',
                'orderBy': 'relevance'
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('items'):
                    for item in data['items']:
                        book_info = self._extract_book_info(item)
                        
                        # Add all books first, then filter later
                        if len(trending_books) < max_results * 2:  # Get more books to filter from
                            # Add trending score based on ratings count and rating
                            trending_score = self._calculate_trending_score(book_info)
                            book_info['trending_score'] = trending_score
                            trending_books.append(book_info)
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching trending books for '{query}': {e}")
                continue
        
        # Remove duplicates and filter for quality books
        trending_books = self._remove_duplicates(trending_books)
        
        # Filter for books with at least some ratings or use fallback
        quality_books = [book for book in trending_books 
                        if ((book.get('ratings_count') or 0) > 10 and (book.get('average_rating') or 0) >= 3.0)]
        
        # If we don't have enough quality books, use all books
        if len(quality_books) < max_results:
            quality_books = trending_books
        
        # Sort by trending score
        quality_books.sort(key=lambda x: x.get('trending_score', 0), reverse=True)
        
        return quality_books[:max_results]
    
    def get_top_rated_books(self, max_results=12):
        """Get top-rated books based on average ratings"""
        # Search for highly rated books in popular categories
        categories = [
            'fiction',
            'mystery', 
            'romance',
            'science fiction',
            'fantasy',
            'biography',
            'self help',
            'history'
        ]
        
        top_rated_books = []
        books_per_category = max_results // len(categories)
        
        for category in categories:
            params = {
                'q': f'subject:{category}',
                'maxResults': books_per_category + 3,  # Get extra to filter
                'printType': 'books',
                'orderBy': 'relevance'
            }
            
            try:
                response = self.session.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data.get('items'):
                    for item in data['items']:
                        book_info = self._extract_book_info(item)
                        
                        # Add all books first, then filter later
                        if len(top_rated_books) < max_results * 2:  # Get more books to filter from
                            top_rated_books.append(book_info)
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching top-rated books for '{category}': {e}")
                continue
        
        # Remove duplicates and filter for quality books
        top_rated_books = self._remove_duplicates(top_rated_books)
        
        # Filter for books with decent ratings or use fallback
        quality_books = [book for book in top_rated_books 
                        if ((book.get('average_rating') or 0) >= 3.5 and (book.get('ratings_count') or 0) > 5)]
        
        # If we don't have enough quality books, use all books
        if len(quality_books) < max_results:
            quality_books = top_rated_books
        
        # Sort by rating and popularity
        quality_books.sort(key=lambda x: ((x.get('average_rating') or 0), (x.get('ratings_count') or 0)), reverse=True)
        
        return quality_books[:max_results]
    
    def _calculate_trending_score(self, book_info):
        """Calculate a trending score based on ratings and popularity"""
        rating = book_info.get('average_rating') or 0
        ratings_count = book_info.get('ratings_count') or 0
        
        # Base score from rating
        score = rating * 20  # Scale rating to 0-100
        
        # Popularity bonus based on ratings count
        if ratings_count > 10000:
            score += 30
        elif ratings_count > 5000:
            score += 20
        elif ratings_count > 1000:
            score += 10
        elif ratings_count > 100:
            score += 5
        
        return min(100, score)  # Cap at 100
    
    def _remove_duplicates(self, books):
        """Remove duplicate books based on title and author"""
        seen = set()
        unique_books = []
        
        for book in books:
            # Create a key based on title and first author
            key = (book['title'].lower(), book['authors'][0].lower() if book['authors'] else '')
            
            if key not in seen:
                seen.add(key)
                unique_books.append(book)
        
        return unique_books

# Test function
def test_books_api():
    """Test the Google Books API integration"""
    api = GoogleBooksAPI()
    
    # Test with some popular books
    test_books = [
        "The Silent Patient",
        "Where the Crawdads Sing",
        "Educated",
        "The Seven Husbands of Evelyn Hugo"
    ]
    
    print("Testing Google Books API...")
    print("=" * 50)
    
    books = api.get_multiple_books(test_books)
    
    print("\nResults:")
    print("=" * 50)
    
    for book in books:
        print(f"\n📚 {book['title']}")
        print(f"👤 Author(s): {book['author_string']}")
        print(f"📅 Published: {book['published_date']}")
        print(f"⭐ Rating: {book['average_rating'] if book['average_rating'] else 'No rating'}")
        print(f"📄 Pages: {book['page_count'] if book['page_count'] else 'Unknown'}")
        print(f"📝 Description: {book['description'][:100]}...")
        if book['thumbnail']:
            print(f"🖼️ Cover: Available")
        print("-" * 30)

if __name__ == "__main__":
    test_books_api()

    