"""add inventory quantity non-negative check

Revision ID: 12e78ecc63c0
Revises: 176c251d053f
Create Date: 2026-07-02 00:00:10.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "12e78ecc63c0"
down_revision: Union[str, Sequence[str], None] = "176c251d053f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_inventories_quantity_non_negative",
        "inventories",
        "quantity >= 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_inventories_quantity_non_negative",
        "inventories",
        type_="check",
    )
