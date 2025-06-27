self.addEventListener('fetch', (event) => {
    // Only cache GET requests
    if (event.request.method === 'GET') {
        event.respondWith(
            caches.match(event.request).then((response) => {
                return response || fetch(event.request).then((fetchResponse) => {
                    return caches.open('dynamic-cache').then((cache) => {
                        cache.put(event.request, fetchResponse.clone());
                        return fetchResponse;
                    });
                });
            })
        );
    }
});