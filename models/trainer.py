"""
Trainer Entity Model
Maps to the Trainer table in the database
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base


class Trainer(Base):
    """
    Trainer entity representing fitness trainers.
    
    Relationships:
    - One-to-Many with PersonalTrainingSession
    """
    __tablename__ = 'Trainer'
    
    # Primary Key
    TrainerID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Attributes
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date)
    Gender = Column(String(1))
    Email = Column(String(100), unique=True, nullable=False)
    Phone = Column(String(20))
    Specialty = Column(String(100))
    HireDate = Column(Date)
    
    # Relationships
    sessions = relationship(
        "PersonalTrainingSession", 
        back_populates="trainer", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Trainer(TrainerID={self.TrainerID}, Name='{self.FirstName} {self.LastName}', Specialty='{self.Specialty}')>"

