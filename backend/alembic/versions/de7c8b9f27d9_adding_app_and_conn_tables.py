"""adding app and conn tables

Revision ID: de7c8b9f27d9
Revises: 
Create Date: 2024-12-28 15:11:19.368988

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
import agentic_workflow


# revision identifiers, used by Alembic.
revision: str = "de7c8b9f27d9"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "workflows_app",
        sa.Column("createdBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.Column("orgId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("endpointUrl", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("logoUrl", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("auth", agentic_workflow.db.utils.PydanticJSONType(), nullable=True),
        sa.Column("version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id", "version", name="pk_app"),
    )
    op.create_table(
        "workflows_workflow",
        sa.Column("createdBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.Column("orgId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("version", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("steps", agentic_workflow.db.utils.PydanticJSONType(), nullable=True),
        sa.Column("startStepId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("id", "version", name="pk_workflow"),
    )
    op.create_table(
        "workflows_app_action",
        sa.Column("createdBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.Column("orgId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "actionType",
            sa.Enum("TRIGGER", "ACTION", name="appactiontype"),
            nullable=False,
        ),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("dataSchema", agentic_workflow.db.utils.PydanticJSONType(), nullable=False),
        sa.Column("uiSchema", agentic_workflow.db.utils.PydanticJSONType(), nullable=False),
        sa.Column("appId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("appVersion", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["appId", "appVersion"],
            ["workflows_app.id", "workflows_app.version"],
            name="fk_app_id_version",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("appId", "appVersion", "name", name="unique_app_id_version_name"),
    )
    op.create_table(
        "workflows_connection",
        sa.Column("createdBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("createdAt", sa.DateTime(), nullable=False),
        sa.Column("updatedBy", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("updatedAt", sa.DateTime(), nullable=False),
        sa.Column("orgId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("appId", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("appVersion", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("credentials", agentic_workflow.db.utils.PydanticJSONType(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["appId", "appVersion"],
            ["workflows_app.id", "workflows_app.version"],
            name="fk_app_id_version",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("workflows_connection")
    op.drop_table("workflows_app_action")
    op.drop_table("workflows_workflow")
    op.drop_table("workflows_app")
    op.execute("DROP TYPE appactiontype")
    # ### end Alembic commands ###
