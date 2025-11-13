"""alerts tables

Revision ID: bfc7126016e6
Revises: d5911dba4b45
Create Date: 2025-11-12 15:20:54.087999
"""
from alembic import op
import sqlalchemy as sa

revision = "bfc7126016e6"
down_revision = "d5911dba4b45"
branch_labels = None
depends_on = None

def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return name in insp.get_table_names()

def upgrade():
    if _table_exists("alert_deliveries"):
        op.drop_table("alert_deliveries")

    with op.batch_alter_table("alerts", schema=None) as batch_op:
        # add column if missing
        cols = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("alerts")}
        if "source_report_id" not in cols:
            batch_op.add_column(sa.Column("source_report_id", sa.Integer(), nullable=True))

        # widen title
        batch_op.alter_column(
            "title",
            existing_type=sa.VARCHAR(length=140),
            type_=sa.String(length=200),
            existing_nullable=True,
        )

        batch_op.create_foreign_key(
            "fk_alerts_source_report",                
            "student_incident_reports",
            ["source_report_id"],
            ["id"],
        )

        if "report_id" in cols:
            batch_op.drop_column("report_id")

def downgrade():
    with op.batch_alter_table("alerts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("report_id", sa.INTEGER(), nullable=True))
        batch_op.drop_constraint("fk_alerts_source_report", type_="foreignkey")

        batch_op.alter_column(
            "title",
            existing_type=sa.String(length=200),
            type_=sa.VARCHAR(length=140),
            existing_nullable=True,
        )

        batch_op.drop_column("source_report_id")

    op.create_table(
        "alert_deliveries",
        sa.Column("id", sa.INTEGER(), primary_key=True, nullable=False),
        sa.Column("alert_id", sa.INTEGER(), nullable=False),
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("delivered_at", sa.DATETIME(), nullable=False),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], name="fk_alert_deliveries_alert"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_alert_deliveries_user"),
    )
