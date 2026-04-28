import { useState, useEffect } from 'react';
import { Navigation, CloudSun, SlidersHorizontal, Sparkle, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import { auth, googleProvider } from './firebase';
import { signInWithPopup, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';

function App() {
  const [weather, setWeather] = useState('');
  const [preferences, setPreferences] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Authentication State
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      setUser(currentUser);
      if (currentUser) {
        try {
          const token = await currentUser.getIdToken();
          
          // Sync user with backend
          await fetch('/api/auth', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          // Fetch chat history
          const res = await fetch('/api/history', {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          const data = await res.json();
          if (data.history) setHistory(data.history);
          
        } catch (err) {
          console.error("Error syncing auth/history:", err);
        }
      } else {
        setHistory([]);
      }
      setAuthLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleGoogleLogin = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleEmailAuth = async (e) => {
    e.preventDefault();
    try {
      if (isLoginMode) {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
    } catch (err) {
      setError(err.message);
      setTimeout(() => setError(null), 5000);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    setResult(null);
    setHistory([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!weather || !preferences) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // Route through Nginx proxy
      const API_URL = '/api/suggest';
      
      const token = await auth.currentUser.getIdToken();

      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
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

      // Refresh history silently
      try {
        const historyRes = await fetch('/api/history', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const historyData = await historyRes.json();
        if (historyData.history) setHistory(historyData.history);
      } catch (e) {
        console.error("Failed to refresh history", e);
      }

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
          {user && (
            <button className="btn-secondary" onClick={handleLogout} style={{ marginTop: '1rem', padding: '0.5rem 1rem', display: 'inline-flex', alignItems: 'center' }}>
              <LogOut size={16} style={{ marginRight: '8px' }} /> Logout ({user.email})
            </button>
          )}
        </header>

        {authLoading ? (
            <div className="loader" style={{ margin: '2rem auto' }}></div>
        ) : !user ? (
            <section className="glass-card">
              <h2 style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#fff' }}>
                {isLoginMode ? 'Login' : 'Sign Up'}
              </h2>
              <form onSubmit={handleEmailAuth}>
                <div className="input-group">
                  <label>Email</label>
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div className="input-group">
                  <label>Password</label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                </div>
                <button type="submit" className="btn-primary" style={{ marginTop: '1rem' }}>
                   {isLoginMode ? 'Login' : 'Sign Up'}
                </button>
              </form>
              <div style={{ textAlign: 'center', margin: '1.5rem 0', color: 'rgba(255, 255, 255, 0.6)' }}>OR</div>
              <button onClick={handleGoogleLogin} className="btn-secondary" style={{ width: '100%' }}>
                Continue with Google
              </button>
              <p style={{ textAlign: 'center', marginTop: '1.5rem', cursor: 'pointer', color: '#c084fc', textDecoration: 'underline' }} onClick={() => setIsLoginMode(!isLoginMode)}>
                {isLoginMode ? 'Need an account? Sign up' : 'Already have an account? Login'}
              </p>
            </section>
        ) : !result ? (
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

        {user && !authLoading && history.length > 0 && (
          <section className="glass-card" style={{ marginTop: '2rem' }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle size={20} color="#a855f7" /> Past Suggestions
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {history.map((item, index) => (
                <div key={index} style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}>
                  <div style={{ fontSize: '0.8rem', color: '#c084fc', marginBottom: '0.8rem', fontWeight: 'bold' }}>
                    {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'Recent'}
                  </div>
                  <div style={{ marginBottom: '0.8rem', fontSize: '0.95rem' }}>
                    <strong>Weather:</strong> {item.weather} <br/>
                    <strong>Preferences:</strong> {item.preferences}
                  </div>
                  <div style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.8)', paddingLeft: '10px', borderLeft: '2px solid #a855f7' }}>
                    <div dangerouslySetInnerHTML={{ __html: (item.suggestion || '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\*(.*?)\*/g, '<em>$1</em>').replace(/\n/g, '<br>') }} />
                  </div>
                </div>
              ))}
            </div>
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
