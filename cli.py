"""
Command Line Interface for Gym Management System
Provides role-based menus for Member, Trainer, and Admin functions
"""

from datetime import date, datetime
from database import SessionLocal, init_db
from app.member_functions import (
    register_member, update_profile, add_fitness_goal,
    log_health_metric, schedule_pt_session
)
from app.trainer_functions import set_availability, view_schedule, lookup_member
from app.admin_functions import (
    assign_room_booking, log_maintenance_issue, update_maintenance_status,
    create_invoice, record_payment
)
from sqlalchemy.orm import Session


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def get_input(prompt, input_type=str, default=None, allow_empty=False):
    """Get user input with type conversion"""
    while True:
        try:
            value = input(f"{prompt}: ").strip()
            if not value:
                if default is not None:
                    return default
                if allow_empty:
                    return None
                print("This field cannot be empty. Please enter a value.")
                continue
            return input_type(value)
        except ValueError:
            print(f"Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None


def get_date_input(prompt, allow_empty=True):
    """Get date input in YYYY-MM-DD format"""
    while True:
        try:
            value = input(f"{prompt} (YYYY-MM-DD, e.g., 1990-05-15): ").strip()
            if not value:
                if allow_empty:
                    return None
                print("Date is required. Please enter a date.")
                continue
            # Parse date
            date_obj = datetime.strptime(value, "%Y-%m-%d").date()
            return date_obj
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None


def get_phone_input(prompt, allow_empty=True):
    """Get phone number input with formatting hints"""
    while True:
        try:
            value = input(f"{prompt} (e.g., 555-1234, (555) 123-4567, or 5551234567): ").strip()
            if not value:
                if allow_empty:
                    return None
                print("Phone number is required. Please enter a phone number.")
                continue
            # Remove common formatting characters for storage
            cleaned = value.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
            # Basic validation - should contain only digits
            if not cleaned.isdigit():
                print("Phone number should contain only digits and formatting characters.")
                continue
            # Return original formatted value (or cleaned if preferred)
            return value  # Store as user entered it
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None


def member_menu(db: Session):
    """Member role menu"""
    while True:
        print_header("MEMBER MENU")
        print("1. Register New Member")
        print("2. Update Profile")
        print("3. Add Fitness Goal")
        print("4. Log Health Metric")
        print("5. Schedule PT Session")
        print("6. Back to Main Menu")
        
        choice = get_input("\nSelect option", int)
        
        if choice == 1:
            print_header("User Registration")
            try:
                member = register_member(
                    db,
                    first_name=get_input("First Name", allow_empty=False),
                    last_name=get_input("Last Name", allow_empty=False),
                    email=get_input("Email", allow_empty=False),
                    date_of_birth=get_date_input("Date of Birth"),
                    gender=get_input("Gender (M/F/O)", str, allow_empty=True) or None,
                    phone=get_phone_input("Phone Number"),
                    address=get_input("Address", str, allow_empty=True) or None
                )
                print(f"\n[OK] Successfully registered: {member.FirstName} {member.LastName} (ID: {member.MemberID})")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 2:
            print_header("Update Profile")
            member_id = get_input("Member ID", int)
            try:
                member = update_profile(
                    db,
                    member_id,
                    first_name=get_input("First Name (leave empty to skip)", str, allow_empty=True) or None,
                    last_name=get_input("Last Name (leave empty to skip)", str, allow_empty=True) or None,
                    phone=get_phone_input("Phone Number (leave empty to skip)"),
                    address=get_input("Address (leave empty to skip)", str, allow_empty=True) or None
                )
                print(f"\n[OK] Profile updated: {member.FirstName} {member.LastName}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 3:
            print_header("Add Fitness Goal")
            member_id = get_input("Member ID", int)
            try:
                goal = add_fitness_goal(
                    db,
                    member_id,
                    goal_type=get_input("Goal Type", allow_empty=False),
                    target_body_weight=get_input("Target Body Weight", float, allow_empty=True) or None,
                    target_body_fat=get_input("Target Body Fat %", float, allow_empty=True) or None,
                    target_date=get_date_input("Target Date")
                )
                print(f"\n[OK] Goal added: {goal.GoalType}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 4:
            print_header("Log Health Metric")
            member_id = get_input("Member ID", int)
            try:
                metric = log_health_metric(
                    db,
                    member_id,
                    recorded_date=date.today(),
                    weight=get_input("Weight", float) or None,
                    height=get_input("Height", float) or None,
                    body_fat_percentage=get_input("Body Fat %", float) or None,
                    resting_heart_rate=get_input("Resting Heart Rate", int) or None
                )
                print(f"\n[OK] Health metric logged for date: {metric.RecordedDate}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 5:
            print_header("Schedule PT Session")
            member_id = get_input("Member ID", int)
            trainer_id = get_input("Trainer ID", int)
            room_id = get_input("Room ID (leave empty if none)", int, allow_empty=True) or None
            session_date = get_date_input("Session Date", allow_empty=False)
            start_time = get_input("Start Time (HH:MM, e.g., 10:30)", str, allow_empty=False)
            end_time = get_input("End Time (HH:MM, e.g., 11:30)", str, allow_empty=False)
            
            try:
                start = datetime.strptime(start_time, "%H:%M").time()
                end = datetime.strptime(end_time, "%H:%M").time()
                
                session = schedule_pt_session(
                    db,
                    member_id,
                    trainer_id,
                    session_date,
                    start,
                    end,
                    room_id=room_id
                )
                print(f"\n[OK] Session scheduled: Session ID {session.SessionID}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
            except Exception as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 6:
            break
        
        input("\nPress Enter to continue...")


def trainer_menu(db: Session):
    """Trainer role menu"""
    while True:
        print_header("TRAINER MENU")
        print("1. Set Availability")
        print("2. View Schedule")
        print("3. Lookup Member")
        print("4. Back to Main Menu")
        
        choice = get_input("\nSelect option", int)
        
        if choice == 1:
            print_header("Set Availability")
            trainer_id = get_input("Trainer ID", int)
            session_date = get_input("Date (YYYY-MM-DD)", str)
            start_time = get_input("Start Time (HH:MM)", str)
            end_time = get_input("End Time (HH:MM)", str)
            
            try:
                start = datetime.strptime(start_time, "%H:%M").time()
                end = datetime.strptime(end_time, "%H:%M").time()
                date_obj = datetime.strptime(session_date, "%Y-%m-%d").date()
                
                result = set_availability(db, trainer_id, date_obj, start, end)
                print(f"\n[OK] {result['message']}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 2:
            print_header("View Schedule")
            trainer_id = get_input("Trainer ID", int)
            try:
                sessions = view_schedule(db, trainer_id)
                if sessions:
                    print(f"\nFound {len(sessions)} upcoming sessions:")
                    for s in sessions:
                        print(f"  - {s.SessionDate} {s.StartTime}-{s.EndTime}: {s.SessionType}")
                else:
                    print("\nNo upcoming sessions found.")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 3:
            print_header("Member Lookup")
            search_term = get_input("Search by name (first name, last name, or full name)", allow_empty=False)
            try:
                results = lookup_member(db, search_term)
                if results:
                    print(f"\nFound {len(results)} member(s):")
                    for r in results:
                        member = r['member']
                        goal = r['latest_goal']
                        metric = r['latest_metric']
                        print(f"\nMember: {member.FirstName} {member.LastName} (ID: {member.MemberID})")
                        print(f"  Email: {member.Email}")
                        if member.Phone:
                            print(f"  Phone: {member.Phone}")
                        if goal:
                            print(f"  Latest Goal: {goal.GoalType} (Status: {goal.GoalStatus})")
                        if metric:
                            print(f"  Latest Metric: Weight={metric.Weight}lbs, Date={metric.RecordedDate}")
                else:
                    print(f"\nNo members found matching '{search_term}'.")
                    print("Tip: Try searching by first name, last name, or full name (e.g., 'John' or 'John Doe')")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 4:
            break
        
        input("\nPress Enter to continue...")


def admin_menu(db: Session):
    """Admin role menu"""
    while True:
        print_header("ADMIN MENU")
        print("1. Assign Room Booking")
        print("2. Log Maintenance Issue")
        print("3. Update Maintenance Status")
        print("4. Create Invoice")
        print("5. Record Payment")
        print("6. Back to Main Menu")
        
        choice = get_input("\nSelect option", int)
        
        if choice == 1:
            print_header("Assign Room Booking")
            session_id = get_input("Session ID", int)
            room_id = get_input("Room ID", int)
            try:
                session = assign_room_booking(db, session_id, room_id)
                print(f"\n[OK] Room {room_id} assigned to session {session_id}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 2:
            print_header("Log Maintenance Issue")
            room_id = get_input("Room ID", int)
            admin_id = get_input("Admin ID", int)
            description = get_input("Issue Description")
            equipment = get_input("Equipment Name (optional)", str) or None
            priority = get_input("Priority (Low/Medium/High/Critical)", str) or "Medium"
            
            try:
                issue = log_maintenance_issue(
                    db, room_id, admin_id, description, equipment, priority
                )
                print(f"\n[OK] Maintenance issue logged: Issue ID {issue.IssueID}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 3:
            print_header("Update Maintenance Status")
            issue_id = get_input("Issue ID", int)
            status = get_input("New Status (Open/In Progress/Resolved/Closed)", str, allow_empty=True) or None
            assigned_date = get_date_input("Assigned Repair Date (optional)")
            try:
                issue = update_maintenance_status(
                    db, 
                    issue_id, 
                    status=status,
                    assigned_repair_date=assigned_date
                )
                print(f"\n[OK] Issue {issue_id} updated to: {issue.Status}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 4:
            print_header("Create Invoice")
            payer_id = get_input("Payer (Member) ID", int)
            invoice_number = get_input("Invoice Number", allow_empty=False)
            amount = get_input("Amount", float, allow_empty=False)
            description = get_input("Service Description", allow_empty=False)
            session_id = get_input("Session ID (optional)", int, allow_empty=True) or None
            due_date = get_date_input("Due Date", allow_empty=False)
            
            try:
                invoice = create_invoice(
                    db,
                    payer_id,
                    invoice_number,
                    date.today(),
                    due_date,
                    amount,
                    description,
                    session_id=session_id
                )
                print(f"\n[OK] Invoice created: {invoice.InvoiceNumber} - ${amount}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 5:
            print_header("Record Payment")
            invoice_id = get_input("Invoice ID", int)
            payment_method = get_input("Payment Method")
            try:
                invoice = record_payment(db, invoice_id, payment_method)
                print(f"\n[OK] Payment recorded: {invoice.InvoiceNumber} - Status: {invoice.PaymentStatus}")
            except ValueError as e:
                print(f"\n[ERROR] Error: {e}")
        
        elif choice == 6:
            break
        
        input("\nPress Enter to continue...")


def main():
    """Main menu"""
    db = SessionLocal()
    
    try:
        while True:
            print_header("GYM MANAGEMENT SYSTEM")
            print("Select your role:")
            print("1. Member")
            print("2. Trainer")
            print("3. Admin Staff")
            print("4. Exit")
            
            choice = get_input("\nSelect option", int)
            
            if choice == 1:
                member_menu(db)
            elif choice == 2:
                trainer_menu(db)
            elif choice == 3:
                admin_menu(db)
            elif choice == 4:
                print("\nThank you for using Gym Management System!")
                break
            else:
                print("\nInvalid option. Please try again.")
    
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database on first run (includes views, triggers, indexes)
    try:
        init_db()
    except Exception as e:
        print(f"Database already initialized or error: {e}")
    
    main()

