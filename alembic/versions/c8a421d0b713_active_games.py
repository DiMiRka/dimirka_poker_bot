from alembic import op
import sqlalchemy as sa


revision = 'c8a421d0b713'
down_revision = 'b665d476ea2a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'active_games',
        sa.Column('chat_id', sa.BigInteger(), primary_key=True),
        sa.Column('state', sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('active_games')
