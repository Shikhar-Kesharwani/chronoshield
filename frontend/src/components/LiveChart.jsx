import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

// Custom glowing dot for anomalies
const CustomizedDot = (props) => {
  const { cx, cy, payload } = props;
  
  if (payload.z_anomaly || payload.if_anomaly || payload.injected) {
    const isCaught = payload.z_anomaly || payload.if_anomaly;
    const color = isCaught ? 'var(--accent-red)' : 'var(--accent-purple)';
    const glow = isCaught ? 'var(--accent-red-glow)' : 'rgba(157, 78, 221, 0.4)';
    
    return (
      <g>
        <circle cx={cx} cy={cy} r={12} fill={glow} opacity={0.6} />
        <circle cx={cx} cy={cy} r={6} fill={color} />
        <circle cx={cx} cy={cy} r={3} fill="#fff" />
      </g>
    );
  }
  return null;
};

// Custom Glassmorphic Tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const timeStr = new Date(data.ts).toLocaleTimeString();
    
    const isAnomaly = data.z_anomaly || data.if_anomaly;
    const detectedBy = [];
    if (data.z_anomaly) detectedBy.push('Z-Score');
    if (data.if_anomaly) detectedBy.push('IForest');

    return (
      <div className="custom-tooltip">
        <div className="tooltip-time">{timeStr}</div>
        <div className="tooltip-row">
          <span className="tooltip-label">CPU Usage:</span>
          <span className="tooltip-val value">{data.value.toFixed(2)}%</span>
        </div>
        
        {data.z_upper != null && (
          <div className="tooltip-row" style={{ fontSize: '0.8rem' }}>
            <span className="tooltip-label">Z-Band:</span>
            <span style={{ color: 'var(--text-muted)' }}>
              [{data.z_lower.toFixed(1)} - {data.z_upper.toFixed(1)}]
            </span>
          </div>
        )}
        
        {data.injected && (
          <div className="tooltip-row">
            <span className="tooltip-label">Status:</span>
            <span className="tooltip-val anomaly" style={{ color: 'var(--accent-purple)'}}>
              INJECTED SPIKE
            </span>
          </div>
        )}

        {isAnomaly && (
          <div className="tooltip-row">
            <span className="tooltip-label">Detection:</span>
            <span className="tooltip-val anomaly">
              CAUGHT ({detectedBy.join(', ')})
            </span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

const LiveChart = ({ data }) => {
  return (
    <div style={{ width: '100%', height: '100%', minHeight: 400, flex: 1 }}>
      <ResponsiveContainer>
        <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorZScore" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ffffff" stopOpacity={0.05}/>
              <stop offset="95%" stopColor="#ffffff" stopOpacity={0.0}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
          
          <XAxis 
            dataKey="ts" 
            tickFormatter={(tick) => new Date(tick).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })} 
            stroke="var(--text-muted)"
            fontSize={12}
            tickMargin={10}
            minTickGap={30}
          />
          <YAxis 
            domain={['auto', 'auto']} 
            stroke="var(--text-muted)"
            fontSize={12}
          />
          
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.1)', strokeWidth: 1 }} />
          
          {/* Z-Score Band Area */}
          <Area 
            type="monotone" 
            dataKey="z_upper" 
            stroke="none" 
            fill="url(#colorZScore)" 
            isAnimationActive={false}
          />
          <Area 
            type="monotone" 
            dataKey="z_lower" 
            stroke="none" 
            fill="#06080F" // Hide area under lower bound
            isAnimationActive={false}
          />

          {/* Main CPU Line with Area */}
          <Area 
            type="monotone" 
            dataKey="value" 
            stroke="var(--accent-cyan)"
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorValue)" 
            isAnimationActive={false}
            dot={<CustomizedDot />}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LiveChart;
