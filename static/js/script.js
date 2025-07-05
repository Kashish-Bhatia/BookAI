document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recommendationForm');
    const loading = document.getElementById('loading');
    const recommendations = document.getElementById('recommendations');
    const bookList = document.getElementById('book-list');
    const getMoreBtn = document.getElementById('get-more');
    
    // Mobile navigation functionality
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        loading.classList.remove('hidden');
        recommendations.classList.add('hidden');
        
        // Get form data
        const formData = new FormData(form);
        const genre = formData.get('genre');
        const mood = formData.get('mood');
        const length = formData.get('length');
        const favoriteBook = formData.get('favorite-book');
        
        // Prepare data for API
        const requestData = {
            genres: [genre],
            favoriteBooks: favoriteBook ? favoriteBook : '',
            favoriteAuthors: '',
            additionalPreferences: `Looking for ${mood} books that are ${length} length. Current mood: ${mood}.`
        };
        
        try {
            // Make API call
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Display recommendations
            displayRecommendations(data.recommendations || data);
            
        } catch (error) {
            console.error('Error:', error);
            showError('Failed to get recommendations. Please try again.');
        } finally {
            // Hide loading state
            loading.classList.add('hidden');
        }
    });
    
    function displayRecommendations(books) {
        // Clear previous results
        bookList.innerHTML = '';
        
        if (!books || books.length === 0) {
            showError('No recommendations found. Please try different preferences.');
            return;
        }
        
        // Create book cards
        books.forEach((book, index) => {
            const bookCard = createBookCard(book, index + 1);
            bookList.appendChild(bookCard);
        });
        
        // Show recommendations section
        recommendations.classList.remove('hidden');
        
        // Scroll to recommendations
        recommendations.scrollIntoView({ behavior: 'smooth' });
    }
    
    
    function showError(message) {
        bookList.innerHTML = `
            <div class="error-message">
                <h3>😕 Oops!</h3>
                <p>${message}</p>
                <button onclick="location.reload()" class="retry-btn">Try Again</button>
            </div>
        `;
        recommendations.classList.remove('hidden');
    }
    
    // Get More Recommendations button
    getMoreBtn.addEventListener('click', function() {
        // Trigger form submission again
        form.dispatchEvent(new Event('submit'));
    });
    
    // Add some interactive effects
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('book-card') || e.target.closest('.book-card')) {
            const card = e.target.classList.contains('book-card') ? e.target : e.target.closest('.book-card');
            card.style.transform = 'scale(1.02)';
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 150);
        }
    });
    

});

// Global Add to Library event listener (works for all dynamically added elements)
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-add-library')) {
        e.preventDefault();
        const bookData = e.target.getAttribute('data-book-data');
        const bookTitle = e.target.getAttribute('data-book-title');
        
        if (bookData) {
            // Handle detailed book data
            try {
                const book = JSON.parse(bookData);
                addToLibrary(book);
            } catch (error) {
                console.error('Error parsing book data:', error);
                alert('Error adding book to library. Please try again.');
            }
        } else if (bookTitle) {
            // Handle simple book title
            const simpleBook = {
                title: bookTitle,
                author_string: 'Various Authors',
                published_date: 'Contemporary',
                description: 'AI-recommended book',
                thumbnail: '',
                average_rating: null,
                ratings_count: null
            };
            addToLibrary(simpleBook);
        }
    }
});

