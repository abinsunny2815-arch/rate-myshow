// Watchlist functionality
async function addToWatchlist(omdbId) {
    try {
        const response = await fetch(`/titles/${omdbId}/watchlist/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=to-watch`
        });

        if (response.ok) {
            const data = await response.json();
            showNotification(data.created ? 'Added to watchlist!' : 'Updated watchlist!');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error updating watchlist', 'error');
    }
}

async function removeFromWatchlist(omdbId) {
    try {
        const response = await fetch(`/titles/${omdbId}/watchlist/remove/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        if (response.ok) {
            showNotification('Removed from watchlist!');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error removing from watchlist', 'error');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function showNotification(message, type = 'success') {
    // Simple notification - can be enhanced
    alert(message);
}
