import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Search } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Scatter
} from 'recharts';

function HistoricalView() {
  const [metric, setMetric] = useState('cpu');
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(1000);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/metrics?metric=${metric}&limit=${limit}`);
      const json = await res.json();
      
      const formatted = json.data.map(d => ({
        ...d,
        timeLabel: new Date(d.ts).toLocaleTimeString(),
        // Normalise anomalies for the chart
        z_score_anomaly: d.is_anomaly_zscore ? d.value : null,
        iforest_anomaly: d.is_anomaly_iforest ? d.value : null
      }));
      setData(formatted.reverse()); // older to newer
    } catch (err) {
      console.error("Failed to fetch historical data", err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchHistory();
  }, [metric]);

  return (
    <motion.div 
      className="dashboard-content historical-view"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="dashboard-controls glass-panel" style={{ marginBottom: "20px" }}>
        <div className="controls-left">
          <label className="metric-select-label">Historical Data: </label>
          <select 
            className="metric-select" 
            value={metric} 
            onChange={(e) => setMetric(e.target.value)}
          >
            <option value="cpu">CPU Usage</option>
            <option value="memory">Memory Usage</option>
            <option value="latency">Network Latency</option>
          </select>
          
          <label className="metric-select-label" style={{marginLeft: "20px"}}>Data Points: </label>
          <select 
            className="metric-select" 
            value={limit} 
            onChange={(e) => setLimit(parseInt(e.target.value))}
          >
            <option value={500}>Last 500</option>
            <option value={1000}>Last 1000</option>
            <option value={2000}>Last 2000</option>
          </select>
        </div>
        
        <div className="controls-right">
          <button className="btn-primary" onClick={fetchHistory} disabled={loading}>
            <Search size={16} style={{marginRight: "8px"}} />
            {loading ? "Loading..." : "Search"}
          </button>
        </div>
      </div>

      <div className="chart-section glass-panel" style={{ height: "600px", padding: "20px" }}>
        <h2>{metric.toUpperCase()} History</h2>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
            <defs>
              <linearGradient id="colorValueHistory" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00E5FF" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2E3C" vertical={false} />
            <XAxis dataKey="timeLabel" stroke="#6B7280" minTickGap={50} />
            <YAxis stroke="#6B7280" />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: '1px solid #1E293B', borderRadius: '8px' }}
              itemStyle={{ color: '#E2E8F0' }}
            />
            
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#00E5FF" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorValueHistory)" 
              isAnimationActive={false}
            />
            <Scatter name="Z-Score Anomaly" dataKey="z_score_anomaly" fill="#FF0055" />
            <Scatter name="iForest Anomaly" dataKey="iforest_anomaly" fill="#9D4EDD" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}

export default HistoricalView;
