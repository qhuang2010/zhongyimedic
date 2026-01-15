import React, { useState, useEffect } from 'react';

const Sidebar = ({ onPatientSelect, onRecordSelect, lastUpdateTime }) => {
  const [query, setQuery] = useState('');
  const [historyUsers, setHistoryUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [patientHistory, setPatientHistory] = useState([]);

  // Date filter state
  const [selectedDate, setSelectedDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });

  // Fetch patients by date
  const fetchByDate = React.useCallback(async () => {
    if (!selectedDate) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/patients/by_date?date=${selectedDate}`);
      if (response.ok) {
        const data = await response.json();
        setHistoryUsers(data);
      }
    } catch (error) {
      console.error('Fetch by date failed:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedDate]);

  // Initial load & Date change effect
  useEffect(() => {
    if (!query.trim()) {
      fetchByDate();
    }
  }, [fetchByDate, lastUpdateTime]); // Reload when date changes or parent notifies update

  // Search effect
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (query.trim()) {
        handleSearch();
      } else {
        // If query cleared, fallback to date filter
        fetchByDate();
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [query, fetchByDate]);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch(`/api/patients/search?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setHistoryUsers(data);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePatientClick = async (patientId) => {
    setSelectedPatientId(patientId);
    onPatientSelect(patientId);

    // Fetch visit history
    try {
      const response = await fetch(`/api/patients/${patientId}/history`);
      if (response.ok) {
        const data = await response.json();
        setPatientHistory(data);
      }
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

  return (
    <div className="sidebar">
      <h3 className="sidebar-title">历史患者</h3>

      <div className="date-filter" style={{ marginBottom: '15px' }}>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
          style={{
            width: '100%',
            padding: '8px',
            borderRadius: '8px',
            border: '1px solid #d2d2d7',
            fontFamily: 'inherit',
            color: '#1d1d1f'
          }}
        />
      </div>

      <div className="sidebar-search-box">
        <input
          type="text"
          placeholder="搜索姓名或电话"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="sidebar-search-input"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="sidebar-search-btn"
        >
          {loading ? '...' : '搜'}
        </button>
      </div>

      <ul className="history-list">
        {historyUsers.length > 0 ? (
          historyUsers.map((user) => (
            <React.Fragment key={user.id}>
              <li
                className={`history-item ${selectedPatientId === user.id ? 'active' : ''}`}
                onClick={() => handlePatientClick(user.id)}
              >
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span className="user-name">{user.name}</span>
                  <span className="user-phone" style={{ fontSize: '0.8em', opacity: 0.8 }}>{user.phone}</span>
                </div>
                <span className="user-date">{user.last_visit}</span>
              </li>

              {selectedPatientId === user.id && patientHistory.length > 0 && (
                <ul className="visit-history">
                  {patientHistory.map(record => (
                    <li
                      key={record.id}
                      onClick={() => onRecordSelect(record.id)}
                      className="visit-item"
                    >
                      <div style={{ fontWeight: '500' }}>{record.visit_date}</div>
                      <div style={{
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        maxWidth: '180px',
                        fontSize: '0.8em',
                        opacity: 0.8
                      }}>
                        {record.complaint || '无主诉'}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </React.Fragment>
          ))
        ) : (
          <li style={{ color: '#999', textAlign: 'center', padding: '10px', fontSize: '0.9em' }}>
            {query ? '无匹配结果' : '该日期无就诊记录'}
          </li>
        )}
      </ul>
    </div>
  );
};

export default Sidebar;
