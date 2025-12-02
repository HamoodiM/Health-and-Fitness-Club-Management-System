"""
FitnessGoal Entity Model
Maps to the FitnessGoal table in the database
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class FitnessGoal(Base):
    """
    FitnessGoal entity representing member fitness goals.
    Allows multiple goals over time for the same member.
    
    Relationships:
    - Many-to-One with Member
    """
    __tablename__ = 'FitnessGoal'
    
    # Primary Key
    GoalID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    MemberID = Column(Integer, ForeignKey('Member.MemberID', ondelete='CASCADE'), nullable=False)
    
    # Attributes
    GoalType = Column(String(50))
    TargetBodyWeight = Column(Numeric(5, 2))
    TargetBodyFatPercentage = Column(Numeric(5, 2))
    SetDate = Column(Date)
    TargetDate = Column(Date)
    GoalStatus = Column(String(20))
    Notes = Column(Text)
    
    # Relationships
    member = relationship("Member", back_populates="fitness_goals", lazy="joined")
    
    def __repr__(self):
        return f"<FitnessGoal(GoalID={self.GoalID}, MemberID={self.MemberID}, Type='{self.GoalType}')>"

