function toggleFeed(button, action) {
    const feed = button.closest('.list-group-item');
    const url = feed.getAttribute('data-url');
    const endpointUrl = feed.getAttribute('data-toggle-endpoint');
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const formData = new FormData();
    formData.append('url', url);
    formData.append('action', action);
    // DO THE WERK SON
    fetch(endpointUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    }).then(response => response.json()).then(data => {
        if (data.success) {
            if (data.action === 'added') {
                button.outerHTML = `<button class="btn btn-danger" onclick="toggleFeed(this, 'remove')">-</button>`;
            } else if (data.action === 'removed') {
                button.outerHTML = `<button class="btn btn-secondary" onclick="toggleFeed(this, 'add')">+</button>`;
            }
        } else {
            alert('Something went wrong...' + data.error);
        }
    }).catch(error => console.log('Error:', error));
}