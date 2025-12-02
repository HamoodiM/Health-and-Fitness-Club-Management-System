"""
Admin Staff Functions Implementation
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from models import Room, PersonalTrainingSession, MaintenanceIssue, AdminStaff, Invoice, Member
from typing import Optional, List


def assign_room_booking(
    db: Session,
    session_id: int,
    room_id: int
) -> PersonalTrainingSession:
    """
    3.3.1 Room Booking
    Assign rooms for sessions or classes. Prevent double-booking.
    """
    # Edge case: Validate IDs
    if not isinstance(session_id, int) or session_id <= 0:
        raise ValueError("Session ID must be a positive integer.")
    if not isinstance(room_id, int) or room_id <= 0:
        raise ValueError("Room ID must be a positive integer.")
    
    # Verify session exists
    session = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.SessionID == session_id
    ).first()
    
    if not session:
        raise ValueError(f"Session with ID {session_id} not found.")
    
    # Edge case: Check if session is in the past
    if session.SessionDate < date.today():
        raise ValueError("Cannot assign room to a past session.")
    
    # Verify room exists
    room = db.query(Room).filter(Room.RoomID == room_id).first()
    if not room:
        raise ValueError(f"Room with ID {room_id} not found.")
    
    # Edge case: Check if room is already assigned to this session
    if session.RoomID == room_id:
        raise ValueError(f"Room {room_id} is already assigned to this session.")
    
    # Edge case: Validate room capacity for group classes
    if session.SessionType == 'Group Class' and session.MaxCapacity:
        if room.RoomCapacity and session.MaxCapacity > room.RoomCapacity:
            raise ValueError(
                f"Session max capacity ({session.MaxCapacity}) exceeds room capacity ({room.RoomCapacity})."
            )
    
    # Check for room conflicts 
    conflicting_booking = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.RoomID == room_id,
        PersonalTrainingSession.SessionDate == session.SessionDate,
        PersonalTrainingSession.StartTime < session.EndTime,
        PersonalTrainingSession.EndTime > session.StartTime,
        PersonalTrainingSession.SessionID != session_id  # Exclude current session
    ).first()
    
    if conflicting_booking:
        raise ValueError(
            f"Room is already booked for session {conflicting_booking.SessionID} "
            f"at {conflicting_booking.StartTime} on {conflicting_booking.SessionDate}."
        )
    
    try:
        # Update session with room assignment 
        session.RoomID = room_id
        db.commit()
        db.refresh(session)
        
        return session
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to assign room: {str(e)}") from e


def log_maintenance_issue(
    db: Session,
    room_id: int,
    admin_id: int,
    issue_description: str,
    equipment_name: Optional[str] = None,
    priority: str = 'Medium',
    reported_date: Optional[date] = None
) -> MaintenanceIssue:
    """
    3.3.2 Equipment Maintenance - Log new issue
    Log issues, track repair status, associate with room/equipment.
    """
    # Edge case: Validate IDs
    if not isinstance(room_id, int) or room_id <= 0:
        raise ValueError("Room ID must be a positive integer.")
    if not isinstance(admin_id, int) or admin_id <= 0:
        raise ValueError("Admin ID must be a positive integer.")
    
    # Edge case: Validate issue_description
    if not issue_description or not issue_description.strip():
        raise ValueError("Issue description is required and cannot be empty.")
    if len(issue_description) > 1000:
        raise ValueError("Issue description cannot exceed 1000 characters.")
    
    # Edge case: Validate equipment_name
    if equipment_name and len(equipment_name) > 100:
        raise ValueError("Equipment name cannot exceed 100 characters.")
    
    # Edge case: Validate priority
    valid_priorities = ['Low', 'Medium', 'High', 'Critical']
    if priority not in valid_priorities:
        raise ValueError(f"Priority must be one of: {valid_priorities}")
    
    # Edge case: Validate reported_date
    if reported_date:
        if reported_date > date.today():
            raise ValueError("Reported date cannot be in the future.")
        if (date.today() - reported_date).days > 3650:  # 10 years
            raise ValueError("Reported date is too far in the past.")
    
    # Verify room exists
    room = db.query(Room).filter(Room.RoomID == room_id).first()
    if not room:
        raise ValueError(f"Room with ID {room_id} not found.")
    
    # Verify admin exists
    admin = db.query(AdminStaff).filter(AdminStaff.AdminID == admin_id).first()
    if not admin:
        raise ValueError(f"Admin staff with ID {admin_id} not found.")
    
    try:
        # Create new maintenance issue using ORM
        new_issue = MaintenanceIssue(
            RoomID=room_id,
            AdminID=admin_id,
            IssueDescription=issue_description.strip(),
            EquipmentName=equipment_name.strip() if equipment_name else None,
            ReportedDate=reported_date or date.today(),
            Priority=priority,
            Status='Open'
        )
        
        db.add(new_issue)
        db.commit()
        db.refresh(new_issue)
        
        return new_issue
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to log maintenance issue: {str(e)}") from e


def update_maintenance_status(
    db: Session,
    issue_id: int,
    status: Optional[str] = None,
    assigned_repair_date: Optional[date] = None,
    resolution_date: Optional[date] = None,
    resolution_notes: Optional[str] = None
) -> MaintenanceIssue:
    
    # Edge case: Validate issue_id
    if not isinstance(issue_id, int) or issue_id <= 0:
        raise ValueError("Issue ID must be a positive integer.")
    
    # Edge case: Check if at least one field is provided
    if all(field is None for field in [status, assigned_repair_date, resolution_date, resolution_notes]):
        raise ValueError("At least one field must be provided for update.")
    
    # Query issue using ORM
    issue = db.query(MaintenanceIssue).filter(MaintenanceIssue.IssueID == issue_id).first()
    
    if not issue:
        raise ValueError(f"Maintenance issue with ID {issue_id} not found.")
    
    # Edge case: Validate status
    valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    if status and status not in valid_statuses:
        raise ValueError(f"Status must be one of: {valid_statuses}")
    
    # Edge case: Validate status transitions
    if status:
        if issue.Status == 'Closed' and status != 'Closed':
            raise ValueError("Cannot change status of a closed issue.")
        if issue.Status == 'Resolved' and status not in ['Resolved', 'Closed']:
            raise ValueError("Resolved issues can only be closed.")
    
    # Edge case: Validate assigned_repair_date
    if assigned_repair_date:
        if assigned_repair_date < issue.ReportedDate:
            raise ValueError("Assigned repair date cannot be before reported date.")
        from datetime import timedelta
        if assigned_repair_date > date.today() + timedelta(weeks=52):  # 1 year
            raise ValueError("Assigned repair date cannot be more than 1 year in the future.")
    
    # Edge case: Validate resolution_date
    if resolution_date:
        if issue.Status not in ['Resolved', 'Closed']:
            raise ValueError("Cannot set resolution date unless status is 'Resolved' or 'Closed'.")
        if resolution_date < issue.ReportedDate:
            raise ValueError("Resolution date cannot be before reported date.")
        if resolution_date > date.today():
            raise ValueError("Resolution date cannot be in the future.")
        if assigned_repair_date and resolution_date < assigned_repair_date:
            raise ValueError("Resolution date cannot be before assigned repair date.")
    
    # Edge case: Validate resolution_notes
    if resolution_notes and len(resolution_notes) > 1000:
        raise ValueError("Resolution notes cannot exceed 1000 characters.")
    
    try:
        # Update fields using ORM
        if status:
            issue.Status = status
        if assigned_repair_date:
            issue.AssignedRepairDate = assigned_repair_date
        if resolution_date:
            issue.ResolutionDate = resolution_date
        if resolution_notes:
            issue.ResolutionNotes = resolution_notes.strip()
        
        db.commit()
        db.refresh(issue)
        
        return issue
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to update maintenance status: {str(e)}") from e


def create_invoice(
    db: Session,
    payer_id: int,
    invoice_number: str,
    invoice_date: date,
    due_date: date,
    amount: float,
    service_description: str,
    session_id: Optional[int] = None,
    payment_method: Optional[str] = None
) -> Invoice:
    
    # Edge case: Validate payer_id
    if not isinstance(payer_id, int) or payer_id <= 0:
        raise ValueError("Payer ID must be a positive integer.")
    
    # Edge case: Validate invoice_number
    if not invoice_number or not invoice_number.strip():
        raise ValueError("Invoice number is required and cannot be empty.")
    if len(invoice_number) > 50:
        raise ValueError("Invoice number cannot exceed 50 characters.")
    
    # Edge case: Validate service_description
    if not service_description or not service_description.strip():
        raise ValueError("Service description is required and cannot be empty.")
    if len(service_description) > 500:
        raise ValueError("Service description cannot exceed 500 characters.")
    
    # Edge case: Validate session_id
    if session_id is not None and (not isinstance(session_id, int) or session_id <= 0):
        raise ValueError("Session ID must be a positive integer if provided.")
    
    # Edge case: Validate dates
    if invoice_date > date.today():
        raise ValueError("Invoice date cannot be in the future.")
    if (date.today() - invoice_date).days > 3650:  # 10 years
        raise ValueError("Invoice date is too far in the past.")
    
    if due_date < invoice_date:
        raise ValueError("Due date cannot be before invoice date.")
    if (due_date - invoice_date).days > 365:  # 1 year
        raise ValueError("Due date cannot be more than 1 year after invoice date.")
    
    # Edge case: Validate amount
    if not isinstance(amount, (int, float)):
        raise ValueError("Amount must be a number.")
    if amount <= 0:
        raise ValueError("Invoice amount must be positive.")
    if amount > 1000000:  # $1M limit
        raise ValueError("Invoice amount exceeds maximum limit.")
    
    # Edge case: Validate payment_method
    if payment_method and len(payment_method) > 50:
        raise ValueError("Payment method cannot exceed 50 characters.")
    
    # Verify payer (member) exists
    payer = db.query(Member).filter(Member.MemberID == payer_id).first()
    if not payer:
        raise ValueError(f"Member with ID {payer_id} not found.")
    
    # Verify session exists if provided
    if session_id:
        session = db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.SessionID == session_id
        ).first()
        if not session:
            raise ValueError(f"Session with ID {session_id} not found.")
        
        # Edge case: Verify session belongs to payer
        if session.MemberID != payer_id:
            raise ValueError(f"Session {session_id} does not belong to member {payer_id}.")
    
    # Edge case: Check if invoice number already exists
    existing = db.query(Invoice).filter(Invoice.InvoiceNumber == invoice_number).first()
    if existing:
        raise ValueError(f"Invoice number '{invoice_number}' already exists.")
    
    try:
        # Create new invoice using ORM
        new_invoice = Invoice(
            InvoiceNumber=invoice_number.strip(),
            PayerID=payer_id,
            SessionID=session_id,
            InvoiceDate=invoice_date,
            DueDate=due_date,
            Amount=round(amount, 2),  # Round to 2 decimal places
            PaymentMethod=payment_method.strip() if payment_method else None,
            PaymentStatus='Pending',
            ServiceDescription=service_description.strip()
        )
        
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)
        return new_invoice
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Invoice number '{invoice_number}' already exists.") from e
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to create invoice: {str(e)}") from e


def record_payment(
    db: Session,
    invoice_id: int,
    payment_method: str,
    paid_date: Optional[date] = None
) -> Invoice:
    
    # Edge case: Validate invoice_id
    if not isinstance(invoice_id, int) or invoice_id <= 0:
        raise ValueError("Invoice ID must be a positive integer.")
    
    # Edge case: Validate payment_method
    if not payment_method or not payment_method.strip():
        raise ValueError("Payment method is required and cannot be empty.")
    if len(payment_method) > 50:
        raise ValueError("Payment method cannot exceed 50 characters.")
    
    # Edge case: Validate paid_date (basic check before querying)
    if paid_date and paid_date > date.today():
        raise ValueError("Paid date cannot be in the future.")
    
    # Query invoice using ORM
    invoice = db.query(Invoice).filter(Invoice.InvoiceID == invoice_id).first()
    
    if not invoice:
        raise ValueError(f"Invoice with ID {invoice_id} not found.")
    
    # Edge case: Check if already paid
    if invoice.PaymentStatus == 'Paid':
        raise ValueError(f"Invoice {invoice_id} is already marked as paid.")
    
    # Edge case: Validate paid_date against invoice date
    if paid_date and paid_date < invoice.InvoiceDate:
        raise ValueError("Paid date cannot be before invoice date.")
    
    try:
        # Update payment information using ORM
        invoice.PaymentStatus = 'Paid'
        invoice.PaymentMethod = payment_method.strip()
        invoice.PaidDate = paid_date or date.today()
        
        db.commit()
        db.refresh(invoice)
        
        return invoice
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to record payment: {str(e)}") from e

