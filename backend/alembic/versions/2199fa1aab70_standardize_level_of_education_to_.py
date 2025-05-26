"""Standardize level_of_education to predefined values

Revision ID: 2199fa1aab70
Revises: 21110d02159d
Create Date: 2025-05-26 16:28:54.426980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2199fa1aab70'
down_revision: Union[str, None] = '21110d02159d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Standardize level_of_education column to use predefined values.
    """
    connection = op.get_bind()

    # Step 1: Add a temporary column with the new ENUM type (nullable initially for migration)
    op.add_column('users', sa.Column('level_of_education_new',
        sa.Enum(
            'elementary_school',
            'middle_school',
            'high_school',
            'associate_degree',
            'bachelor_degree',
            'master_degree',
            'doctoral_degree',
            'professional_degree',  # MD, JD, PharmD, etc.
            'other',
            name='education_level_enum'
        ),
        nullable=True  # Temporarily nullable for migration
    ))

    # Step 2: Map existing free-form values to standardized values
    connection.execute(sa.text("""
        UPDATE users
        SET level_of_education_new = CASE
            -- Map bachelor degrees
            WHEN level_of_education LIKE '%bachelor%' OR level_of_education LIKE '%Bachelor%'
                THEN 'bachelor_degree'

            -- Map master degrees
            WHEN level_of_education LIKE '%master%' OR level_of_education LIKE '%Master%'
                OR level_of_education LIKE '%MBA%' OR level_of_education LIKE '%MS%'
                OR level_of_education LIKE '%MA%'
                THEN 'master_degree'

            -- Map doctoral degrees
            WHEN level_of_education LIKE '%PhD%' OR level_of_education LIKE '%Ph.D%'
                OR level_of_education LIKE '%doctorate%' OR level_of_education LIKE '%Doctorate%'
                OR level_of_education LIKE '%doctoral%' OR level_of_education LIKE '%Doctoral%'
                THEN 'doctoral_degree'

            -- Map professional degrees (MD, JD, etc.)
            WHEN level_of_education LIKE '%MD%' OR level_of_education LIKE '%M.D%'
                OR level_of_education LIKE '%Doctor of Medicine%'
                OR level_of_education LIKE '%JD%' OR level_of_education LIKE '%J.D%'
                OR level_of_education LIKE '%PharmD%' OR level_of_education LIKE '%Pharm.D%'
                OR level_of_education LIKE '%DDS%' OR level_of_education LIKE '%DMD%'
                OR level_of_education LIKE '%Residency%' OR level_of_education LIKE '%residency%'
                THEN 'professional_degree'

            -- Map associate degrees
            WHEN level_of_education LIKE '%associate%' OR level_of_education LIKE '%Associate%'
                OR level_of_education LIKE '%AA%' OR level_of_education LIKE '%AS%'
                THEN 'associate_degree'

            -- Map high school
            WHEN level_of_education LIKE '%high school%' OR level_of_education LIKE '%High School%'
                OR level_of_education LIKE '%secondary%' OR level_of_education LIKE '%Secondary%'
                OR level_of_education LIKE '%diploma%' OR level_of_education LIKE '%Diploma%'
                THEN 'high_school'

            -- Map elementary/middle school
            WHEN level_of_education LIKE '%elementary%' OR level_of_education LIKE '%Elementary%'
                OR level_of_education LIKE '%primary%' OR level_of_education LIKE '%Primary%'
                THEN 'elementary_school'

            WHEN level_of_education LIKE '%middle%' OR level_of_education LIKE '%Middle%'
                OR level_of_education LIKE '%junior high%' OR level_of_education LIKE '%Junior High%'
                THEN 'middle_school'

            -- Default to 'other' for unrecognized values or NULL
            ELSE 'other'
        END
        WHERE level_of_education IS NOT NULL OR level_of_education_new IS NULL
    """))

    # Step 3: Set default value for users with NULL education
    connection.execute(sa.text("""
        UPDATE users
        SET level_of_education_new = 'other'
        WHERE level_of_education_new IS NULL
    """))

    # Step 4: Drop the old column and rename the new one
    op.drop_column('users', 'level_of_education')
    op.alter_column('users', 'level_of_education_new', new_column_name='level_of_education')

    # Step 5: Make the column non-nullable now that all data is migrated
    op.alter_column('users', 'level_of_education', nullable=False)

    # Step 6: Update the index
    op.drop_index('idx_users_level_of_education', table_name='users')
    op.create_index('idx_users_level_of_education', 'users', ['level_of_education'])


def downgrade() -> None:
    """
    Revert level_of_education column back to VARCHAR(100).
    """
    connection = op.get_bind()

    # Step 1: Add temporary VARCHAR column
    op.add_column('users', sa.Column('level_of_education_old', sa.String(100), nullable=True))

    # Step 2: Convert ENUM values back to descriptive text
    connection.execute(sa.text("""
        UPDATE users
        SET level_of_education_old = CASE level_of_education
            WHEN 'elementary_school' THEN 'Elementary School'
            WHEN 'middle_school' THEN 'Middle School'
            WHEN 'high_school' THEN 'High School'
            WHEN 'associate_degree' THEN 'Associate Degree'
            WHEN 'bachelor_degree' THEN 'Bachelor Degree'
            WHEN 'master_degree' THEN 'Master Degree'
            WHEN 'doctoral_degree' THEN 'Doctoral Degree'
            WHEN 'professional_degree' THEN 'Professional Degree'
            ELSE 'Other'
        END
    """))

    # Step 3: Drop the ENUM column and rename the VARCHAR column
    op.drop_index('idx_users_level_of_education', table_name='users')
    op.drop_column('users', 'level_of_education')
    op.alter_column('users', 'level_of_education_old', new_column_name='level_of_education')

    # Step 4: Recreate the index
    op.create_index('idx_users_level_of_education', 'users', ['level_of_education'])

    # Step 5: Drop the ENUM type
    sa.Enum(name='education_level_enum').drop(op.get_bind(), checkfirst=True)
