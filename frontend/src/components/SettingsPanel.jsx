import React, { useState } from 'react';
import { X, Save } from 'lucide-react';
import { motion } from 'framer-motion';

const SettingsPanel = ({ onClose }) => {
  const [zscoreThreshold, setZscoreThreshold] = useState(3.0);
  const [iforestContamination, setIforestContamination] = useState(0.05);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          zscore_threshold: parseFloat(zscoreThreshold),
          iforest_contamination: parseFloat(iforestContamination)
        })
      });
      onClose();
    } catch (err) {
      console.error("Failed to update config", err);
    }
    setSaving(false);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <motion.div 
        className="modal-content glass-panel"
        onClick={e => e.stopPropagation()}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
      >
        <div className="modal-header">
          <h3>Detector Settings</h3>
          <button className="btn-icon" onClick={onClose}><X size={20} /></button>
        </div>
        
        <div className="modal-body">
          <div className="setting-group">
            <label>
              Z-Score Threshold: <span>{zscoreThreshold}</span>
            </label>
            <input 
              type="range" 
              min="1.0" 
              max="5.0" 
              step="0.1" 
              value={zscoreThreshold} 
              onChange={e => setZscoreThreshold(e.target.value)} 
            />
            <small>Higher = Less sensitive to spikes</small>
          </div>

          <div className="setting-group">
            <label>
              IForest Contamination: <span>{iforestContamination}</span>
            </label>
            <input 
              type="range" 
              min="0.01" 
              max="0.20" 
              step="0.01" 
              value={iforestContamination} 
              onChange={e => setIforestContamination(e.target.value)} 
            />
            <small>Expected percentage of anomalies in the dataset</small>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={16} style={{marginRight: "8px"}} />
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default SettingsPanel;
