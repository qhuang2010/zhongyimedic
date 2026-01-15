import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import Base
from src.database.models import Practitioner, MedicalRecord

# Setup DB connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate():
    print("Starting migration...")
    db = SessionLocal()
    
    # 1. Create 'practitioners' table
    # We use engine to create tables that don't exist
    Base.metadata.create_all(bind=engine)
    print("Checked/Created 'practitioners' table.")
    
    # 2. Add 'practitioner_id' to 'medical_records' if missing
    # SQLite ALTER TABLE is limited, so we check first
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(medical_records)"))
            columns = [row[1] for row in result.fetchall()]
            if "practitioner_id" not in columns:
                print("Adding 'practitioner_id' column to 'medical_records'...")
                conn.execute(text("ALTER TABLE medical_records ADD COLUMN practitioner_id INTEGER REFERENCES practitioners(id)"))
                conn.commit()
            else:
                print("'practitioner_id' column already exists.")
    except Exception as e:
        print(f"Error modifying table: {e}")
        
    # 3. Seed Data
    teachers = ["王春", "舒建平", "周静", "张小珊", "王定详"]
    
    # Seed Doctor (Self)
    doctor = db.query(Practitioner).filter(Practitioner.role == "doctor").first()
    if not doctor:
        doctor = Practitioner(name="主治医师", role="doctor")
        db.add(doctor)
        print("Seeded Doctor: 主治医师")
        
    # Seed Teachers
    for name in teachers:
        p = db.query(Practitioner).filter(Practitioner.name == name, Practitioner.role == "teacher").first()
        if not p:
            p = Practitioner(name=name, role="teacher")
            db.add(p)
            print(f"Seeded Teacher: {name}")
            
    db.commit()
    db.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
