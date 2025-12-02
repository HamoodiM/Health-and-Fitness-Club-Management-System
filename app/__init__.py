# Application package initialization
# Import all functions for easy access

from .member_functions import (
    register_member,
    update_profile,
    add_fitness_goal,
    log_health_metric,
    schedule_pt_session
)

from .trainer_functions import (
    set_availability,
    view_schedule,
    lookup_member
)

from .admin_functions import (
    assign_room_booking,
    log_maintenance_issue,
    update_maintenance_status,
    create_invoice,
    record_payment
)

__all__ = [
    # Member functions
    'register_member',
    'update_profile',
    'add_fitness_goal',
    'log_health_metric',
    'schedule_pt_session',
    # Trainer functions
    'set_availability',
    'view_schedule',
    'lookup_member',
    # Admin functions
    'assign_room_booking',
    'log_maintenance_issue',
    'update_maintenance_status',
    'create_invoice',
    'record_payment'
]

