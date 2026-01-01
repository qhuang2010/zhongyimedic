from sqlalchemy import create_engine, text
import os

# Database connection URL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/tcm_pulse_db"
)

def upgrade_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name='patients' AND column_name='phone'"
            ))
            if result.rowcount == 0:
                print("Adding 'phone' column to 'patients' table...")
                connection.execute(text("ALTER TABLE patients ADD COLUMN phone VARCHAR"))
                connection.execute(text("CREATE INDEX idx_patients_phone ON patients(phone)"))
                connection.commit()
                print("Column added successfully.")
            else:
                print("'phone' column already exists.")
        except Exception as e:
            print(f"Error updating database: {e}")

if __name__ == "__main__":
    upgrade_db()
