from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    pinyin = Column(String, index=True, nullable=True) # Added pinyin for search
    phone = Column(String, index=True, nullable=True) # Added phone number
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    
    # JSONB Flesh for extensible patient details (e.g., lifestyle, family history)
    info = Column(JSON, nullable=True, server_default='{}')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    records = relationship("MedicalRecord", back_populates="patient")

class Practitioner(Base):
    __tablename__ = "practitioners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False, default="teacher") # 'doctor' or 'teacher'
    created_at = Column(DateTime, default=datetime.now)

    records = relationship("MedicalRecord", back_populates="practitioner")

class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    practitioner_id = Column(Integer, ForeignKey("practitioners.id"), nullable=True) # Link to doctor/teacher
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
    data = Column(JSON, nullable=False, server_default='{}')
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    patient = relationship("Patient", back_populates="records")
    practitioner = relationship("Practitioner", back_populates="records")

