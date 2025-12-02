"""
Member Entity Model
Maps to the Member table in the database
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base


class Member(Base):
    """
    Member entity representing gym members.
    
    Relationships:
    - One-to-Many with HealthMetric
    - One-to-Many with FitnessGoal
    - One-to-Many with PersonalTrainingSession
    - One-to-Many with Invoice (as payer)
    """
    __tablename__ = 'Member'
    
    # Primary Key
    MemberID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Attributes
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date)
    Gender = Column(String(1))
    Email = Column(String(100), unique=True, nullable=False)
    Phone = Column(String(20))
    Address = Column(String(200))
    JoinDate = Column(Date)
    MembershipStatus = Column(String(20))
    
    # Relationships (lazy loading by default)
    health_metrics = relationship(
        "HealthMetric", 
        back_populates="member", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    fitness_goals = relationship(
        "FitnessGoal", 
        back_populates="member", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    sessions = relationship(
        "PersonalTrainingSession", 
        back_populates="member", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    invoices = relationship(
        "Invoice", 
        back_populates="payer", 
        foreign_keys="Invoice.PayerID",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Member(MemberID={self.MemberID}, Name='{self.FirstName} {self.LastName}', Email='{self.Email}')>"

