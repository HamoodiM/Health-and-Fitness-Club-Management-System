"""
PersonalTrainingSession Entity Model
Maps to the PersonalTrainingSession table in the database
Handles both Personal Training sessions and Group Classes via SessionType
"""

from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class PersonalTrainingSession(Base):
    """
    PersonalTrainingSession entity representing training sessions.
    Can be either 'Personal Training' or 'Group Class' based on SessionType.
    
    Relationships:
    - Many-to-One with Trainer
    - Many-to-One with Member
    - Many-to-One with Room
    - One-to-Zero-or-One with Invoice
    """
    __tablename__ = 'PersonalTrainingSession'
    
    # Primary Key
    SessionID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    TrainerID = Column(Integer, ForeignKey('Trainer.TrainerID', ondelete='CASCADE'), nullable=False)
    MemberID = Column(Integer, ForeignKey('Member.MemberID', ondelete='CASCADE'), nullable=False)
    RoomID = Column(Integer, ForeignKey('Room.RoomID', ondelete='SET NULL'))
    
    # Attributes
    SessionDate = Column(Date, nullable=False)
    StartTime = Column(Time, nullable=False)
    EndTime = Column(Time, nullable=False)
    DurationMinutes = Column(Integer)
    SessionType = Column(String(50))  # 'Personal Training' or 'Group Class'
    MaxCapacity = Column(Integer)  # NULL for PT, set for group classes
    CurrentEnrollment = Column(Integer, default=0)  # for group classes
    Notes = Column(Text)
    
    # Relationships
    trainer = relationship("Trainer", back_populates="sessions", lazy="joined")
    member = relationship("Member", back_populates="sessions", lazy="joined")
    room = relationship("Room", back_populates="sessions", lazy="joined")
    invoices = relationship("Invoice", back_populates="session", lazy="select")
    
    def __repr__(self):
        return f"<PersonalTrainingSession(SessionID={self.SessionID}, Type='{self.SessionType}', Date={self.SessionDate})>"

