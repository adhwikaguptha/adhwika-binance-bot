# src/db.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Sequence
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Utility to create human-friendly IDs like user001, order001
def _format_id(prefix: str, num: int, width: int = 3) -> str:
    return f"{prefix}{str(num).zfill(width)}"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, index=True)  # e.g., user001
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderRecord(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, index=True)      # order001
    user_id = Column(String, index=True)                    # user001
    symbol = Column(String, index=True)
    side = Column(String)
    price = Column(Float, nullable=True)
    quantity = Column(Float)
    params = Column(JSON)
    result = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True)
    signal_id = Column(String, unique=True, index=True)     # signal001
    user_id = Column(String, index=True)
    name = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

# helper functions for id creation and user management
def get_or_create_user(db, username: str):
    u = db.query(User).filter(User.name == username).first()
    if u:
        return u
    # create next user id
    last = db.query(User).order_by(User.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    user_id = _format_id("user", next_num)
    u = User(user_id=user_id, name=username)
    db.add(u); db.commit(); db.refresh(u)
    return u

def create_order_record(db, user_id: str, symbol: str, side: str, price: float, quantity: float, params: dict, result: dict, status: str):
    last = db.query(OrderRecord).order_by(OrderRecord.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    order_id = _format_id("order", next_num)
    rec = OrderRecord(order_id=order_id, user_id=user_id, symbol=symbol, side=side, price=price, quantity=quantity, params=params, result=result, status=status)
    db.add(rec); db.commit(); db.refresh(rec)
    return rec

def create_signal_record(db, user_id: str, name: str, payload: dict):
    last = db.query(Signal).order_by(Signal.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    signal_id = _format_id("signal", next_num)
    rec = Signal(signal_id=signal_id, user_id=user_id, name=name, payload=payload)
    db.add(rec); db.commit(); db.refresh(rec)
    return rec
