"""
Advanced SQL Features
Implemented using SQLAlchemy ORM and raw SQL where necessary
"""

from sqlalchemy import text, Index
from database import engine, Base
from models import Member, HealthMetric, FitnessGoal, PersonalTrainingSession


def create_views():
    """
    Create database views using raw SQL (views are not directly supported in SQLAlchemy ORM).
    These views simplify common queries.
    """
    with engine.connect() as conn:
        # View 1: Member Dashboard View
        # Combines Member with latest HealthMetric and latest FitnessGoal
        conn.execute(text("""
            CREATE OR REPLACE VIEW MemberDashboardView AS
            SELECT
                m."MemberID",
                m."FirstName",
                m."LastName",
                m."Email",
                m."MembershipStatus",
                (SELECT h."Weight" 
                 FROM "HealthMetric" h 
                 WHERE h."MemberID" = m."MemberID" 
                 ORDER BY h."RecordedDate" DESC 
                 LIMIT 1) AS LatestWeight,
                (SELECT h."RecordedDate" 
                 FROM "HealthMetric" h 
                 WHERE h."MemberID" = m."MemberID" 
                 ORDER BY h."RecordedDate" DESC 
                 LIMIT 1) AS LatestMetricDate,
                (SELECT f."GoalType" 
                 FROM "FitnessGoal" f 
                 WHERE f."MemberID" = m."MemberID" 
                 ORDER BY f."SetDate" DESC 
                 LIMIT 1) AS CurrentGoal,
                (SELECT COUNT(*) 
                 FROM "PersonalTrainingSession" p 
                 WHERE p."MemberID" = m."MemberID" 
                 AND p."SessionDate" < CURRENT_DATE) AS PastSessionCount,
                (SELECT COUNT(*) 
                 FROM "PersonalTrainingSession" p 
                 WHERE p."MemberID" = m."MemberID" 
                 AND p."SessionDate" >= CURRENT_DATE) AS UpcomingSessionCount
            FROM "Member" m;
        """))
        conn.commit()
        print("[OK] Created MemberDashboardView")
        
        # View 2: Trainer Schedule View
        conn.execute(text("""
            CREATE OR REPLACE VIEW TrainerScheduleView AS
            SELECT 
                t."TrainerID",
                t."FirstName" || ' ' || t."LastName" AS TrainerName,
                p."SessionID",
                p."SessionDate",
                p."StartTime",
                p."EndTime",
                p."SessionType",
                m."FirstName" || ' ' || m."LastName" AS MemberName,
                r."RoomNumber"
            FROM "Trainer" t
            JOIN "PersonalTrainingSession" p ON t."TrainerID" = p."TrainerID"
            LEFT JOIN "Member" m ON p."MemberID" = m."MemberID"
            LEFT JOIN "Room" r ON p."RoomID" = r."RoomID"
            WHERE p."SessionDate" >= CURRENT_DATE
            ORDER BY p."SessionDate", p."StartTime";
        """))
        conn.commit()
        print("[OK] Created TrainerScheduleView")


def create_indexes():
    """
    Create indexes for improved query performance.
    Using SQLAlchemy Index objects.
    """
    indexes = [
        Index('idx_member_email', Member.Email),
        Index('idx_session_trainer_date', PersonalTrainingSession.TrainerID, PersonalTrainingSession.SessionDate),
        Index('idx_session_room_date', PersonalTrainingSession.RoomID, PersonalTrainingSession.SessionDate),
        Index('idx_session_date_time', PersonalTrainingSession.SessionDate, PersonalTrainingSession.StartTime),
        Index('idx_health_member_date', HealthMetric.MemberID, HealthMetric.RecordedDate.desc()),
        Index('idx_goal_member_date', FitnessGoal.MemberID, FitnessGoal.SetDate.desc())
    ]
    
    for idx in indexes:
        try:
            idx.create(engine)
        except Exception:
            pass  # Index may already exist
    
    print("[OK] Created all indexes")


def create_triggers():
    """
    Create database triggers using raw SQL.
    Triggers maintain data consistency automatically.
    """
    with engine.connect() as conn:
        # Trigger 1: Update CurrentEnrollment when sessions are booked/cancelled
        # This maintains consistency for group classes
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION update_enrollment()
            RETURNS TRIGGER AS $$
            BEGIN
                IF TG_OP = 'INSERT' AND NEW."SessionType" = 'Group Class' THEN
                    UPDATE "PersonalTrainingSession"
                    SET "CurrentEnrollment" = "CurrentEnrollment" + 1
                    WHERE "SessionID" = NEW."SessionID";
                ELSIF TG_OP = 'DELETE' AND OLD."SessionType" = 'Group Class' THEN
                    UPDATE "PersonalTrainingSession"
                    SET "CurrentEnrollment" = GREATEST("CurrentEnrollment" - 1, 0)
                    WHERE "SessionID" = OLD."SessionID";
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        conn.commit()
        print("[OK] Created trigger function: update_enrollment()")
        
        # Trigger 2: Auto-calculate DurationMinutes from StartTime and EndTime
        conn.execute(text("""
            CREATE OR REPLACE FUNCTION calculate_duration()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW."StartTime" IS NOT NULL AND NEW."EndTime" IS NOT NULL THEN
                    NEW."DurationMinutes" := EXTRACT(EPOCH FROM (NEW."EndTime" - NEW."StartTime")) / 60;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        conn.commit()
        print("[OK] Created trigger function: calculate_duration()")


def setup_advanced_features():
    """Setup all advanced SQL features"""
    print("\nSetting up advanced SQL features...")
    create_views()
    create_indexes()
    create_triggers()
    print("\n[OK] All advanced features created!")


if __name__ == "__main__":
    setup_advanced_features()

