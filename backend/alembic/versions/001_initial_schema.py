"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-10-16 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=True),
        sa.Column('claude_process_pid', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('CREATED', 'CONNECTING', 'ACTIVE', 'DISCONNECTED', 'RECONNECTING', 'IDLE', 'ENDED', name='sessionstatus'), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('connection_id', sa.String(100), nullable=True),
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id'), nullable=False, index=True),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='messagerole'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.Enum('TEXT', 'CODE', 'ERROR', 'JSON', 'MARKDOWN', name='messagecontenttype'), nullable=False, server_default='TEXT'),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('is_streamed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id'), nullable=True),
    )
    op.create_index('idx_message_session_sequence', 'messages', ['session_id', 'sequence_number'])

    # Create claude_processes table
    op.create_table(
        'claude_processes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id'), nullable=False, unique=True),
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_heartbeat', sa.DateTime(), nullable=False, server_default=sa.text('now()'), index=True),
        sa.Column('status', sa.Enum('STARTING', 'RUNNING', 'UNHEALTHY', 'CRASHED', 'STOPPED', name='processstatus'), nullable=False, server_default='STARTING', index=True),
        sa.Column('working_directory', sa.String(500), nullable=False),
        sa.Column('environment_vars', postgresql.JSONB(), nullable=True),
        sa.Column('restart_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
    )


def downgrade() -> None:
    op.drop_table('claude_processes')
    op.drop_table('messages')
    op.drop_table('sessions')
    op.drop_table('users')

    op.execute('DROP TYPE IF EXISTS processstatus')
    op.execute('DROP TYPE IF EXISTS messagecontenttype')
    op.execute('DROP TYPE IF EXISTS messagerole')
    op.execute('DROP TYPE IF EXISTS sessionstatus')