// Global createBookCard function
function createBookCard(book, rank) {
    const card = document.createElement('div');
    card.className = 'book-card';
    
    const thumbnail = book.thumbnail || 'https://via.placeholder.com/128x192/cccccc/666666?text=No+Cover';
    const rating = book.average_rating ? `⭐ ${book.average_rating}/5` : 'No rating';
    const ratingCount = book.ratings_count ? `(${book.ratings_count.toLocaleString()} reviews)` : '';
    const pageCount = book.page_count ? `📄 ${book.page_count} pages` : '';
    const publishedYear = book.published_date ? book.published_date.split('-')[0] : 'Unknown';
    
    card.innerHTML = `
        <div class="book-rank">#${rank}</div>
        <div class="book-image">
            <img src="${thumbnail}" alt="${book.title}" loading="lazy">
        </div>
        <div class="book-info">
            <h3 class="book-title">${book.title}</h3>
            <p class="book-author">by ${book.author_string || 'Unknown Author'}</p>
            <p class="book-published">Published: ${publishedYear}</p>
            
            <div class="book-rating">
                <span class="rating">${rating}</span>
                <span class="rating-count">${ratingCount}</span>
            </div>
            
            ${pageCount ? `<p class="book-pages">${pageCount}</p>` : ''}
            
            ${book.categories && book.categories.length > 0 ? 
                `<div class="book-categories">
                    ${book.categories.slice(0, 2).map(cat => `<span class="category-tag">${cat}</span>`).join('')}
                </div>` : ''
            }
            
            <p class="book-description">
                ${book.description ? 
                    (book.description.length > 150 ? 
                        book.description.substring(0, 150) + '...' : 
                        book.description) : 
                    'No description available.'}
            </p>
            
            ${book.recommendation_explanation ? 
                `<div class="recommendation-reason">
                    <strong>Why this book:</strong> ${book.recommendation_explanation}
                </div>` : ''
            }
            
            ${book.match_reasons && book.match_reasons.length > 0 ? 
                `<div class="match-reasons">
                    ${book.match_reasons.map(reason => `<span class="match-tag">${reason}</span>`).join('')}
                </div>` : ''
            }
            
            <div class="book-actions">
                ${book.preview_link ?
                    `<a href="${book.preview_link}" target="_blank" class="btn-preview">📖 Preview</a>` : ''
                }
                ${book.info_link ?
                    `<a href="${book.info_link}" target="_blank" class="btn-info">ℹ️ More Info</a>` : ''
                }
                <button class="btn-add-library" data-book-data='${JSON.stringify(book).replace(/'/g, "&#39;")}'>
                    📚 Add to Library
                </button>
            </div>
        </div>
    `;
    
    return card;
}

// Global library functions
function addToLibrary(book) {
    let library = JSON.parse(localStorage.getItem('library')) || [];
    
    // Check if book is already in library
    const exists = library.some(existingBook => existingBook.title === book.title);
    if (exists) {
        alert(`"${book.title}" is already in your library!`);
        return;
    }
    
    library.push(book);
    localStorage.setItem('library', JSON.stringify(library));
    alert(`Added "${book.title}" to your library!`);
}

function removeFromLibrary(title) {
    let library = JSON.parse(localStorage.getItem('library')) || [];
    library = library.filter(book => book.title !== title);
    localStorage.setItem('library', JSON.stringify(library));
    alert(`Removed "${title}" from your library.`);
    location.reload();
}

// Global functions for sidebar community features
function loadTrendingBooks() {
    showLoadingState();
    
    fetch('/api/trending', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.books) {
            displaySidebarBooks(data.books, 'Trending Books 🔥');
        } else {
            showError('No trending books found. Please try again later.');
        }
    })
    .catch(error => {
        console.error('Error fetching trending books:', error);
        showError('Failed to load trending books. Please try again.');
    })
    .finally(() => {
        hideLoadingState();
    });
}

function loadTopRatedBooks() {
    showLoadingState();
    
    fetch('/api/top-rated', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success && data.books) {
            displaySidebarBooks(data.books, 'Top Rated Books ⭐');
        } else {
            showError('No top-rated books found. Please try again later.');
        }
    })
    .catch(error => {
        console.error('Error fetching top-rated books:', error);
        showError('Failed to load top-rated books. Please try again.');
    })
    .finally(() => {
        hideLoadingState();
    });
}

