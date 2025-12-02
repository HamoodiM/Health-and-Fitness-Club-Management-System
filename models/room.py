"""
Room Entity Model
Maps to the Room table in the database
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Room(Base):
    """
    Room entity representing gym rooms/facilities.
    
    Relationships:
    - One-to-Many with PersonalTrainingSession
    - One-to-Many with MaintenanceIssue
    """
    __tablename__ = 'Room'
    
    # Primary Key
    RoomID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Attributes
    RoomNumber = Column(String(10), unique=True, nullable=False)
    RoomCapacity = Column(Integer)
    RoomType = Column(String(50))
    AccessPermissions = Column(String(100))
    
    # Relationships
    sessions = relationship(
        "PersonalTrainingSession", 
        back_populates="room",
        lazy="select"
    )
    maintenance_issues = relationship(
        "MaintenanceIssue", 
        back_populates="room", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Room(RoomID={self.RoomID}, RoomNumber='{self.RoomNumber}', Capacity={self.RoomCapacity})>"

