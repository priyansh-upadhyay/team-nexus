from sqlalchemy import Column, Integer, DateTime, func

from app.core.database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    # Timestamps for audit trail
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created (UTC)"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated (UTC)"
    )

    # Future: Add tenant_id for multi-tenant SaaS architecture
    # tenant_id = Column(Integer, nullable=False, index=True)