function displaySidebarBooks(books, title, containerId = 'book-list') {
    // Clear previous results
    const bookList = document.getElementById(containerId);
    if (!bookList) {
        console.error(`Container with ID '${containerId}' not found`);
        return;
    }
    
    bookList.innerHTML = '';
    
    // Update the recommendations section title if it exists
    const recommendationsSection = document.getElementById('recommendations');
    if (recommendationsSection) {
        const titleElement = recommendationsSection.querySelector('h2');
        if (titleElement) {
            titleElement.innerHTML = `<i class="fas fa-stars"></i> ${title}`;
        }
        // Show recommendations section
        recommendationsSection.classList.remove('hidden');
        // Scroll to recommendations
        recommendationsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Create book cards
    books.forEach((book, index) => {
        const bookCard = createBookCard(book, index + 1);
        bookList.appendChild(bookCard);
    });
}

function showLoadingState() {
    const loading = document.getElementById('loading');  
    const recommendations = document.getElementById('recommendations');  
    
    if (loading) {
        loading.classList.remove('hidden');  
    }
    if (recommendations) {
        recommendations.classList.add('hidden');  
    }
}

function hideLoadingState() {
    const loading = document.getElementById('loading');  
    if (loading) {
        loading.classList.add('hidden');  
    }
}

// Load library on library page
if (window.location.pathname.includes('Library.html') || window.location.pathname.includes('/library')) {
    document.addEventListener('DOMContentLoaded', function() {
        const librarySection = document.getElementById('library-section');
        if (librarySection) {
            let library = JSON.parse(localStorage.getItem('library')) || [];
            
            if (library.length === 0) {
                librarySection.innerHTML = '<p>No books in your library. Add some books from the recommendations!</p>';
            } else {
                librarySection.innerHTML = library.map(book => {
                    const thumbnail = book.thumbnail || 'https://via.placeholder.com/80x120/cccccc/666666?text=No+Cover';
                    const rating = book.average_rating ? `⭐ ${book.average_rating}/5` : 'No rating';
                    const publishedYear = book.published_date ? book.published_date.split('-')[0] : 'Unknown';
                    
                    return `
                        <div class="library-book">
                            <div class="book-image" style="text-align: center; margin-bottom: 1rem;">
                                <img src="${thumbnail}" alt="${book.title}" style="max-width: 80px; height: auto; border-radius: 6px;">
                            </div>
                            <h3>${book.title}</h3>
                            <p>by ${book.author_string || 'Unknown Author'}</p>
                            <p style="color: var(--text-muted); font-size: 0.9rem;">Published: ${publishedYear}</p>
                            <p style="color: var(--text-muted); font-size: 0.9rem;">${rating}</p>
                            <button onclick='removeFromLibrary("${book.title.replace(/'/g, "\\'")}")'>
                                🗑️ Remove from Library
                            </button>
                        </div>`;
                }).join('');
            }
        }
    });
}

// Load trending books page function
function loadTrendingBooksPage() {
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    const booksContainer = document.getElementById('trending-books');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (errorElement) errorElement.classList.add('hidden');
    if (booksContainer) booksContainer.innerHTML = '';
    
    fetch('/api/trending', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Trending API response:', data);
        if (data.success && data.books && data.books.length > 0) {
            console.log('Displaying', data.books.length, 'trending books');
            // Display detailed book objects
            displayBooksOnPage(data.books, 'trending-books');
        } else {
            console.log('No trending books found or API failed');
            showPageError('Unable to load trending books at this time.');
        }
    })
    .catch(error => {
        console.error('Error fetching trending books:', error);
        showPageError('Please check your connection and try again.');
    })
    .finally(() => {
        if (loadingElement) loadingElement.classList.add('hidden');
    });
}

// Load top-rated books page function
function loadTopRatedBooksPage() {
    const loadingElement = document.getElementById('loading');
    const errorElement = document.getElementById('error-message');
    const booksContainer = document.getElementById('top-rated-books');
    
    if (loadingElement) loadingElement.classList.remove('hidden');
    if (errorElement) errorElement.classList.add('hidden');
    if (booksContainer) booksContainer.innerHTML = '';
    
    fetch('/api/top-rated', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Top-rated API response:', data);
        if (data.success && data.books && data.books.length > 0) {
            console.log('Displaying', data.books.length, 'top-rated books');
            // Display detailed book objects
            displayBooksOnPage(data.books, 'top-rated-books');
        } else {
            console.log('No top-rated books found or API failed');
            showPageError('Unable to load top-rated books at this time.');
        }
    })
    .catch(error => {
        console.error('Error fetching top-rated books:', error);
        showPageError('Please check your connection and try again.');
    })
    .finally(() => {
        if (loadingElement) loadingElement.classList.add('hidden');
    });
}

// Display books on dedicated pages
function displayBooksOnPage(books, containerId) {
    console.log(`displayBooksOnPage called with ${books.length} books for container ${containerId}`);
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found`);
        return;
    }
    
    container.innerHTML = '';
    
    books.forEach((book, index) => {
        console.log(`Creating card for book ${index + 1}: ${book.title}`);
        try {
            const bookCard = createBookCard(book, index + 1);
            container.appendChild(bookCard);
        } catch (error) {
            console.error(`Error creating book card for ${book.title}:`, error);
        }
    });
    
    console.log(`Successfully added ${container.children.length} book cards to ${containerId}`);
}

// Show error on dedicated pages
function showPageError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.classList.remove('hidden');
        const errorText = errorElement.querySelector('p');
        if (errorText) {
            errorText.textContent = message;
        }
    }
}

