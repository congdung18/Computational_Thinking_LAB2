document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('suggestion-form');
    const submitBtn = document.getElementById('submit-btn');
    const resultContainer = document.getElementById('result-container');
    const resultContent = document.getElementById('result-content');
    const resetBtn = document.getElementById('reset-btn');
    const toast = document.getElementById('error-toast');
    const errorMessage = document.getElementById('error-message');

    // API URL configuration (routed through Nginx proxy in Docker)
    const API_URL = '/api/suggest';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const weather = document.getElementById('weather').value.trim();
        const preferences = document.getElementById('preferences').value.trim();

        if (!weather || !preferences) return;

        // Start loading state
        setLoading(true);
        hideToast();
        resultContainer.classList.add('hidden');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    weather: weather,
                    preferences: preferences
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to get recommendation from server');
            }

            const data = await response.json();
            
            // Format markdown-like response to simple HTML
            const formattedText = data.suggestion
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');

            // Show result
            resultContent.innerHTML = formattedText;
            resultContainer.classList.remove('hidden');
            form.parentElement.classList.add('hidden'); // Hide form card
            resetBtn.classList.remove('hidden');

        } catch (error) {
            console.error('API Error:', error);
            showToast(error.message === 'Failed to fetch' ? 
                'Cannot connect to backend server. Is it running?' : 
                error.message);
        } finally {
            setLoading(false);
        }
    });

    resetBtn.addEventListener('click', () => {
        form.reset();
        resultContainer.classList.add('hidden');
        form.parentElement.classList.remove('hidden'); // Show form card
        resetBtn.classList.add('hidden');
    });

    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
        } else {
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
        }
    }

    function showToast(message) {
        errorMessage.textContent = message;
        toast.classList.remove('hidden');
        
        setTimeout(() => {
            hideToast();
        }, 5000);
    }

    function hideToast() {
        toast.classList.add('hidden');
    }
});