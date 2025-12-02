"""
Member Functions Implementation
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime
from models import Member, HealthMetric, FitnessGoal, PersonalTrainingSession, Trainer, Room
from typing import Optional, List


def register_member(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
    date_of_birth: Optional[date] = None,
    gender: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    membership_status: str = 'Active'
) -> Member:
    """
    User Registration
    Create a new member with unique email and basic profile info.
    
    Returns: Created Member object
    Raises: ValueError for validation errors, IntegrityError if email already exists
    """
    # Edge case: Validate required fields
    if not first_name or not first_name.strip():
        raise ValueError("First name is required and cannot be empty.")
    if not last_name or not last_name.strip():
        raise ValueError("Last name is required and cannot be empty.")
    if not email or not email.strip():
        raise ValueError("Email is required and cannot be empty.")
    
    # Edge case: Validate email format (basic check)
    if '@' not in email or '.' not in email.split('@')[-1]:
        raise ValueError("Invalid email format.")
    
    # Edge case: Validate name length
    if len(first_name) > 50:
        raise ValueError("First name cannot exceed 50 characters.")
    if len(last_name) > 50:
        raise ValueError("Last name cannot exceed 50 characters.")
    if len(email) > 100:
        raise ValueError("Email cannot exceed 100 characters.")
    
    # Edge case: Validate date of birth (not in future, reasonable age)
    if date_of_birth:
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        age = (date.today() - date_of_birth).days // 365
        if age > 120:
            raise ValueError("Invalid date of birth (age exceeds reasonable limit).")
        if age < 13:
            raise ValueError("Member must be at least 13 years old.")
    
    # Edge case: Validate gender
    if gender and gender.upper() not in ['M', 'F', 'O', '']:
        raise ValueError("Gender must be 'M', 'F', 'O', or empty.")
    
    # Edge case: Validate membership status
    valid_statuses = ['Active', 'Inactive', 'Suspended', 'Cancelled']
    if membership_status not in valid_statuses:
        raise ValueError(f"Membership status must be one of: {valid_statuses}")
    
    # Edge case: Check if email already exists (before attempting insert)
    existing = db.query(Member).filter(Member.Email == email).first()
    if existing:
        raise ValueError(f"Email '{email}' already exists. Registration failed.")
    
    try:
        # Create new member using ORM
        new_member = Member(
            FirstName=first_name.strip(),
            LastName=last_name.strip(),
            Email=email.strip().lower(),
            DateOfBirth=date_of_birth,
            Gender=gender.upper() if gender else None,
            Phone=phone.strip() if phone else None,
            Address=address.strip() if address else None,
            JoinDate=date.today(),
            MembershipStatus=membership_status
        )
        
        # Add to session and commit
        db.add(new_member)
        db.commit()
        db.refresh(new_member)
        
        return new_member
    
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Email '{email}' already exists. Registration failed.") from e
    except Exception as e:
        db.rollback()
        raise ValueError(f"Registration failed: {str(e)}") from e


def update_profile(
    db: Session,
    member_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    date_of_birth: Optional[date] = None,
    gender: Optional[str] = None
) -> Member:
    """
    Profile Management - Update personal details
    Update member's personal information.
    """
    # Edge case: Validate member_id
    if not isinstance(member_id, int) or member_id <= 0:
        raise ValueError("Member ID must be a positive integer.")
    
    # Edge case: Check if at least one field is provided
    if all(field is None for field in [first_name, last_name, phone, address, date_of_birth, gender]):
        raise ValueError("At least one field must be provided for update.")
    
    # Query member using ORM
    member = db.query(Member).filter(Member.MemberID == member_id).first()
    
    if not member:
        raise ValueError(f"Member with ID {member_id} not found.")
    
    # Update fields if provided with validation
    if first_name is not None:
        if not first_name.strip():
            raise ValueError("First name cannot be empty.")
        if len(first_name) > 50:
            raise ValueError("First name cannot exceed 50 characters.")
        member.FirstName = first_name.strip()
    
    if last_name is not None:
        if not last_name.strip():
            raise ValueError("Last name cannot be empty.")
        if len(last_name) > 50:
            raise ValueError("Last name cannot exceed 50 characters.")
        member.LastName = last_name.strip()
    
    if phone is not None:
        if phone and len(phone) > 20:
            raise ValueError("Phone number cannot exceed 20 characters.")
        member.Phone = phone.strip() if phone else None
    
    if address is not None:
        if address and len(address) > 200:
            raise ValueError("Address cannot exceed 200 characters.")
        member.Address = address.strip() if address else None
    
    if date_of_birth is not None:
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        age = (date.today() - date_of_birth).days // 365
        if age > 120 or age < 13:
            raise ValueError("Invalid date of birth.")
        member.DateOfBirth = date_of_birth
    
    if gender is not None:
        if gender and gender.upper() not in ['M', 'F', 'O', '']:
            raise ValueError("Gender must be 'M', 'F', 'O', or empty.")
        member.Gender = gender.upper() if gender else None
    
    try:
        db.commit()
        db.refresh(member)
        return member
    except Exception as e:
        db.rollback()
        raise ValueError(f"Profile update failed: {str(e)}") from e


def add_fitness_goal(
    db: Session,
    member_id: int,
    goal_type: str,
    target_body_weight: Optional[float] = None,
    target_body_fat: Optional[float] = None,
    target_date: Optional[date] = None,
    goal_status: str = 'Active',
    notes: Optional[str] = None
) -> FitnessGoal:
    """
    Profile Management - Add fitness goal
    Create a new fitness goal for a member.
    """
    # Edge case: Validate member_id
    if not isinstance(member_id, int) or member_id <= 0:
        raise ValueError("Member ID must be a positive integer.")
    
    # Edge case: Validate goal_type
    if not goal_type or not goal_type.strip():
        raise ValueError("Goal type is required and cannot be empty.")
    if len(goal_type) > 50:
        raise ValueError("Goal type cannot exceed 50 characters.")
    
    # Edge case: Validate target values
    if target_body_weight is not None:
        if target_body_weight <= 0:
            raise ValueError("Target body weight must be positive.")
        if target_body_weight > 1000:
            raise ValueError("Target body weight exceeds reasonable limit.")
    
    if target_body_fat is not None:
        if target_body_fat < 0 or target_body_fat > 100:
            raise ValueError("Target body fat percentage must be between 0 and 100.")
    
    # Edge case: Validate target_date
    if target_date:
        if target_date < date.today():
            raise ValueError("Target date cannot be in the past.")
        if (target_date - date.today()).days > 3650:  # 10 years
            raise ValueError("Target date is too far in the future.")
    
    # Edge case: Validate goal_status
    valid_statuses = ['Active', 'Completed', 'Cancelled', 'On Hold']
    if goal_status not in valid_statuses:
        raise ValueError(f"Goal status must be one of: {valid_statuses}")
    
    # Verify member exists
    member = db.query(Member).filter(Member.MemberID == member_id).first()
    if not member:
        raise ValueError(f"Member with ID {member_id} not found.")
    
    # Edge case: Check if at least one target is set
    if target_body_weight is None and target_body_fat is None:
        raise ValueError("At least one target (body weight or body fat percentage) must be specified.")
    
    try:
        # Create new goal using ORM
        new_goal = FitnessGoal(
            MemberID=member_id,
            GoalType=goal_type.strip(),
            TargetBodyWeight=target_body_weight,
            TargetBodyFatPercentage=target_body_fat,
            SetDate=date.today(),
            TargetDate=target_date,
            GoalStatus=goal_status,
            Notes=notes.strip() if notes else None
        )
        
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)
        
        return new_goal
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to add fitness goal: {str(e)}") from e


def log_health_metric(
    db: Session,
    member_id: int,
    recorded_date: date,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    body_fat_percentage: Optional[float] = None,
    resting_heart_rate: Optional[int] = None,
    notes: Optional[str] = None
) -> HealthMetric:
    """
    3.1.3 Health History
    Log multiple metric entries; do not overwrite. Must support time-stamped entries.
    Historical tracking - never UPDATE, only INSERT.
    """
    # Edge case: Validate member_id
    if not isinstance(member_id, int) or member_id <= 0:
        raise ValueError("Member ID must be a positive integer.")
    
    # Edge case: Validate recorded_date
    if recorded_date > date.today():
        raise ValueError("Recorded date cannot be in the future.")
    if (date.today() - recorded_date).days > 36500:  # 100 years
        raise ValueError("Recorded date is too far in the past.")
    
    # Edge case: Validate at least one metric is provided
    if all(metric is None for metric in [height, weight, body_fat_percentage, resting_heart_rate]):
        raise ValueError("At least one health metric (height, weight, body fat, or heart rate) must be provided.")
    
    # Edge case: Validate metric values
    if height is not None:
        if height <= 0:
            raise ValueError("Height must be positive.")
        if height > 300:  # cm (about 10 feet)
            raise ValueError("Height exceeds reasonable limit.")
    
    if weight is not None:
        if weight <= 0:
            raise ValueError("Weight must be positive.")
        if weight > 1000:  # kg (about 2200 lbs)
            raise ValueError("Weight exceeds reasonable limit.")
    
    if body_fat_percentage is not None:
        if body_fat_percentage < 0 or body_fat_percentage > 100:
            raise ValueError("Body fat percentage must be between 0 and 100.")
    
    if resting_heart_rate is not None:
        if resting_heart_rate <= 0:
            raise ValueError("Resting heart rate must be positive.")
        if resting_heart_rate < 30 or resting_heart_rate > 200:
            raise ValueError("Resting heart rate must be between 30 and 200 bpm.")
    
    # Verify member exists
    member = db.query(Member).filter(Member.MemberID == member_id).first()
    if not member:
        raise ValueError(f"Member with ID {member_id} not found.")
    
    try:
        # Create new health metric using ORM (never UPDATE to preserve history)
        new_metric = HealthMetric(
            MemberID=member_id,
            RecordedDate=recorded_date,
            Height=height,
            Weight=weight,
            BodyFatPercentage=body_fat_percentage,
            RestingHeartRate=resting_heart_rate,
            Notes=notes.strip() if notes else None
        )
        
        db.add(new_metric)
        db.commit()
        db.refresh(new_metric)
        
        return new_metric
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to log health metric: {str(e)}") from e


def schedule_pt_session(
    db: Session,
    member_id: int,
    trainer_id: int,
    session_date: date,
    start_time: datetime.time,
    end_time: datetime.time,
    room_id: Optional[int] = None,
    session_type: str = 'Personal Training',
    duration_minutes: Optional[int] = None,
    max_capacity: Optional[int] = None,
    notes: Optional[str] = None
) -> PersonalTrainingSession:
    """
    PT Session Scheduling
    Book or reschedule training with a trainer, validating availability and room conflicts.
    """
    # Edge case: Validate IDs
    if not isinstance(member_id, int) or member_id <= 0:
        raise ValueError("Member ID must be a positive integer.")
    if not isinstance(trainer_id, int) or trainer_id <= 0:
        raise ValueError("Trainer ID must be a positive integer.")
    if room_id is not None and (not isinstance(room_id, int) or room_id <= 0):
        raise ValueError("Room ID must be a positive integer if provided.")
    
    # Edge case: Validate session_date
    if session_date < date.today():
        raise ValueError("Session date cannot be in the past.")
    if (session_date - date.today()).days > 365:
        raise ValueError("Session date cannot be more than 1 year in the future.")
    
    # Edge case: Validate time range
    if start_time >= end_time:
        raise ValueError("Start time must be before end time.")
    
    # Edge case: Validate session duration (reasonable limits)
    time_diff = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
    duration_mins = time_diff.total_seconds() / 60
    if duration_mins < 15:
        raise ValueError("Session duration must be at least 15 minutes.")
    if duration_mins > 480:  # 8 hours
        raise ValueError("Session duration cannot exceed 8 hours.")
    
    # Edge case: Validate session_type
    valid_types = ['Personal Training', 'Group Class']
    if session_type not in valid_types:
        raise ValueError(f"Session type must be one of: {valid_types}")
    
    # Edge case: Validate max_capacity for group classes
    if session_type == 'Group Class':
        if max_capacity is None or max_capacity <= 0:
            raise ValueError("Group classes must have a positive max capacity.")
        if max_capacity > 100:
            raise ValueError("Max capacity cannot exceed 100.")
    
    # Verify entities exist
    member = db.query(Member).filter(Member.MemberID == member_id).first()
    if not member:
        raise ValueError(f"Member with ID {member_id} not found.")
    
    trainer = db.query(Trainer).filter(Trainer.TrainerID == trainer_id).first()
    if not trainer:
        raise ValueError(f"Trainer with ID {trainer_id} not found.")
    
    if room_id:
        room = db.query(Room).filter(Room.RoomID == room_id).first()
        if not room:
            raise ValueError(f"Room with ID {room_id} not found.")
        
        # Edge case: Validate room capacity for group classes
        if session_type == 'Group Class' and max_capacity and room.RoomCapacity:
            if max_capacity > room.RoomCapacity:
                raise ValueError(f"Max capacity ({max_capacity}) exceeds room capacity ({room.RoomCapacity}).")
    
    # Check for trainer availability conflicts (using ORM query)
    conflicting_sessions = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.TrainerID == trainer_id,
        PersonalTrainingSession.SessionDate == session_date,
        PersonalTrainingSession.StartTime < end_time,
        PersonalTrainingSession.EndTime > start_time
    ).first()
    
    if conflicting_sessions:
        raise ValueError(
            f"Trainer has a conflicting session (ID: {conflicting_sessions.SessionID}) "
            f"from {conflicting_sessions.StartTime} to {conflicting_sessions.EndTime}."
        )
    
    # Check for room conflicts if room is specified
    if room_id:
        conflicting_room = db.query(PersonalTrainingSession).filter(
            PersonalTrainingSession.RoomID == room_id,
            PersonalTrainingSession.SessionDate == session_date,
            PersonalTrainingSession.StartTime < end_time,
            PersonalTrainingSession.EndTime > start_time
        ).first()
        
        if conflicting_room:
            raise ValueError(
                f"Room is already booked for session {conflicting_room.SessionID} "
                f"from {conflicting_room.StartTime} to {conflicting_room.EndTime}."
            )
    
    # Edge case: Check if member already has a session at this time
    member_conflict = db.query(PersonalTrainingSession).filter(
        PersonalTrainingSession.MemberID == member_id,
        PersonalTrainingSession.SessionDate == session_date,
        PersonalTrainingSession.StartTime < end_time,
        PersonalTrainingSession.EndTime > start_time
    ).first()
    
    if member_conflict:
        raise ValueError(
            f"Member already has a session scheduled at this time "
            f"(Session ID: {member_conflict.SessionID})."
        )
    
    try:
        # Calculate duration if not provided
        if duration_minutes is None:
            time_diff = datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)
            duration_minutes = int(time_diff.total_seconds() / 60)
        
        # Create new session using ORM
        new_session = PersonalTrainingSession(
            MemberID=member_id,
            TrainerID=trainer_id,
            RoomID=room_id,
            SessionDate=session_date,
            StartTime=start_time,
            EndTime=end_time,
            DurationMinutes=duration_minutes,
            SessionType=session_type,
            MaxCapacity=max_capacity,
            CurrentEnrollment=0,
            Notes=notes.strip() if notes else None
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return new_session
    except Exception as e:
        db.rollback()
        raise ValueError(f"Failed to schedule session: {str(e)}") from e

