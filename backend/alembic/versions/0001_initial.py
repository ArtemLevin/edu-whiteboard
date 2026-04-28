"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-28
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    attempt_status = postgresql.ENUM("draft", "submitted", "checked", name="attempt_status")
    attempt_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "exercises",
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("subject", sa.String(length=100), nullable=False),
        sa.Column("topic", sa.String(length=100), nullable=False),
        sa.Column("difficulty", sa.String(length=50), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "solution_attempts",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("board_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", attempt_status, nullable=False),
        sa.Column("teacher_comment", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_solution_attempts_exercise_id"), "solution_attempts", ["exercise_id"])
    op.create_index(op.f("ix_solution_attempts_user_id"), "solution_attempts", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_solution_attempts_user_id"), table_name="solution_attempts")
    op.drop_index(op.f("ix_solution_attempts_exercise_id"), table_name="solution_attempts")
    op.drop_table("solution_attempts")
    op.drop_table("exercises")
    postgresql.ENUM(name="attempt_status").drop(op.get_bind(), checkfirst=True)
