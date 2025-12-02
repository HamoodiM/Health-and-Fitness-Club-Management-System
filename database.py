"""
Database Configuration and Setup
Handles database connection, session management, and table creation
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database configuration - global variables
DB_CONFIG = { 
    'host': 'localhost',
    'port': 5432,
    'database': 'gymdb',
    'username': 'postgres',
    'password': 'postgres'
}

# Construct database URL
DATABASE_URL = f"postgresql://{DB_CONFIG['username']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use with FastAPI or similar frameworks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all tables in the database.
    This is equivalent to running DDL.sql - the ORM generates the SQL.
    """
    # Import all models to ensure they're registered with Base
    from models import (
        Member, Trainer, AdminStaff, Room,
        PersonalTrainingSession, HealthMetric, FitnessGoal,
        Invoice, MaintenanceIssue
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("[OK] All tables created successfully!")
    
    # Create advanced features (views, triggers, indexes)
    try:
        from database_advanced import setup_advanced_features
        setup_advanced_features()
    except Exception as e:
        print(f"Note: Advanced features setup: {e}")


def drop_tables():
    """
    Drop all tables from the database.
    Use with caution!
    """
    # Drop views first (they depend on tables)
    try:
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("DROP VIEW IF EXISTS MemberDashboardView CASCADE"))
            conn.execute(text("DROP VIEW IF EXISTS TrainerScheduleView CASCADE"))
            conn.commit()
    except Exception:
        pass  # Views may not exist
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)
    print("[OK] All tables dropped!")


def init_db():
    """
    Initialize database: create tables and optionally seed with sample data.
    This replaces DDL.sql and DML.sql when using ORM.
    """
    # Create tables
    create_tables()
    
    # Optionally seed with sample data
    # seed_database()


if __name__ == "__main__":
    # Run this file directly to create tables
    print("Creating database tables...")
    init_db()

