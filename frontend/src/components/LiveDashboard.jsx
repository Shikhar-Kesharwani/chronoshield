import React, { useState } from 'react';
import { Activity, AlertTriangle, ShieldCheck, Target, Zap, Settings } from 'lucide-react';
import { motion } from 'framer-motion';
import { useMetricStream } from '../hooks/useMetricStream';
import LiveChart from './LiveChart';
import AlertFeed from './AlertFeed';
import ComparisonPanel from './ComparisonPanel';
import SettingsPanel from './SettingsPanel';

const KPICard = ({ title, value, icon: Icon, className = "" }) => (
  <motion.div 
    className="glass-panel kpi-card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="kpi-label">{title}</div>
    <motion.div 
      className={`kpi-value ${className}`}
      key={value}
      initial={{ scale: 1.1, opacity: 0.8 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      {value}
    </motion.div>
    <Icon size={48} className="kpi-icon" />
  </motion.div>
);

function LiveDashboard() {
  const [metric, setMetric] = useState("cpu");
  const { points: data, anomalies, connected: isConnected, stats } = useMetricStream(metric);
  const [injecting, setInjecting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Manual anomaly injection
  const injectAnomaly = async () => {
    setInjecting(true);
    try {
      await fetch('/api/inject', { method: 'POST' });
    } catch (err) {
      console.error("Failed to inject anomaly", err);
    }
    setTimeout(() => setInjecting(false), 1000);
  };

  // Safe access checks
  const currentVal = data && data.length > 0 ? data[data.length - 1].value.toFixed(1) : "0.0";
  const recentAnomalies = anomalies ? anomalies.filter(a => (Date.now() - new Date(a.ts).getTime()) < 60000).length : 0;
  
  // Safe stats
  const defaultStats = { precision: 0, recall: 0 };
  const safeStats = stats || { zscore: defaultStats, iforest: defaultStats };

  return (
    <div className="dashboard-content">
      {/* Header Controls */}
      <div className="dashboard-controls glass-panel">
        <div className="controls-left">
          <label className="metric-select-label">Select Metric: </label>
          <select 
            className="metric-select" 
            value={metric} 
            onChange={(e) => setMetric(e.target.value)}
          >
            <option value="cpu">CPU Usage</option>
            <option value="memory">Memory Usage</option>
            <option value="latency">Network Latency</option>
          </select>
        </div>
        
        <div className="controls-right">
          <div className="live-indicator">
            {isConnected ? (
              <>
                <div className="pulse-dot"></div>
                Live Stream Active
              </>
            ) : (
              <span style={{ color: "var(--accent-red)" }}>Connecting...</span>
            )}
          </div>

          <button 
            className="btn-icon"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            <Settings size={18} />
          </button>
          
          <button 
            className="btn-inject"
            onClick={injectAnomaly}
            disabled={injecting || !isConnected}
          >
            <Zap size={18} />
            {injecting ? "INJECTING..." : "INJECT ANOMALY"}
          </button>
        </div>
      </div>

      {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}

      {/* KPI Grid */}
      <div className="kpi-grid">
        <KPICard title={`Current ${metric.toUpperCase()}`} value={currentVal} icon={Activity} />
        <KPICard title="Recent Anomalies" value={recentAnomalies} icon={AlertTriangle} className={recentAnomalies > 0 ? "anomalies" : ""} />
        <KPICard title="Z-Score Precision" value={`${(safeStats.zscore.precision * 100).toFixed(1)}%`} icon={Target} className="precision" />
        <KPICard title="iForest Precision" value={`${(safeStats.iforest.precision * 100).toFixed(1)}%`} icon={ShieldCheck} className="precision" />
      </div>

      {/* Main Dashboard */}
      <div className="dashboard-grid">
        <motion.section 
          className="chart-section glass-panel"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="chart-header">
            <h2>Live Metric Stream ({metric})</h2>
            <div className="legend">
              <div className="legend-item"><div className="legend-dot normal"></div> Data</div>
              <div className="legend-item"><div className="legend-dot zscore"></div> Z-Score Band</div>
              <div className="legend-item"><div className="legend-dot anomaly"></div> Detected Anomaly</div>
            </div>
          </div>
          <LiveChart data={data} />
        </motion.section>

        <motion.aside 
          className="sidebar"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <ComparisonPanel stats={safeStats} />
          <AlertFeed anomalies={anomalies || []} />
        </motion.aside>
      </div>
    </div>
  );
}

export default LiveDashboard;
