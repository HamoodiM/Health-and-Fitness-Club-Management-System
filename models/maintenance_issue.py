"""
MaintenanceIssue Entity Model
Maps to the MaintenanceIssue table in the database
"""

from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class MaintenanceIssue(Base):
    """
    MaintenanceIssue entity representing equipment maintenance issues.
    
    Relationships:
    - Many-to-One with Room
    - Many-to-One with AdminStaff
    """
    __tablename__ = 'MaintenanceIssue'
    
    # Primary Key
    IssueID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    RoomID = Column(Integer, ForeignKey('Room.RoomID', ondelete='CASCADE'), nullable=False)
    AdminID = Column(Integer, ForeignKey('AdminStaff.AdminID', ondelete='CASCADE'), nullable=False)
    
    # Attributes
    IssueDescription = Column(Text, nullable=False)
    EquipmentName = Column(String(100))  # Name of equipment if specific
    ReportedDate = Column(Date, nullable=False)
    Priority = Column(String(20))  # 'Low', 'Medium', 'High', 'Critical'
    Status = Column(String(20), default='Open')  # 'Open', 'In Progress', 'Resolved', 'Closed'
    AssignedRepairDate = Column(Date)
    ResolutionDate = Column(Date)
    ResolutionNotes = Column(Text)
    
    # Relationships
    room = relationship("Room", back_populates="maintenance_issues", lazy="joined")
    admin = relationship("AdminStaff", back_populates="maintenance_issues", lazy="joined")
    
    def __repr__(self):
        return f"<MaintenanceIssue(IssueID={self.IssueID}, RoomID={self.RoomID}, Status='{self.Status}', Priority='{self.Priority}')>"

