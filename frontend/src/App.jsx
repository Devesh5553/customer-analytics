// frontend/src/App.jsx
import { useState, useEffect, useRef } from 'react'
import { Play, Square, Settings, RefreshCw, Moon, Sun, Search, Activity, Users, ShoppingCart, DollarSign } from 'lucide-react'
import './App.css'

function App() {
  const [theme, setTheme] = useState(() => {
    // Read local storage or fallback to system preference
    const saved = localStorage.getItem('theme')
    if (saved) return saved
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  // Telemetry Metrics States
  const [events, setEvents] = useState([])
  const [totalEvents, setTotalEvents] = useState(0)
  const [purchasesCount, setPurchasesCount] = useState(0)
  const [totalRevenue, setTotalRevenue] = useState(0)

  // Rolling chart counts
  const [rollingCounts, setRollingCounts] = useState([2, 5, 3, 6, 8, 4, 7, 5, 9, 6])
  const activeEventsCountRef = useRef(0)

  // Simulator Control States
  const [isSimulating, setIsSimulating] = useState(false)
  const [delaySeconds, setDelaySeconds] = useState(2.0)
  const [sliderVal, setSliderVal] = useState(2.0)

  // User Search / Recommendation Explainer States
  const [searchUserId, setSearchUserId] = useState('')
  const [recommendationResult, setRecommendationResult] = useState(null)
  const [searchError, setSearchError] = useState('')

  // Segment Analytics States
  const [segmentsSummary, setSegmentsSummary] = useState(null)
  const [isRetraining, setIsRetraining] = useState(false)

  // WebSocket reference
  const wsRef = useRef(null)

  // 1. Sync theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  // 2. Fetch initial values and status from backend on mount
  useEffect(() => {
    fetchSimulatorStatus()
    fetchGeneralAnalytics()
    fetchSegmentsSummary()
    
    // Connect WebSocket
    connectWebSocket()

    // Interval to calculate events-per-second rolling chart data
    const chartInterval = setInterval(() => {
      setRollingCounts(prev => {
        const next = [...prev.slice(1), activeEventsCountRef.current]
        activeEventsCountRef.current = 0 // Reset counter for the next interval
        return next
      })
    }, 1500)

    return () => {
      clearInterval(chartInterval)
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close()

    console.log("Connecting to WebSocket telemetry...")
    const ws = new WebSocket('ws://localhost:8000/ws/telemetry')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      activeEventsCountRef.current += 1

      // Add to event list (limit to 10)
      setEvents(prev => [data, ...prev.slice(0, 9)])
      
      // Update real-time incremental counts
      setTotalEvents(prev => prev + 1)
      if (data.event_type === 'purchase') {
        setPurchasesCount(prev => prev + 1)
        setTotalRevenue(prev => prev + (data.price || 0))
      }
    }

    ws.onclose = () => {
      console.log("WebSocket disconnected. Retrying in 3 seconds...")
      setTimeout(connectWebSocket, 3000)
    }

    ws.onerror = (err) => {
      console.error("WebSocket error observed:", err)
    }

    wsRef.current = ws
  }

  // REST calls to Simulator Status
  const fetchSimulatorStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/simulator/status')
      const data = await res.json()
      setIsSimulating(data.is_running)
      setDelaySeconds(data.delay_seconds)
      setSliderVal(data.delay_seconds)
    } catch (err) {
      console.error("Could not fetch simulator status:", err)
    }
  }

  const fetchGeneralAnalytics = async () => {
    try {
      const res = await fetch('http://localhost:8000/analytics')
      const data = await res.json()
      setTotalEvents(data.total_events || 0)
      setPurchasesCount(data.purchases || 0)
    } catch (err) {
      console.error("Could not fetch analytics totals:", err)
    }
  }

  const fetchSegmentsSummary = async () => {
    try {
      const res = await fetch('http://localhost:8000/top-segments')
      const data = await res.json()
      // format segment list to object: { 'Power User': count, etc }
      const summary = {}
      data.forEach(item => {
        summary[item._id] = item.count
      })
      setSegmentsSummary(summary)
    } catch (err) {
      console.error("Could not fetch segment aggregates:", err)
    }
  }

  // Handle simulator controls
  const handleStartStop = async () => {
    const endpoint = isSimulating ? 'stop' : 'start'
    try {
      const res = await fetch(`http://localhost:8000/simulator/${endpoint}`, { method: 'POST' })
      const data = await res.json()
      setIsSimulating(data.status === 'started')
    } catch (err) {
      console.error("Error executing simulator trigger:", err)
    }
  }

  const handleUpdateConfig = async () => {
    try {
      const res = await fetch('http://localhost:8000/simulator/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ delay_seconds: parseFloat(sliderVal) })
      })
      const data = await res.json()
      setDelaySeconds(data.delay_seconds)
    } catch (err) {
      console.error("Error updating config:", err)
    }
  }

  // Explainer Search handler (Day 10 goal setup)
  const handleSearchUser = async (e) => {
    e.preventDefault()
    setSearchError('')
    setRecommendationResult(null)
    
    if (!searchUserId.trim()) return

    try {
      const recsRes = await fetch(`http://localhost:8000/recommendations/${searchUserId}`)
      const recsData = await recsRes.json()
      
      const explainRes = await fetch(`http://localhost:8000/explain-recommendation/${searchUserId}`)
      const explainData = await explainRes.json()
      
      if (explainData.reason === 'No purchase history found') {
        setSearchError(`User ${searchUserId} has no telemetry history yet. Standard defaults served.`)
      }

      setRecommendationResult({
        recs: recsData.recommendations || [],
        explanation: explainData
      })
    } catch (err) {
      setSearchError('Error retrieving profiles from backend API.')
    }
  }

  // Model retraining trigger (Day 11 goal setup)
  const handleTriggerRetrain = async () => {
    setIsRetraining(true)
    try {
      const res = await fetch('http://localhost:8000/ml/retrain', { method: 'POST' })
      const data = await res.json()
      if (data.status === 'success') {
        fetchSegmentsSummary()
        alert(`Model retrained successfully. Clustered ${data.users_clustered} users!`)
      } else {
        alert(`Retraining skipped: ${data.message}`)
      }
    } catch (err) {
      console.error("Failed to retrain model:", err)
    } finally {
      setIsRetraining(false)
    }
  }

  // Calculate coordinates for SVG sparkline chart
  const getSvgPathPoints = () => {
    const width = 500
    const height = 150
    const pointsCount = rollingCounts.length
    const maxVal = Math.max(...rollingCounts, 3) // avoid division by zero
    
    const xStep = width / (pointsCount - 1)
    
    const points = rollingCounts.map((val, idx) => {
      const x = idx * xStep
      // Invert Y coordinate since SVG (0,0) is top-left
      const y = height - (val / maxVal) * (height - 20) - 10
      return `${x},${y}`
    })

    return {
      linePath: `M ${points.join(' L ')}`,
      areaPath: `M 0,${height} L ${points.join(' L ')} L ${width},${height} Z`
    }
  }

  const { linePath, areaPath } = getSvgPathPoints()

  return (
    <div className="app-container">
      {/* Sidebar Section */}
      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <Activity className="brand-icon" size={28} color="var(--accent-primary)" />
            <h2>Telemetry AI</h2>
          </div>

          <div className="simulator-panel">
            <div className="simulator-header">
              <span className="card-title">Event Ingest</span>
              <span className={`status-badge ${isSimulating ? 'active' : 'inactive'}`}>
                {isSimulating ? 'active' : 'offline'}
              </span>
            </div>
            
            <button className="primary" onClick={handleStartStop}>
              {isSimulating ? <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}><Square size={16} /> Stop simulator</span> : <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}><Play size={16} /> Start simulator</span>}
            </button>

            <div className="slider-group">
              <div className="slider-labels">
                <span>Speed Delay</span>
                <span>{sliderVal}s</span>
              </div>
              <input 
                type="range" 
                min="0.1" 
                max="5.0" 
                step="0.1" 
                value={sliderVal} 
                onChange={(e) => setSliderVal(e.target.value)} 
              />
              <button className="secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }} onClick={handleUpdateConfig}>
                <Settings size={16} /> Apply Interval
              </button>
            </div>
          </div>
        </div>

        <div className="sidebar-bottom">
          <button className="theme-switch" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
            {theme === 'light' ? <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Moon size={16} /> Dark Mode</span> : <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Sun size={16} /> Light Mode</span>}
          </button>
        </div>
      </aside>

      {/* Main Panel Section */}
      <main className="dashboard-main">
        <header className="dashboard-header">
          <h1>Telemetry Streaming Board</h1>
          <p style={{ color: 'var(--text-secondary)' }}>Observe Kafka broker activity, train user clusters on-demand, and fetch customer explainers.</p>
        </header>

        {/* Metrics Grid Cards */}
        <section className="metrics-grid">
          <div className="card">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Activity size={16} /> Stream Count</div>
            <div className="card-value">{totalEvents}</div>
          </div>
          <div className="card">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><ShoppingCart size={16} /> Total Purchases</div>
            <div className="card-value">{purchasesCount}</div>
          </div>
          <div className="card">
            <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><DollarSign size={16} /> Est. Revenue</div>
            <div className="card-value">${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</div>
          </div>
        </section>

        {/* Analytics Section Graph & Real-time Live Feed */}
        <section className="dashboard-grid">
          {/* Chart Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <h3 style={{ fontSize: '1.15rem' }}>Dynamic Events/Sec Stream</h3>
            <div className="chart-container">
              <svg className="chart-svg" viewBox="0 0 500 150" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="chart-gradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--accent-primary)" />
                    <stop offset="100%" stopColor="var(--accent-primary)" stopOpacity="0" />
                  </linearGradient>
                </defs>
                {/* Horizontal dash grids */}
                <line x1="0" y1="20" x2="500" y2="20" className="chart-grid-line" />
                <line x1="0" y1="75" x2="500" y2="75" className="chart-grid-line" />
                <line x1="0" y1="130" x2="500" y2="130" className="chart-grid-line" />
                {/* Area under the line */}
                <path d={areaPath} className="chart-area" />
                {/* Line Path */}
                <path d={linePath} className="chart-line" />
              </svg>
            </div>
          </div>

          {/* Activity Feed Card */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: '320px' }}>
            <h3 style={{ fontSize: '1.15rem' }}>Ingestion Feed</h3>
            <div className="feed-container">
              {events.length === 0 ? (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '2rem 0' }}>
                  No telemetry stream active. Start simulator to trigger flows.
                </div>
              ) : (
                events.map((e, idx) => (
                  <div className="feed-item" key={idx}>
                    <div className="feed-info">
                      <span className="feed-title">{e.product}</span>
                      <span className="feed-meta">User ID: {e.user_id} | ${e.price}</span>
                    </div>
                    <span className={`event-badge ${e.event_type}`}>
                      {e.event_type}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </section>

        {/* Dynamic Placeholders for Day 10 Search Explainer & Day 11 Retrain Panels */}
        <section className="dashboard-grid">
          {/* Day 10: Recommendation Explorer Placeholder */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem' }}>Explainer Recommendations</h3>
              <p style={{ font: '13px var(--font-sans)', color: 'var(--text-secondary)' }}>Identify user segments and view explaining reasons dynamically.</p>
            </div>
            
            <form onSubmit={handleSearchUser} style={{ display: 'flex', gap: '0.5rem' }}>
              <input 
                type="number" 
                placeholder="Enter User ID (e.g. 50)" 
                style={{ flex: 1, padding: '0.5rem 1rem', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', background: 'var(--bg-glass)', color: 'var(--text-primary)', outline: 'none' }}
                value={searchUserId}
                onChange={(e) => setSearchUserId(e.target.value)}
              />
              <button type="submit" className="primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><Search size={16} /> Search</button>
            </form>

            {searchError && (
              <p style={{ fontSize: '0.85rem', color: 'var(--status-inactive)' }}>{searchError}</p>
            )}

            {recommendationResult && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'var(--bg-primary)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <p style={{ fontSize: '0.9rem' }}>
                  <strong>Favorite Category:</strong> {recommendationResult.explanation.favorite_category || 'N/A'} (Purchases: {recommendationResult.explanation.purchase_count || 0})
                </p>
                <p style={{ fontSize: '0.9rem' }}>
                  <strong>Reason:</strong> {recommendationResult.explanation.reason}
                </p>
                <div style={{ marginTop: '0.5rem' }}>
                  <strong style={{ fontSize: '0.9rem' }}>Recommendations:</strong>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.25rem' }}>
                    {recommendationResult.recs.map((item, idx) => (
                      <span key={idx} style={{ background: 'var(--accent-glow)', color: 'var(--accent-primary)', fontSize: '0.8rem', padding: '0.25rem 0.5rem', borderRadius: '4px' }}>
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Day 11: ML Management & Segments summary */}
          <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.15rem' }}>K-Means Segments</h3>
              <button className="secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.8rem' }} onClick={handleTriggerRetrain} disabled={isRetraining}>
                <RefreshCw size={14} className={isRetraining ? 'spin' : ''} /> {isRetraining ? 'Retraining...' : 'Retrain'}
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {segmentsSummary ? (
                Object.entries(segmentsSummary).map(([segmentName, count], idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.9rem', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-color)' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{segmentName}</span>
                    <strong style={{ color: 'var(--text-primary)' }}>{count} profiles</strong>
                  </div>
                ))
              ) : (
                <div style={{ color: 'var(--text-secondary)', textAlign: 'center', padding: '1rem' }}>
                  No segment data loaded. Trigger model retraining.
                </div>
              )}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
