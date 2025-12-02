# Health and Fitness Club Management System

A database-driven fitness club management system built with SQLAlchemy ORM (Python) and PostgreSQL.

## Group Information
- **Group Size**: 2
- **Entities**: 9
- **Relationships**: 10
- **Functions**: 10 total (4 member, 3 trainer, 3 admin)

## Technology Stack
- **ORM**: SQLAlchemy 2.0+
- **Database**: PostgreSQL
- **Language**: Python 3.8+

## Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database**
   - Update `DB_CONFIG` in `database.py` with your PostgreSQL credentials
   - Default: username='postgres', password='postgres', host='localhost', port=5432, database='gymdb'

3. **Initialize database**
   ```bash
   python seed_data.py
   ```
   This creates all tables, views, triggers, and indexes using ORM.

4. **Run the application**
   ```bash
   python cli.py
   ```

## Project Structure

```
COMP3005_FinalProject/
├── models/                    # ORM entity classes (9 entities)
│   ├── __init__.py
│   ├── member.py
│   ├── trainer.py
│   ├── admin_staff.py
│   ├── room.py
│   ├── personal_training_session.py
│   ├── health_metric.py
│   ├── fitness_goal.py
│   ├── invoice.py
│   └── maintenance_issue.py
├── app/                       # Application logic
│   ├── __init__.py
│   ├── member_functions.py    # 4 member operations
│   ├── trainer_functions.py   # 3 trainer operations
│   └── admin_functions.py     # 3 admin operations
├── docs/                      # Documentation
│   └── ERD.pdf                # ER diagram + Mapping + Normalization
├── example_presentation.py    # Demo script for all operations
├── seed_data.py              # Sample data seeding (optional)
├── database.py                # Database configuration and setup (core infrastructure)
├── database_advanced.py       # Views, triggers, indexes (core infrastructure)
├── cli.py                     # Command-line interface (main entry point)
├── requirements.txt          # Python dependencies
├── REPORT.md                 # ORM Report
└── README.md                 # This file
```

## Implemented Functions

### Member Functions (4)
1. **User Registration** - Create new member with unique email
2. **Profile Management** - Update profile, add fitness goals
3. **Health History** - Log health metrics (historical tracking)
4. **PT Session Scheduling** - Book/reschedule training sessions

### Trainer Functions (3)
1. **Set Availability** - Define available time windows
2. **Schedule View** - View assigned sessions and classes
3. **Member Lookup** - Search members and view goals/metrics

### Admin Functions (3)
1. **Room Booking** - Assign rooms to sessions (prevent conflicts)
2. **Equipment Maintenance** - Log and update maintenance issues
3. **Billing & Payment** - Create invoices and record payments

## Demo Video

https://www.youtube.com/watch?v=GR_Hh5LATeA
