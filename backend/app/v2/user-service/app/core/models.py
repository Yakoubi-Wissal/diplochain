from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime,
    ForeignKey, func
)
from sqlalchemy.orm import relationship

from core.database import Base


class Role(Base):
    __tablename__ = "ROLE"  # matches init.sql uppercase

    id_role = Column(Integer, primary_key=True, autoincrement=True)
    label_role = Column(String(100))
    code = Column(String(255), nullable=False, unique=True)
    id_cursus = Column(Integer)

    user_roles = relationship("UserRole", back_populates="role")


class User(Base):
    __tablename__ = "User"  # quoted name in init.sql

    id_user = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255))
    password = Column(String(120))
    token = Column(String(255))
    tokentype = Column(String(50))
    revoked = Column(Boolean)
    expired = Column(Boolean)
    email = Column(String(255), unique=True)
    reset_code = Column(String(255))
    tokentype = Column(String(50))
    verificationtoken_expiration = Column(DateTime)
    reset_code_expiration = Column(DateTime)
    verification_token = Column(String(255), unique=True)
    status = Column(String(255))

    roles = relationship("UserRole", back_populates="user")


class UserRole(Base):
    __tablename__ = "UserRole"  # matches init.sql

    user_id = Column(Integer, ForeignKey("User.id_user"), primary_key=True)
    role_id = Column(Integer, ForeignKey("ROLE.id_role"), primary_key=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
