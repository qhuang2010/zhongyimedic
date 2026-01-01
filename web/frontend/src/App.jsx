import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import PatientInfo from './components/PatientInfo';
import MedicalRecord from './components/MedicalRecord';
import PulseGrid from './components/PulseGrid';
import AIAnalysis from './components/AIAnalysis';

function App() {
  // Centralized State Management
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    age: '',
    gender: '男',
    phone: ''
  });

  const [medicalRecord, setMedicalRecord] = useState({
    complaint: '',
    prescription: '',
    note: ''
  });

  const [pulseGrid, setPulseGrid] = useState({});
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleLoadPatient = async (patientId) => {
    try {
      const response = await fetch(`/api/patients/${patientId}/latest_record`);
      if (response.ok) {
        const data = await response.json();
        
        // Update state with loaded data
        setPatientInfo(data.patient_info || {
          name: '',
          age: '',
          gender: '',
          phone: ''
        });
        
        setMedicalRecord(data.medical_record || {
          complaint: '',
          prescription: '',
          note: ''
        });
        
        setPulseGrid(data.pulse_grid || {});
        setAnalysisResult(null); // Reset analysis when loading new patient
      } else {
        alert('加载患者信息失败');
      }
    } catch (err) {
      console.error('Error loading patient:', err);
      alert('加载患者信息出错');
    }
  };

  const handleLoadRecord = async (recordId) => {
    try {
      const response = await fetch(`/api/records/${recordId}`);
      if (response.ok) {
        const data = await response.json();
        
        setMedicalRecord(data.medical_record || {
          complaint: '',
          prescription: '',
          note: ''
        });
        
        setPulseGrid(data.pulse_grid || {});
        setAnalysisResult(null); // Reset analysis when loading new record
      } else {
        alert('加载病历失败');
      }
    } catch (err) {
      console.error('Error loading record:', err);
      alert('加载病历出错');
    }
  };

  const handleSave = async () => {
    const payload = {
      patient_info: patientInfo,
      medical_record: medicalRecord,
      pulse_grid: pulseGrid
    };

    try {
      const response = await fetch('/api/records/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const result = await response.json();
        alert('保存成功！Record ID: ' + result.record_id);
      } else {
        const error = await response.json();
        alert('保存失败: ' + error.detail);
      }
    } catch (err) {
      alert('保存出错: ' + err.message);
    }
  };

  const handleAnalyze = async () => {
    const payload = {
      medical_record: medicalRecord,
      pulse_grid: pulseGrid
    };

    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const result = await response.json();
      setAnalysisResult(result);
    } else {
      throw new Error('Analysis failed');
    }
  };

  return (
    <div className="app-container">
      <div className="header">
        <h1>中医脉象九宫格病历录入系统</h1>
        <div>
          <span style={{ fontSize: '0.9em', opacity: 0.8 }}>DeepSeek-OCR Powered</span>
        </div>
      </div>

      <div className="main-layout">
        <Sidebar 
          onPatientSelect={handleLoadPatient} 
          onRecordSelect={handleLoadRecord}
        />
        
        <div className="content-area">
          <div className="left-panel">
            <PatientInfo data={patientInfo} onChange={setPatientInfo} />
            <MedicalRecord data={medicalRecord} onChange={setMedicalRecord} />
            <AIAnalysis data={analysisResult} onAnalyze={handleAnalyze} />
          </div>

          <div className="right-panel">
            <PulseGrid 
              data={pulseGrid} 
              onChange={setPulseGrid} 
              onSave={handleSave} 
            />
          </div>
        </div>
      </div>
      
      <div className="footer">
          <p>&copy; 2024 中医脉象九宫格病历录入系统 | DeepSeek-OCR Powered</p>
      </div>
    </div>
  );
}

export default App;
