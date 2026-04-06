"""add stimuli reporting tables

Revision ID: 20260406_0002
Revises: 20260406_0001
Create Date: 2026-04-06 00:30:00

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260406_0002"
down_revision = "20260406_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stimuli",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(length=500), nullable=False),
        sa.Column("insight", sa.String(length=2000), nullable=False),
        sa.Column("source_text", sa.String(length=10000), nullable=False),
        sa.Column("flagged_for_review", sa.Boolean(), nullable=False),
        sa.Column("report_reason", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("flagged_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stimuli_id"), "stimuli", ["id"], unique=False)
    op.create_index(op.f("ix_stimuli_user_id"), "stimuli", ["user_id"], unique=False)

    op.create_table(
        "admin_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("stimulus_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["stimulus_id"], ["stimuli.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_notifications_id"), "admin_notifications", ["id"], unique=False)
    op.create_index(op.f("ix_admin_notifications_stimulus_id"), "admin_notifications", ["stimulus_id"], unique=False)
    op.create_index(op.f("ix_admin_notifications_user_id"), "admin_notifications", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_notifications_user_id"), table_name="admin_notifications")
    op.drop_index(op.f("ix_admin_notifications_stimulus_id"), table_name="admin_notifications")
    op.drop_index(op.f("ix_admin_notifications_id"), table_name="admin_notifications")
    op.drop_table("admin_notifications")

    op.drop_index(op.f("ix_stimuli_user_id"), table_name="stimuli")
    op.drop_index(op.f("ix_stimuli_id"), table_name="stimuli")
    op.drop_table("stimuli")
