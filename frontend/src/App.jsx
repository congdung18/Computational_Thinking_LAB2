import { useState } from 'react';
import { Navigation, CloudSun, SlidersHorizontal, Sparkle, CheckCircle, AlertCircle } from 'lucide-react';

function App() {
  const [weather, setWeather] = useState('');
  const [preferences, setPreferences] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!weather || !preferences) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Route through Nginx proxy
      const API_URL = '/api/suggest';
      
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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get recommendation from server');
      }

      const data = await response.json();
      
      // Format markdown-like response to simple HTML
      const formattedText = data.suggestion
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');

      setResult(formattedText);
    } catch (err) {
      console.error('API Error:', err);
      setError(
        err.message === 'Failed to fetch' 
          ? 'Cannot connect to backend server. Is it running on port 8000?' 
          : err.message
      );
      
      // Hide error after 5 seconds
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setWeather('');
    setPreferences('');
    setResult(null);
  };

  return (
    <>
      <div className="ambient-background">
        <div className="blob blob-1"></div>
        <div className="blob blob-2"></div>
      </div>

      <main className="app-container">
        <header>
          <h1>
            <Navigation size={40} color="#c084fc" />
            <span>Transit</span><span style={{ color: '#fff' }}>AI</span>
          </h1>
          <p>Intelligent travel recommendations tailored to your conditions.</p>
        </header>

        {!result ? (
          <section className="glass-card">
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label htmlFor="weather">
                  <CloudSun size={20} /> Weather Conditions
                </label>
                <input 
                  type="text" 
                  id="weather" 
                  value={weather}
                  onChange={(e) => setWeather(e.target.value)}
                  placeholder="e.g., Heavy rain, 25°C sunny, snowing..." 
                  required
                />
              </div>

              <div className="input-group">
                <label htmlFor="preferences">
                  <SlidersHorizontal size={20} /> Your Preferences
                </label>
                <textarea 
                  id="preferences" 
                  rows="3" 
                  value={preferences}
                  onChange={(e) => setPreferences(e.target.value)}
                  placeholder="e.g., I need to travel 5km, prefer eco-friendly, want to exercise..." 
                  required
                ></textarea>
              </div>

              <button type="submit" className="btn-primary" disabled={isLoading}>
                {isLoading ? (
                  <div className="loader"></div>
                ) : (
                  <>
                    <span>Get Recommendation</span>
                    <Sparkle size={20} />
                  </>
                )}
              </button>
            </form>
          </section>
        ) : (
          <section className="glass-card">
            <div className="result-header">
              <CheckCircle size={28} />
              <h2>Recommended Transport</h2>
            </div>
            <div 
              className="result-content"
              dangerouslySetInnerHTML={{ __html: result }}
            ></div>
            <button onClick={handleReset} className="btn-secondary">
              Plan Another Trip
            </button>
          </section>
        )}

        <div className={`toast ${error ? 'show' : ''}`}>
          <AlertCircle size={24} />
          <span>{error}</span>
        </div>
      </main>
    </>
  );
}

export default App;
