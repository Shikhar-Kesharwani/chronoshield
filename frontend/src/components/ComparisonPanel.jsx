import React from 'react';
import { motion } from 'framer-motion';
import { BarChart2 } from 'lucide-react';

const StatBar = ({ label, value }) => {
  const percentage = Math.min(Math.max(value * 100, 0), 100);
  
  return (
    <div className="model-stat">
      <div className="model-stat-header">
        <span className="model-name">{label}</span>
        <span className="model-score">{percentage.toFixed(1)}%</span>
      </div>
      <div className="progress-bg">
        <motion.div 
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ type: "spring", stiffness: 100, damping: 20 }}
        />
      </div>
    </div>
  );
};

const ComparisonPanel = ({ stats }) => {
  return (
    <div className="comparison-container glass-panel">
      <div className="alerts-header">
        <BarChart2 size={20} color="var(--accent-purple)" />
        Model Performance
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '0.5rem' }}>
        <div>
          <h4 style={{ color: 'var(--text-muted)', marginBottom: '10px', fontSize: '0.85rem', textTransform: 'uppercase' }}>Rolling Z-Score</h4>
          <StatBar label="Precision (True Positives)" value={stats.zscore.precision} />
          <div style={{ height: '10px' }} />
          <StatBar label="Recall (Caught vs Missed)" value={stats.zscore.recall} />
        </div>
        
        <div>
          <h4 style={{ color: 'var(--text-muted)', marginBottom: '10px', fontSize: '0.85rem', textTransform: 'uppercase' }}>Isolation Forest (ML)</h4>
          <StatBar label="Precision (True Positives)" value={stats.iforest.precision} />
          <div style={{ height: '10px' }} />
          <StatBar label="Recall (Caught vs Missed)" value={stats.iforest.recall} />
        </div>
      </div>
    </div>
  );
};

export default ComparisonPanel;
