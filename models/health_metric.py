"""
HealthMetric Entity Model
Maps to the HealthMetric table in the database
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class HealthMetric(Base):
    """
    HealthMetric entity representing member health measurements.
    Historical tracking - records are never overwritten.
    
    Relationships:
    - Many-to-One with Member
    """
    __tablename__ = 'HealthMetric'
    
    # Primary Key
    HealthMetricID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    MemberID = Column(Integer, ForeignKey('Member.MemberID', ondelete='CASCADE'), nullable=False)
    
    # Attributes
    RecordedDate = Column(Date, nullable=False)
    Height = Column(Numeric(5, 2))
    Weight = Column(Numeric(5, 2))
    BodyFatPercentage = Column(Numeric(5, 2))
    RestingHeartRate = Column(Integer)
    Notes = Column(Text)
    
    # Relationships
    member = relationship("Member", back_populates="health_metrics", lazy="joined")
    
    def __repr__(self):
        return f"<HealthMetric(HealthMetricID={self.HealthMetricID}, MemberID={self.MemberID}, Date={self.RecordedDate})>"

