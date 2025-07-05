#!/usr/bin/env python3

from app import recommendation_engine, book_api

def test_trending_endpoint():
    """Test the trending books endpoint logic"""
    try:
        print("🔍 Testing AI recommender...")
        trending_titles = recommendation_engine.ai_recommender.get_trending_books()
        print(f"✅ AI trending titles: {trending_titles}")
        
        print("\n🔍 Testing Google Books API...")
        detailed_books = book_api.get_multiple_books(trending_titles)
        print(f"✅ Google Books found {len(detailed_books)} books")
        
        print("\n🔍 Testing book enhancement...")
        for book in detailed_books:
            book['is_trending'] = True
            book['trending_rank'] = detailed_books.index(book) + 1
        
        print(f"✅ Enhanced books: {len(detailed_books)} books with trending data")
        print(f"First book title: {detailed_books[0]['title'] if detailed_books else 'None'}")
        
        return {
            'success': True,
            'books': detailed_books,
            'total_found': len(detailed_books)
        }
        
    except Exception as e:
        print(f"❌ Error in trending endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'books': []
        }

if __name__ == "__main__":
    result = test_trending_endpoint()
    print(f"\n📊 Final result: {result}")
