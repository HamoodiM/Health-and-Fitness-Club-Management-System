"""
Seed Database with Sample Data
This replaces DML.sql when using ORM - all data is inserted via ORM
"""

from datetime import date, time
from database import SessionLocal, create_tables
from models import (
    Member, Trainer, AdminStaff, Room,
    PersonalTrainingSession, HealthMetric, FitnessGoal,
    Invoice, MaintenanceIssue
)


def seed_database():
    """
    Populate database with sample data using ORM.
    This demonstrates how DML operations are done via ORM instead of SQL.
    """
    db = SessionLocal()
    
    try:
        print("Seeding database with sample data...")
        
        # Create Members
        members = [
            Member(
                FirstName="John",
                LastName="Doe",
                Email="john.doe@example.com",
                DateOfBirth=date(1990, 5, 15),
                Gender="M",
                Phone="555-0100",
                Address="123 Main St",
                JoinDate=date(2023, 1, 15),
                MembershipStatus="Active"
            ),
            Member(
                FirstName="Jane",
                LastName="Smith",
                Email="jane.smith@example.com",
                DateOfBirth=date(1985, 8, 22),
                Gender="F",
                Phone="555-0200",
                Address="456 Oak Ave",
                JoinDate=date(2023, 3, 10),
                MembershipStatus="Active"
            ),
            Member(
                FirstName="Bob",
                LastName="Johnson",
                Email="bob.johnson@example.com",
                DateOfBirth=date(1992, 11, 5),
                Gender="M",
                Phone="555-0300",
                JoinDate=date(2024, 6, 1),
                MembershipStatus="Active"
            )
        ]
        db.add_all(members)
        db.commit()
        print(f"[OK] Created {len(members)} members")
        
        # Create Trainers
        trainers = [
            Trainer(
                FirstName="Mike",
                LastName="Trainer",
                Email="mike.trainer@example.com",
                DateOfBirth=date(1988, 3, 10),
                Gender="M",
                Phone="555-1000",
                Specialty="Strength Training",
                HireDate=date(2020, 1, 15)
            ),
            Trainer(
                FirstName="Sarah",
                LastName="Coach",
                Email="sarah.coach@example.com",
                DateOfBirth=date(1990, 7, 20),
                Gender="F",
                Phone="555-1100",
                Specialty="Yoga",
                HireDate=date(2021, 3, 1)
            )
        ]
        db.add_all(trainers)
        db.commit()
        print(f"[OK] Created {len(trainers)} trainers")
        
        # Create Admin Staff
        admins = [
            AdminStaff(
                FirstName="Admin",
                LastName="Manager",
                Email="admin@example.com",
                DateOfBirth=date(1980, 1, 1),
                Gender="M",
                Phone="555-2000",
                Role="Manager",
                HireDate=date(2019, 1, 1)
            )
        ]
        db.add_all(admins)
        db.commit()
        print(f"[OK] Created {len(admins)} admin staff")
        
        # Create Rooms
        rooms = [
            Room(
                RoomNumber="101",
                RoomCapacity=10,
                RoomType="Training Room",
                AccessPermissions="Members Only"
            ),
            Room(
                RoomNumber="201",
                RoomCapacity=20,
                RoomType="Studio",
                AccessPermissions="All Members"
            ),
            Room(
                RoomNumber="301",
                RoomCapacity=5,
                RoomType="Private",
                AccessPermissions="Premium Members"
            )
        ]
        db.add_all(rooms)
        db.commit()
        print(f"[OK] Created {len(rooms)} rooms")
        
        # Create Health Metrics
        health_metrics = [
            HealthMetric(
                MemberID=members[0].MemberID,
                RecordedDate=date(2024, 1, 1),
                Height=70.0,
                Weight=180.0,
                BodyFatPercentage=20.0,
                RestingHeartRate=65
            ),
            HealthMetric(
                MemberID=members[0].MemberID,
                RecordedDate=date(2024, 2, 1),
                Height=70.0,
                Weight=175.0,  # Weight loss tracked
                BodyFatPercentage=18.5,
                RestingHeartRate=62
            ),
            HealthMetric(
                MemberID=members[1].MemberID,
                RecordedDate=date(2024, 1, 15),
                Height=65.0,
                Weight=140.0,
                BodyFatPercentage=22.0,
                RestingHeartRate=70
            )
        ]
        db.add_all(health_metrics)
        db.commit()
        print(f"[OK] Created {len(health_metrics)} health metrics")
        
        # Create Fitness Goals
        fitness_goals = [
            FitnessGoal(
                MemberID=members[0].MemberID,
                GoalType="Weight Loss",
                TargetBodyWeight=170.0,
                TargetBodyFatPercentage=15.0,
                SetDate=date(2024, 1, 1),
                TargetDate=date(2024, 12, 31),
                GoalStatus="Active"
            ),
            FitnessGoal(
                MemberID=members[1].MemberID,
                GoalType="Muscle Gain",
                TargetBodyWeight=145.0,
                SetDate=date(2024, 1, 15),
                TargetDate=date(2024, 6, 30),
                GoalStatus="Active"
            )
        ]
        db.add_all(fitness_goals)
        db.commit()
        print(f"[OK] Created {len(fitness_goals)} fitness goals")
        
        # Create Sessions
        sessions = [
            PersonalTrainingSession(
                TrainerID=trainers[0].TrainerID,
                MemberID=members[0].MemberID,
                RoomID=rooms[0].RoomID,
                SessionDate=date(2024, 12, 15),
                StartTime=time(10, 0),
                EndTime=time(11, 0),
                DurationMinutes=60,
                SessionType="Personal Training",
                Notes="Focus on strength training"
            ),
            PersonalTrainingSession(
                TrainerID=trainers[1].TrainerID,
                MemberID=members[1].MemberID,
                RoomID=rooms[1].RoomID,
                SessionDate=date(2024, 12, 16),
                StartTime=time(14, 0),
                EndTime=time(15, 0),
                DurationMinutes=60,
                SessionType="Personal Training",
                Notes="Yoga session"
            )
        ]
        db.add_all(sessions)
        db.commit()
        print(f"[OK] Created {len(sessions)} sessions")
        
        # Create Invoices
        invoices = [
            Invoice(
                InvoiceNumber="INV-001",
                PayerID=members[0].MemberID,
                SessionID=sessions[0].SessionID,
                InvoiceDate=date(2024, 12, 10),
                DueDate=date(2024, 12, 31),
                Amount=75.00,
                PaymentMethod="Credit Card",
                PaymentStatus="Paid",
                ServiceDescription="Personal Training Session",
                PaidDate=date(2024, 12, 10)
            ),
            Invoice(
                InvoiceNumber="INV-002",
                PayerID=members[1].MemberID,
                InvoiceDate=date(2024, 12, 1),
                DueDate=date(2024, 12, 31),
                Amount=50.00,
                PaymentStatus="Pending",
                ServiceDescription="Monthly Membership Fee"
            )
        ]
        db.add_all(invoices)
        db.commit()
        print(f"[OK] Created {len(invoices)} invoices")
        
        # Create Maintenance Issues
        maintenance_issues = [
            MaintenanceIssue(
                RoomID=rooms[0].RoomID,
                AdminID=admins[0].AdminID,
                IssueDescription="Treadmill not working properly",
                EquipmentName="Treadmill #3",
                ReportedDate=date(2024, 12, 10),
                Priority="High",
                Status="Open"
            ),
            MaintenanceIssue(
                RoomID=rooms[1].RoomID,
                AdminID=admins[0].AdminID,
                IssueDescription="Light bulb needs replacement",
                ReportedDate=date(2024, 12, 12),
                Priority="Low",
                Status="Resolved",
                ResolutionDate=date(2024, 12, 13),
                ResolutionNotes="Replaced bulb"
            )
        ]
        db.add_all(maintenance_issues)
        db.commit()
        print(f"[OK] Created {len(maintenance_issues)} maintenance issues")
        
        print("\n[OK] Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Create tables first
    print("Creating database tables...")
    create_tables()
    
    # Seed with data
    seed_database()

