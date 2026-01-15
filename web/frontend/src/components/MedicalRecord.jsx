import React from 'react';

const MedicalRecord = ({ data, onChange }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onChange({ ...data, [name]: value });
  };

  return (
    <div className="medical-record-section">
      <div className="section-title">诊疗记录</div>
      <div className="form-group mb-20">
        <label>主诉</label>
        <textarea
          name="complaint"
          className="form-control"
          placeholder="请输入患者主诉..."
          value={data.complaint}
          onChange={handleChange}
        ></textarea>
      </div>

      <div className="form-group mb-20" style={{ position: 'relative' }}>
        <label>用药</label>
        <textarea
          name="prescription"
          className="form-control"
          placeholder="请输入用药方案..."
          value={data.prescription}
          onChange={handleChange}
          style={{ paddingBottom: '40px' }}
        ></textarea>
        <div style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          display: 'flex',
          alignItems: 'center',
          gap: '5px',
          backgroundColor: 'rgba(255,255,255,0.9)',
          padding: '2px 5px',
          borderRadius: '4px'
        }}>
          <span style={{ fontSize: '0.8rem', color: '#666' }}>总计量:</span>
          <input
            type="text"
            name="totalDosage"
            value={data.totalDosage || '6付'}
            onChange={handleChange}
            style={{
              width: '60px',
              padding: '2px 5px',
              border: '1px solid #ccc',
              borderRadius: '4px',
              textAlign: 'center',
              fontSize: '0.9rem'
            }}
          />
        </div>
      </div>

      <div className="form-group">
        <label>体会/备注</label>
        <textarea
          name="note"
          className="form-control"
          placeholder="请输入诊疗体会或备注..."
          value={data.note}
          onChange={handleChange}
        ></textarea>
      </div>
    </div>
  );
};

export default MedicalRecord;
