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

      <div className="form-group mb-20">
        <label>用药</label>
        <textarea 
          name="prescription"
          className="form-control" 
          placeholder="请输入用药方案..."
          value={data.prescription}
          onChange={handleChange}
        ></textarea>
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
