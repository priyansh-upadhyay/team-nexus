# Database models package.
#
# All SQLAlchemy models must be imported here for Alembic autogeneration to work properly.
# This ensures that Alembic can discover all models when creating and applying migrations.
#
# Import all models in this file to make them available to the database migration system.
# This is a SQLAlchemy best practice for production applications.
#
# Model imports:
from .user import User
from .team import Team
from .team_member import TeamMember
from .project import Project
from .task import Task

# Example future imports (do not uncomment until models are created):
# from .organization import Organization
# from .project import Project
# from .task import Task
# from .membership import Membership
# from .invitation import Invitation

