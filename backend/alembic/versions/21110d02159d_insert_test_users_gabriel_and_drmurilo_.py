"""Insert test users gabriel and drmurilo with relationship

Revision ID: 21110d02159d
Revises: b68a022b1d28
Create Date: 2025-05-26 16:18:10.010862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21110d02159d'
down_revision: Union[str, None] = 'b68a022b1d28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Execute user insertions
    connection = op.get_bind()

    # Update existing users with standardized level_of_education values (since they already exist)
    connection.execute(sa.text("""
        UPDATE users
        SET
            level_of_education = 'bachelor_degree',
            email = 'gabriel@example.com',
            updated_at = CURRENT_TIMESTAMP
        WHERE username = 'gabriel'
    """))

    connection.execute(sa.text("""
        UPDATE users
        SET
            level_of_education = 'professional_degree',
            email = 'drmurilo@hospital.com',
            specialty = 'Internal Medicine',
            license_number = 'CRM-12345',
            organization = 'Hospital São Paulo',
            updated_at = CURRENT_TIMESTAMP
        WHERE username = 'drmurilo'
    """))

    # Update relationship between Gabriel and Dr. Murilo (if it exists)
    # If it doesn't exist, this will do nothing (which is fine since it already exists)
    connection.execute(sa.text("""
        UPDATE patient_professional_relationships r
        JOIN users p ON r.patient_id = p.id
        JOIN users prof ON r.professional_id = prof.id
        SET
            r.notes = 'Sample patient-doctor relationship for testing document sharing functionality',
            r.updated_at = CURRENT_TIMESTAMP
        WHERE p.username = 'gabriel' AND prof.username = 'drmurilo'
    """))


def downgrade() -> None:
    # Remove the test relationship
    connection = op.get_bind()
    connection.execute(sa.text("""
        DELETE r FROM patient_professional_relationships r
        JOIN users p ON r.patient_id = p.id
        JOIN users prof ON r.professional_id = prof.id
        WHERE p.username = 'gabriel' AND prof.username = 'drmurilo'
    """))

    # Remove test users
    connection.execute(sa.text("DELETE FROM users WHERE username IN ('gabriel', 'drmurilo')"))
