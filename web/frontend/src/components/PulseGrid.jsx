import React from 'react';

const PulseGrid = ({ data, onChange, onSave }) => {
  const positions = [
    { label: '寸浮', id: 'cun-fu' },
    { label: '关浮', id: 'guan-fu' },
    { label: '尺浮', id: 'chi-fu' },
    { label: '寸中', id: 'cun-zhong' },
    { label: '关中', id: 'guan-zhong' },
    { label: '尺中', id: 'chi-zhong' },
    { label: '寸沉', id: 'cun-chen' },
    { label: '关沉', id: 'guan-chen' },
    { label: '尺沉', id: 'chi-chen' },
  ];

  const handleCellChange = (id, value) => {
    onChange({ ...data, [id]: value });
  };

  return (
    <div className="grid-wrapper">
      <div className="grid-title">脉象九宫格录入</div>
      
      <div className="overall-pulse-section" style={{ marginBottom: '15px' }}>
        <div style={{ marginBottom: '8px', fontSize: '0.9rem', color: 'var(--apple-text-secondary)', fontWeight: '500' }}>
          整体脉象
        </div>
        <textarea
          className="form-control"
          style={{ 
            minHeight: '60px', 
            resize: 'none',
            fontSize: '0.95rem',
            padding: '10px'
          }}
          placeholder="例如：脉整体偏窄，显寒夹气血虚弱，空2分"
          value={data.overall_description || ''}
          onChange={(e) => onChange({ ...data, overall_description: e.target.value })}
        />
      </div>

      <div className="pulse-grid">
        {positions.map((pos) => (
          <div key={pos.id} className="grid-input-cell">
            <div className="cell-label">{pos.label}</div>
            <textarea 
              className="cell-textarea" 
              placeholder="输入脉象"
              value={data[pos.id] || ''}
              onChange={(e) => handleCellChange(pos.id, e.target.value)}
            ></textarea>
          </div>
        ))}
      </div>
      <button className="btn-primary" onClick={onSave}>
        保存病历
      </button>
    </div>
  );
};

export default PulseGrid;
