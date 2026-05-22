// RateMyShow JavaScript utilities

// Add to watchlist
function addToWatchlist(omdbId) {
    const csrf = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (!csrf) {
        window.location.href = '/accounts/login/';
        return;
    }

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrf.value);
    formData.append('status', 'to-watch');

    fetch(`/titles/${omdbId}/watchlist/`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(data.created ? 'Added to watchlist!' : 'Updated watchlist!');
            }
        })
        .catch(error => console.error('Error:', error));
}

// Submit rating via AJAX
function submitRating(omdbId, score) {
    const csrf = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (!csrf) {
        window.location.href = '/accounts/login/';
        return;
    }

    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrf.value);
    formData.append('score', score);

    fetch(`/titles/${omdbId}/rate/`, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Rating submitted: ${data.rating}/10`);
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Search suggestions
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.querySelector('input[name="q"]');
    if (!searchInput) return;

    searchInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();
        if (query.length < 2) return;

        // You could add AJAX search suggestions here
        // For now, just allowing form submission
    });
});

// Dark mode toggle (if needed)
function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
}

// Initialize dark mode from localStorage
if (localStorage.getItem('darkMode') === 'false') {
    document.documentElement.classList.remove('dark');
}
