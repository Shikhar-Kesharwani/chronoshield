import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell } from 'lucide-react';

const AlertFeed = ({ anomalies }) => {
  // Sort descending to show newest alerts at the top
  const sortedAnomalies = [...anomalies].sort((a, b) => 
    new Date(b.ts).getTime() - new Date(a.ts).getTime()
  );

  return (
    <div className="alerts-container glass-panel">
      <div className="alerts-header">
        <Bell size={20} color="var(--accent-red)" />
        Active Alerts
      </div>
      
      {sortedAnomalies.length === 0 ? (
        <div className="empty-alerts">No anomalies detected recently.</div>
      ) : (
        <div className="alerts-list">
          <AnimatePresence>
            {sortedAnomalies.slice(0, 10).map((anomaly) => {
              const detectedBy = [];
              if (anomaly.z_anomaly) detectedBy.push('Z-Score');
              if (anomaly.if_anomaly) detectedBy.push('IForest');
              
              const severity = Math.max(anomaly.z_severity || 0, anomaly.if_severity || 0);

              return (
                <motion.div
                  key={anomaly.ts}
                  className="alert-item"
                  initial={{ opacity: 0, x: 50, scale: 0.95 }}
                  animate={{ opacity: 1, x: 0, scale: 1 }}
                  exit={{ opacity: 0, x: -50, scale: 0.9 }}
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                >
                  <div className="alert-item-header">
                    <span>{new Date(anomaly.ts).toLocaleTimeString()}</span>
                    <span style={{ color: 'var(--accent-cyan)' }}>CPU: {anomaly.value.toFixed(1)}%</span>
                  </div>
                  <div className="alert-item-body">
                    Detected by: {detectedBy.join(', ')}
                  </div>
                  {severity > 0 && (
                    <div className="alert-severity-bar">
                      <motion.div 
                        className="alert-severity-fill" 
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.min(severity * 100, 100)}%` }}
                        transition={{ duration: 1, delay: 0.2 }}
                      />
                    </div>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
};

export default AlertFeed;
