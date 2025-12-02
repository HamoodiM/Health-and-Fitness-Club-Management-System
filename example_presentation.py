"""
Example Presentation Script
Demonstrates all implemented operations with success and failure cases.
This script walks through every feature as required for the demo video.
"""

from datetime import date, time, timedelta
from database import SessionLocal, init_db, drop_tables
from app.member_functions import (
    register_member, update_profile, add_fitness_goal,
    log_health_metric, schedule_pt_session
)
from app.trainer_functions import set_availability, view_schedule, lookup_member
from app.admin_functions import (
    assign_room_booking, log_maintenance_issue, update_maintenance_status,
    create_invoice, record_payment
)
from models import Member, Trainer, AdminStaff, Room, PersonalTrainingSession


def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_operation(role, operation_name, description):
    """Print operation header"""
    print(f"\n[{role}] {operation_name}")
    print(f"Description: {description}")


def demo_member_registration(db):
    """Demonstrate User Registration"""
    print_operation(
        "MEMBER",
        "1. User Registration",
        "Create a new member with unique email and basic profile info"
    )
    
    # Success case
    print("\n--- SUCCESS CASE ---")
    member = None
    try:
        member = register_member(
            db,
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            date_of_birth=date(1995, 6, 15),
            gender="F",
            phone="555-1234",
            address="123 Fitness St"
        )
        print(f"[OK] Successfully registered member:")
        print(f"  Member ID: {member.MemberID}")
        print(f"  Name: {member.FirstName} {member.LastName}")
        print(f"  Email: {member.Email}")
        print(f"  Status: {member.MembershipStatus}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case
    print("\n--- FAILURE CASE: Duplicate Email ---")
    try:
        register_member(
            db,
            first_name="Bob",
            last_name="Smith",
            email="alice.johnson@example.com"  # Duplicate email
        )
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected duplicate email: {e}")
    
    return member


def demo_profile_management(db, member_id):
    """Demonstrate Profile Management"""
    print_operation(
        "MEMBER",
        "2. Profile Management",
        "Update personal details and add fitness goals"
    )
    
    # Success case: Update profile
    print("\n--- SUCCESS CASE: Update Profile ---")
    try:
        updated = update_profile(
            db,
            member_id,
            phone="555-5678",
            address="456 Health Ave"
        )
        print(f"[OK] Profile updated successfully:")
        print(f"  Phone: {updated.Phone}")
        print(f"  Address: {updated.Address}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Success case: Add fitness goal
    print("\n--- SUCCESS CASE: Add Fitness Goal ---")
    try:
        goal = add_fitness_goal(
            db,
            member_id,
            goal_type="Weight Loss",
            target_body_weight=150.0,
            target_body_fat=18.0,
            target_date=date.today() + timedelta(days=90)
        )
        print(f"[OK] Fitness goal added:")
        print(f"  Goal Type: {goal.GoalType}")
        print(f"  Target Weight: {goal.TargetBodyWeight} lbs")
        print(f"  Target Date: {goal.TargetDate}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Invalid target weight
    print("\n--- FAILURE CASE: Negative Target Weight ---")
    try:
        add_fitness_goal(
            db,
            member_id,
            goal_type="Weight Loss",
            target_body_weight=-10.0  # Invalid negative weight
        )
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected invalid weight: {e}")


def demo_health_history(db, member_id):
    """Demonstrate Health History Logging"""
    print_operation(
        "MEMBER",
        "3. Health History",
        "Log health metrics with time-stamped entries (never overwrite)"
    )
    
    # Success case
    print("\n--- SUCCESS CASE: Log Health Metric ---")
    try:
        metric1 = log_health_metric(
            db,
            member_id,
            recorded_date=date.today() - timedelta(days=30),
            weight=165.0,
            height=65.0,
            body_fat_percentage=22.0,
            resting_heart_rate=72
        )
        print(f"[OK] Health metric logged:")
        print(f"  Date: {metric1.RecordedDate}")
        print(f"  Weight: {metric1.Weight} lbs")
        print(f"  Body Fat: {metric1.BodyFatPercentage}%")
        
        # Log another metric (historical tracking)
        metric2 = log_health_metric(
            db,
            member_id,
            recorded_date=date.today(),
            weight=162.0,  # Weight loss tracked
            body_fat_percentage=20.5
        )
        print(f"\n[OK] Second metric logged (historical tracking):")
        print(f"  Date: {metric2.RecordedDate}")
        print(f"  Weight: {metric2.Weight} lbs")
        print(f"  Note: Previous entry preserved - no overwrite")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Future date
    print("\n--- FAILURE CASE: Future Recorded Date ---")
    try:
        log_health_metric(
            db,
            member_id,
            recorded_date=date.today() + timedelta(days=1),  # Future date
            weight=160.0
        )
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected future date: {e}")


def demo_pt_scheduling(db, member_id):
    """Demonstrate PT Session Scheduling"""
    print_operation(
        "MEMBER",
        "4. PT Session Scheduling",
        "Book training session with trainer, validating availability and conflicts"
    )
    
    # Create trainer and room first
    trainer = Trainer(
        FirstName="Mike",
        LastName="Trainer",
        Email="mike.trainer@example.com",
        Specialty="Strength Training"
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    
    room = Room(
        RoomNumber="101",
        RoomCapacity=10,
        RoomType="Training Room"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    
    # Success case
    print("\n--- SUCCESS CASE: Schedule PT Session ---")
    session = None
    try:
        session = schedule_pt_session(
            db,
            member_id,
            trainer.TrainerID,
            session_date=date.today() + timedelta(days=7),
            start_time=time(10, 0),
            end_time=time(11, 0),
            room_id=room.RoomID
        )
        print(f"[OK] Session scheduled successfully:")
        print(f"  Session ID: {session.SessionID}")
        print(f"  Date: {session.SessionDate}")
        print(f"  Time: {session.StartTime} - {session.EndTime}")
        print(f"  Trainer: {trainer.FirstName} {trainer.LastName}")
        print(f"  Room: {room.RoomNumber}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Trainer conflict
    print("\n--- FAILURE CASE: Trainer Time Conflict ---")
    try:
        schedule_pt_session(
            db,
            member_id,
            trainer.TrainerID,
            session_date=date.today() + timedelta(days=7),
            start_time=time(10, 30),  # Overlaps with previous session
            end_time=time(11, 30)
        )
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly detected trainer conflict: {e}")
    
    return session


def demo_trainer_availability(db, trainer_id):
    """Demonstrate Set Availability"""
    print_operation(
        "TRAINER",
        "1. Set Availability",
        "Define time windows when available for sessions (prevent overlap)"
    )
    
    # Success case
    print("\n--- SUCCESS CASE: Set Availability ---")
    try:
        result = set_availability(
            db,
            trainer_id,
            session_date=date.today() + timedelta(days=14),
            start_time=time(14, 0),
            end_time=time(17, 0)
        )
        print(f"[OK] Availability validated:")
        print(f"  Date: {result['date']}")
        print(f"  Time: {result['time']}")
        print(f"  Available: {result['available']}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Overlapping time
    print("\n--- FAILURE CASE: Overlapping Availability ---")
    try:
        set_availability(
            db,
            trainer_id,
            session_date=date.today() + timedelta(days=7),  # Same date as scheduled session
            start_time=time(10, 30),  # Overlaps with existing session
            end_time=time(11, 30)
        )
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly detected overlap: {e}")


def demo_trainer_schedule_view(db, trainer_id):
    """Demonstrate Schedule View"""
    print_operation(
        "TRAINER",
        "2. Schedule View",
        "View assigned PT sessions and classes"
    )
    
    # Success case
    print("\n--- SUCCESS CASE: View Schedule ---")
    try:
        sessions = view_schedule(db, trainer_id)
        print(f"[OK] Found {len(sessions)} upcoming session(s):")
        for s in sessions:
            print(f"  - {s.SessionDate} {s.StartTime}-{s.EndTime}: {s.SessionType}")
            if s.room:
                print(f"    Room: {s.room.RoomNumber}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Edge case: No sessions
    print("\n--- EDGE CASE: No Upcoming Sessions ---")
    # Create a trainer with no sessions
    trainer2 = Trainer(
        FirstName="Sarah",
        LastName="Coach",
        Email="sarah.coach@example.com"
    )
    db.add(trainer2)
    db.commit()
    db.refresh(trainer2)
    
    try:
        sessions = view_schedule(db, trainer2.TrainerID)
        if not sessions:
            print("[OK] Correctly returned empty list (no sessions)")
        else:
            print(f"Found {len(sessions)} sessions")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def demo_trainer_member_lookup(db):
    """Demonstrate Member Lookup"""
    print_operation(
        "TRAINER",
        "3. Member Lookup",
        "Search members by name (case-insensitive), view goals and metrics (read-only)"
    )
    
    # Success case
    print("\n--- SUCCESS CASE: Member Lookup ---")
    try:
        results = lookup_member(db, "Alice")
        if results:
            for r in results:
                member = r['member']
                goal = r['latest_goal']
                metric = r['latest_metric']
                print(f"[OK] Found member:")
                print(f"  Name: {member.FirstName} {member.LastName}")
                print(f"  Email: {member.Email}")
                if goal:
                    print(f"  Latest Goal: {goal.GoalType} ({goal.GoalStatus})")
                if metric:
                    print(f"  Latest Metric: Weight={metric.Weight}lbs (Date: {metric.RecordedDate})")
        else:
            print("No members found")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Empty search
    print("\n--- FAILURE CASE: Empty Search Term ---")
    try:
        lookup_member(db, "")
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected empty search: {e}")


def demo_admin_room_booking(db, session_id, room_id):
    """Demonstrate Room Booking"""
    print_operation(
        "ADMIN",
        "1. Room Booking",
        "Assign rooms to sessions or classes (prevent double-booking)"
    )
    
    # Create another room
    room2 = Room(
        RoomNumber="201",
        RoomCapacity=20,
        RoomType="Studio"
    )
    db.add(room2)
    db.commit()
    db.refresh(room2)
    
    # Success case
    print("\n--- SUCCESS CASE: Assign Room Booking ---")
    try:
        session = assign_room_booking(db, session_id, room2.RoomID)
        print(f"[OK] Room assigned successfully:")
        print(f"  Session ID: {session.SessionID}")
        print(f"  Room: {room2.RoomNumber}")
        print(f"  Room Capacity: {room2.RoomCapacity}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Room conflict
    print("\n--- FAILURE CASE: Room Double-Booking ---")
    # Create another session at same time but with a different trainer to avoid trainer conflict
    member2 = register_member(
        db,
        first_name="Bob",
        last_name="Smith",
        email="bob.smith@example.com"
    )
    
    trainer2 = Trainer(
        FirstName="Laura",
        LastName="Coach",
        Email="laura.coach@example.com",
        Specialty="Group Fitness"
    )
    db.add(trainer2)
    db.commit()
    db.refresh(trainer2)
    
    session2 = schedule_pt_session(
        db,
        member2.MemberID,
        trainer2.TrainerID,
        session_date=date.today() + timedelta(days=7),
        start_time=time(10, 0),
        end_time=time(11, 0)
    )
    
    try:
        assign_room_booking(db, session2.SessionID, room2.RoomID)  # Same room, same time
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly detected room conflict: {e}")


def demo_admin_maintenance(db):
    """Demonstrate Equipment Maintenance"""
    print_operation(
        "ADMIN",
        "2. Equipment Maintenance",
        "Log maintenance issues and update repair status"
    )
    
    # Create admin
    admin = AdminStaff(
        FirstName="Admin",
        LastName="Manager",
        Email="admin@example.com",
        Role="Manager"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    room = db.query(Room).filter(Room.RoomNumber == "101").first()
    
    # Success case: Log issue
    print("\n--- SUCCESS CASE: Log Maintenance Issue ---")
    try:
        issue = log_maintenance_issue(
            db,
            room.RoomID,
            admin.AdminID,
            issue_description="Treadmill not working properly",
            equipment_name="Treadmill #3",
            priority="High"
        )
        print(f"[OK] Maintenance issue logged:")
        print(f"  Issue ID: {issue.IssueID}")
        print(f"  Room: {room.RoomNumber}")
        print(f"  Priority: {issue.Priority}")
        print(f"  Status: {issue.Status}")
        issue_id = issue.IssueID
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return
    
    # Success case: Update status
    print("\n--- SUCCESS CASE: Update Maintenance Status ---")
    try:
        updated = update_maintenance_status(
            db,
            issue_id,
            status="In Progress",
            assigned_repair_date=date.today() + timedelta(days=3)
        )
        print(f"[OK] Status updated:")
        print(f"  Status: {updated.Status}")
        print(f"  Assigned Repair Date: {updated.AssignedRepairDate}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Invalid status transition
    print("\n--- FAILURE CASE: Invalid Status Transition ---")
    # First resolve it in two steps (status change, then resolution date)
    update_maintenance_status(db, issue_id, status="Resolved")
    update_maintenance_status(db, issue_id, resolution_date=date.today())
    
    try:
        update_maintenance_status(db, issue_id, status="Open")  # Can't reopen resolved issue
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected invalid status transition: {e}")


def demo_admin_billing(db, member_id):
    """Demonstrate Billing & Payment"""
    print_operation(
        "ADMIN",
        "3. Billing & Payment",
        "Generate invoices and record payments (simulated)"
    )
    
    # Success case: Create invoice
    print("\n--- SUCCESS CASE: Create Invoice ---")
    try:
        invoice = create_invoice(
            db,
            payer_id=member_id,
            invoice_number="INV-001",
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            amount=75.00,
            service_description="Personal Training Session"
        )
        print(f"[OK] Invoice created:")
        print(f"  Invoice Number: {invoice.InvoiceNumber}")
        print(f"  Amount: ${invoice.Amount}")
        print(f"  Status: {invoice.PaymentStatus}")
        print(f"  Due Date: {invoice.DueDate}")
        invoice_id = invoice.InvoiceID
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return
    
    # Success case: Record payment
    print("\n--- SUCCESS CASE: Record Payment ---")
    try:
        paid_invoice = record_payment(
            db,
            invoice_id,
            payment_method="Credit Card"
        )
        print(f"[OK] Payment recorded:")
        print(f"  Invoice: {paid_invoice.InvoiceNumber}")
        print(f"  Payment Method: {paid_invoice.PaymentMethod}")
        print(f"  Status: {paid_invoice.PaymentStatus}")
        print(f"  Paid Date: {paid_invoice.PaidDate}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    # Failure case: Double payment
    print("\n--- FAILURE CASE: Double Payment ---")
    try:
        record_payment(db, invoice_id, payment_method="Cash")  # Already paid
        print("[ERROR] Should have failed but didn't!")
    except ValueError as e:
        print(f"[OK] Correctly rejected double payment: {e}")


def main():
    """Run all demonstrations"""
    print_section("HEALTH AND FITNESS CLUB MANAGEMENT SYSTEM - DEMONSTRATION")
    print("\nThis script demonstrates all implemented operations:")
    print("  - Member Functions (4 operations)")
    print("  - Trainer Functions (3 operations)")
    print("  - Admin Functions (3 operations)")
    print("\nEach operation shows:")
    print("  [OK] Success case")
    print("  [ERROR] Failure/edge case")
    
    # Initialize database
    print("\n\nInitializing database...")
    try:
        drop_tables()
        init_db()
        print("[OK] Database initialized")
    except Exception as e:
        print(f"Note: {e}")
    
    db = SessionLocal()
    
    try:
        # Member Functions
        print_section("MEMBER FUNCTIONS")
        member = demo_member_registration(db)
        if member:
            demo_profile_management(db, member.MemberID)
            demo_health_history(db, member.MemberID)
            session = demo_pt_scheduling(db, member.MemberID)
        
        # Trainer Functions
        print_section("TRAINER FUNCTIONS")
        trainer = db.query(Trainer).filter(Trainer.Email == "mike.trainer@example.com").first()
        if trainer:
            demo_trainer_availability(db, trainer.TrainerID)
            demo_trainer_schedule_view(db, trainer.TrainerID)
        demo_trainer_member_lookup(db)
        
        # Admin Functions
        print_section("ADMIN FUNCTIONS")
        if session:
            room = db.query(Room).filter(Room.RoomNumber == "101").first()
            if room:
                demo_admin_room_booking(db, session.SessionID, room.RoomID)
        demo_admin_maintenance(db)
        if member:
            demo_admin_billing(db, member.MemberID)
        
        print_section("DEMONSTRATION COMPLETE")
        print("\n[OK] All operations demonstrated successfully!")
        print("\nSummary:")
        print("  - 4 Member operations: Registration, Profile Management, Health History, PT Scheduling")
        print("  - 3 Trainer operations: Set Availability, Schedule View, Member Lookup")
        print("  - 3 Admin operations: Room Booking, Maintenance, Billing & Payment")
        print("\nAll operations include:")
        print("  - Success cases demonstrating normal operation")
        print("  - Failure/edge cases showing proper error handling")
        
    except Exception as e:
        print(f"\n[ERROR] Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
