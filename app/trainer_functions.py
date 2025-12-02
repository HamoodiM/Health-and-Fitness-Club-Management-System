"""
Trainer Functions Implementation
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import date, datetime
from models import Trainer, PersonalTrainingSession, Member, FitnessGoal, HealthMetric
from typing import List, Optional


def set_availability(
    db: Session,
    trainer_id: int,
    session_date: date,
    start_time: datetime.time,
    end_time: datetime.time
) -> dict:
    """
    Set Availability.
    Define time windows when available for sessions or classes. Prevent overlap.
    Returns availability validation result.
    """
    # Edge case: Validate trainer_id
    if not isinstance(trainer_id, int) or trainer_id <= 0:
        raise ValueError("Trainer ID must be a positive integer.")
    
    # Edge case: Validate session_date
    if session_date < date.today():
        raise ValueError("Availability date cannot be in the past.")
    if (session_date - date.today()).days > 365:
        raise ValueError("Availability date cannot be more than 1 year in the future.")
    
    # Edge case: Validate time range
    if start_time >= end_time:
        raise ValueError("Start time must be before end time.")
    
    # Edge case: Validate duration (reasonable limits)
    time_diff = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
    duration_mins = time_diff.total_seconds() / 60
    if duration_mins < 15:
        raise ValueError("Availability slot must be at least 15 minutes.")
    if duration_mins > 1440:  # 24 hours
        raise ValueError("Availability slot cannot exceed 24 hours.")
    
    # Verify trainer exists
    trainer = db.query(Trainer).filter(Trainer.TrainerID == trainer_id).first()
    if not trainer:
        raise ValueError(f"Trainer with ID {trainer_id} not found.")
    
    # Check for overlapping sessions using ORM query
    overlapping = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.TrainerID == trainer_id,
        PersonalTrainingSession.SessionDate == session_date,
        PersonalTrainingSession.StartTime < end_time,
        PersonalTrainingSession.EndTime > start_time
    ).first()
    
    if overlapping:
        raise ValueError(
            f"Time slot conflicts with existing session (ID: {overlapping.SessionID}): "
            f"{overlapping.StartTime} - {overlapping.EndTime}"
        )
    
    # Return confirmation that availability slot is valid
    return {
        "message": "Availability slot validated",
        "trainer_id": trainer_id,
        "date": session_date,
        "time": f"{start_time} - {end_time}",
        "available": True
    }


def view_schedule(
    db: Session,
    trainer_id: int,
    from_date: Optional[date] = None
) -> List[PersonalTrainingSession]:
    """
    Schedule View
    See assigned PT sessions and classes.
    """
    # Edge case: Validate trainer_id
    if not isinstance(trainer_id, int) or trainer_id <= 0:
        raise ValueError("Trainer ID must be a positive integer.")
    
    # Edge case: Validate from_date if provided
    if from_date and from_date < date(1900, 1, 1):
        raise ValueError("Date cannot be before 1900.")
    if from_date and (from_date - date.today()).days > 3650:
        raise ValueError("Date cannot be more than 10 years in the future.")
    
    # Verify trainer exists
    trainer = db.query(Trainer).filter(Trainer.TrainerID == trainer_id).first()
    if not trainer:
        raise ValueError(f"Trainer with ID {trainer_id} not found.")
    
    # Query sessions using ORM with eager loading
    query = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.TrainerID == trainer_id
    )
    
    if from_date:
        query = query.filter(PersonalTrainingSession.SessionDate >= from_date)
    else:
        query = query.filter(PersonalTrainingSession.SessionDate >= date.today())
    
    # Use joined loading to avoid N+1 queries
    sessions = query.order_by(
        PersonalTrainingSession.SessionDate,
        PersonalTrainingSession.StartTime
    ).all()
    
    return sessions


def lookup_member(
    db: Session,
    search_term: str
) -> List[dict]:
    """
    Member Lookup
    Search by name (case-insensitive) and view current goal and last metric. No editing rights.
    Supports searching by first name, last name, or full name.
    """
    # Edge case: Validate search_term
    if not search_term or not search_term.strip():
        raise ValueError("Search term cannot be empty.")
    
    # Edge case: Validate search term length
    if len(search_term) > 100:
        raise ValueError("Search term cannot exceed 100 characters.")
    
    # Edge case: Prevent SQL injection-like patterns (basic sanitization)
    # Allow % and _ for LIKE patterns, but sanitize other dangerous chars
    search_term_clean = search_term.strip()
    search_term_clean = search_term_clean.replace(';', '').replace('--', '').replace('/*', '').replace('*/', '')
    
    # Case-insensitive search using ORM
    search_pattern = f"%{search_term_clean}%"
    
    # Split search term to check if it's a full name (e.g., "John Doe")
    search_parts = search_term_clean.split()
    
    if len(search_parts) >= 2:
        # Full name search: match "FirstName LastName" or "LastName FirstName"
        first_part = f"%{search_parts[0]}%"
        last_part = f"%{search_parts[-1]}%"
        members = db.query(Member).filter(
            or_(
                # Match first name with first part and last name with last part
                and_(
                    Member.FirstName.ilike(first_part),
                    Member.LastName.ilike(last_part)
                ),
                # Match last name with first part and first name with last part (reversed)
                and_(
                    Member.LastName.ilike(first_part),
                    Member.FirstName.ilike(last_part)
                ),
                # Also match if either name contains the full search term
                Member.FirstName.ilike(search_pattern),
                Member.LastName.ilike(search_pattern),
                # Match concatenated full name
                (Member.FirstName + ' ' + Member.LastName).ilike(search_pattern)
            )
        ).limit(100).all()
    else:
        # Single word search: match first name or last name
        members = db.query(Member).filter(
            or_(
                Member.FirstName.ilike(search_pattern),
                Member.LastName.ilike(search_pattern)
            )
        ).limit(100).all()
    
    if not members:
        return []
    
    # Build result with latest goal and metric
    results = []
    for member in members:
        # Get latest fitness goal using ORM
        latest_goal = db.query(FitnessGoal).filter(
            FitnessGoal.MemberID == member.MemberID
        ).order_by(FitnessGoal.SetDate.desc()).first()
        
        # Get latest health metric using ORM
        latest_metric = db.query(HealthMetric).filter(
            HealthMetric.MemberID == member.MemberID
        ).order_by(HealthMetric.RecordedDate.desc()).first()
        
        results.append({
            'member': member,
            'latest_goal': latest_goal,
            'latest_metric': latest_metric
        })
    
    return results

