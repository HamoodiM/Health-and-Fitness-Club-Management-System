"""
AdminStaff Entity Model
Maps to the AdminStaff table in the database
"""

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from database import Base


class AdminStaff(Base):
    """
    AdminStaff entity representing administrative staff.
    
    Relationships:
    - One-to-Many with MaintenanceIssue
    """
    __tablename__ = 'AdminStaff'
    
    # Primary Key
    AdminID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Attributes
    FirstName = Column(String(50), nullable=False)
    LastName = Column(String(50), nullable=False)
    DateOfBirth = Column(Date)
    Gender = Column(String(1))
    Email = Column(String(100), unique=True, nullable=False)
    Phone = Column(String(20))
    Role = Column(String(50))
    HireDate = Column(Date)
    
    # Relationships
    maintenance_issues = relationship(
        "MaintenanceIssue", 
        back_populates="admin", 
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<AdminStaff(AdminID={self.AdminID}, Name='{self.FirstName} {self.LastName}', Role='{self.Role}')>"

