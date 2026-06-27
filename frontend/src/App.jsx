import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Activity, Clock } from 'lucide-react';
import { AnimatePresence } from 'framer-motion';

import LiveDashboard from './components/LiveDashboard';
import HistoricalView from './components/HistoricalView';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Header / Navbar */}
        <header className="app-header glass-panel">
          <div className="header-title">
            <Activity color="#00E5FF" />
            ChronoShield
          </div>
          
          <nav className="header-nav">
            <NavLink 
              to="/live" 
              className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
            >
              <Activity size={18} />
              Live Stream
            </NavLink>
            <NavLink 
              to="/history" 
              className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
            >
              <Clock size={18} />
              Historical Data
            </NavLink>
          </nav>
        </header>

        {/* Route Content */}
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Navigate to="/live" replace />} />
            <Route path="/live" element={<LiveDashboard />} />
            <Route path="/history" element={<HistoricalView />} />
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  );
}

export default App;
