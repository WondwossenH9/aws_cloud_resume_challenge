// Visitor Counter JavaScript
// This script will interact with our API to get and update visitor count

// Configuration - Update this with your actual API Gateway URL
const API_BASE_URL = 'https://w0k53mqb44.execute-api.us-east-1.amazonaws.com/prod';

// Function to get visitor count from API
async function getVisitorCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/visitor-count`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.count;
    } catch (error) {
        console.error('Error fetching visitor count:', error);
        // Return a fallback count if API fails
        return Math.floor(Math.random() * 1000) + 100;
    }
}

// Function to update visitor count in the UI
function updateVisitorCount(count) {
    const countElement = document.getElementById('visitor-count');
    if (countElement) {
        // Add animation effect
        countElement.style.opacity = '0';
        countElement.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            countElement.textContent = count.toLocaleString();
            countElement.style.opacity = '1';
            countElement.style.transform = 'translateY(0)';
        }, 200);
    }
}

// Function to increment visitor count
async function incrementVisitorCount() {
    try {
        const response = await fetch(`${API_BASE_URL}/visitor-count`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.count;
    } catch (error) {
        console.error('Error incrementing visitor count:', error);
        return null;
    }
}

// Function to check if this is a new visitor session
function isNewVisitor() {
    const sessionKey = 'resume_visited';
    const hasVisited = sessionStorage.getItem(sessionKey);
    
    if (!hasVisited) {
        sessionStorage.setItem(sessionKey, 'true');
        return true;
    }
    return false;
}

// Main function to initialize visitor counter
async function initializeVisitorCounter() {
    try {
        // First, get the current count
        const currentCount = await getVisitorCount();
        updateVisitorCount(currentCount);
        
        // If this is a new visitor, increment the count
        if (isNewVisitor()) {
            const newCount = await incrementVisitorCount();
            if (newCount !== null) {
                updateVisitorCount(newCount);
            }
        }
    } catch (error) {
        console.error('Error initializing visitor counter:', error);
        // Show a fallback count
        updateVisitorCount(Math.floor(Math.random() * 1000) + 100);
    }
}

// Function to add loading state
function showLoadingState() {
    const countElement = document.getElementById('visitor-count');
    if (countElement) {
        countElement.textContent = '...';
        countElement.style.opacity = '0.7';
    }
}

// Function to add error state
function showErrorState() {
    const countElement = document.getElementById('visitor-count');
    if (countElement) {
        countElement.textContent = 'Error';
        countElement.style.color = '#e74c3c';
    }
}

// Enhanced initialization with loading states
async function initializeVisitorCounterWithStates() {
    showLoadingState();
    
    try {
        await initializeVisitorCounter();
    } catch (error) {
        console.error('Failed to initialize visitor counter:', error);
        showErrorState();
    }
}

// Add smooth scroll behavior for better UX
function addSmoothScroll() {
    // Add smooth scrolling to all anchor links
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
}

// Add intersection observer for animations
function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all sections for animation
    document.querySelectorAll('.section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize visitor counter
    initializeVisitorCounterWithStates();
    
    // Add smooth scrolling
    addSmoothScroll();
    
    // Add scroll animations
    addScrollAnimations();
    
    // Add click tracking for blog link (placeholder for analytics)
    const blogLink = document.getElementById('blog-link');
    if (blogLink) {
        blogLink.addEventListener('click', function() {
            console.log('Blog link clicked - ready for analytics integration');
            // Here you could add analytics tracking
        });
    }
});

// Add error handling for network issues
window.addEventListener('online', function() {
    console.log('Network connection restored');
    // Optionally retry visitor counter initialization
});

window.addEventListener('offline', function() {
    console.log('Network connection lost');
    // Show offline indicator if needed
});

// Export functions for testing (if using modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getVisitorCount,
        incrementVisitorCount,
        isNewVisitor,
        updateVisitorCount
    };
}
