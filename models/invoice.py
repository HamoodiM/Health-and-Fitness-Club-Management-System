"""
Invoice Entity Model
Maps to the Invoice table in the database
"""

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Invoice(Base):
    """
    Invoice entity representing billing and payment records.
    
    Relationships:
    - Many-to-One with Member (as payer)
    - Many-to-Zero-or-One with PersonalTrainingSession
    """
    __tablename__ = 'Invoice'
    
    # Primary Key
    InvoiceID = Column(Integer, primary_key=True, autoincrement=True)
    
    # Attributes
    InvoiceNumber = Column(String(20), unique=True, nullable=False)
    
    # Foreign Keys
    PayerID = Column(Integer, ForeignKey('Member.MemberID', ondelete='CASCADE'), nullable=False)
    SessionID = Column(Integer, ForeignKey('PersonalTrainingSession.SessionID', ondelete='SET NULL'))
    
    # Attributes
    InvoiceDate = Column(Date, nullable=False)
    DueDate = Column(Date, nullable=False)
    Amount = Column(Numeric(10, 2), nullable=False)
    PaymentMethod = Column(String(30))
    PaymentStatus = Column(String(20), default='Pending')
    ServiceDescription = Column(String(200))
    PaidDate = Column(Date)
    
    # Relationships
    payer = relationship("Member", back_populates="invoices", foreign_keys=[PayerID], lazy="joined")
    session = relationship("PersonalTrainingSession", back_populates="invoices", lazy="joined")
    
    def __repr__(self):
        return f"<Invoice(InvoiceID={self.InvoiceID}, Number='{self.InvoiceNumber}', Amount={self.Amount}, Status='{self.PaymentStatus}')>"

