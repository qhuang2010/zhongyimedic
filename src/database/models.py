from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    phone = Column(String, index=True, nullable=True) # Added phone number
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    
    # JSONB Flesh for extensible patient details (e.g., lifestyle, family history)
    info = Column(JSONB, nullable=True, server_default='{}')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    records = relationship("MedicalRecord", back_populates="patient")

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    visit_date = Column(DateTime, default=datetime.now, index=True)
    
    # Relational Skeleton for common queries
    complaint = Column(Text, nullable=True) # 主诉
    diagnosis = Column(Text, nullable=True) # 诊断 (could be extracted later)
    
    # JSONB Flesh for the core data
    # Contains:
    # - pulse_grid: { 'cun_fu': '...', ... } (The 9-grid data)
    # - prescription: Text (or structured)
    # - note: Text
    # - raw_input: Full frontend payload for AI training
    data = Column(JSONB, nullable=False, server_default='{}')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    patient = relationship("Patient", back_populates="records")

    # Index on JSONB data for faster querying inside the JSON document
    __table_args__ = (
        Index('ix_medical_records_data_gin', data, postgresql_using='gin'),
    )
