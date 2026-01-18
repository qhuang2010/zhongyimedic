import React from 'react';

const ConfirmModal = ({ isOpen, title, message, onConfirm, onCancel }) => {
    if (!isOpen) return null;

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10000
            }}
            onClick={onCancel}
        >
            <div
                style={{
                    backgroundColor: '#fff',
                    borderRadius: '14px',
                    padding: '24px',
                    maxWidth: '320px',
                    width: '90%',
                    boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
                    textAlign: 'center'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                <h3 style={{
                    margin: '0 0 12px 0',
                    color: '#1d1d1f',
                    fontSize: '18px',
                    fontWeight: '600'
                }}>
                    {title || '确认操作'}
                </h3>
                <p style={{
                    margin: '0 0 24px 0',
                    color: '#666',
                    fontSize: '14px',
                    lineHeight: '1.5'
                }}>
                    {message}
                </p>
                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                    <button
                        type="button"
                        onClick={onCancel}
                        style={{
                            flex: 1,
                            padding: '12px 24px',
                            borderRadius: '8px',
                            border: '1px solid #d2d2d7',
                            backgroundColor: '#fff',
                            color: '#1d1d1f',
                            fontSize: '14px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            transition: 'background-color 0.2s'
                        }}
                    >
                        取消
                    </button>
                    <button
                        type="button"
                        onClick={onConfirm}
                        style={{
                            flex: 1,
                            padding: '12px 24px',
                            borderRadius: '8px',
                            border: 'none',
                            backgroundColor: '#ff3b30',
                            color: '#fff',
                            fontSize: '14px',
                            fontWeight: '500',
                            cursor: 'pointer',
                            transition: 'background-color 0.2s'
                        }}
                    >
                        确定删除
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ConfirmModal;
