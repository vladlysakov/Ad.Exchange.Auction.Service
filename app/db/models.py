from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    pass


supply_bidder = Table(
    'supply_bidder',
    Base.metadata,
    Column('supply_id', String, ForeignKey('supplies.id', ondelete='CASCADE'), primary_key=True),
    Column('bidder_id', String, ForeignKey('bidders.id', ondelete='CASCADE'), primary_key=True)
)


class Supply(Base):
    __tablename__ = 'supplies'
    
    id = Column(String, primary_key=True, index=True)
    bidders = relationship("Bidder", secondary=supply_bidder, back_populates="supplies")


class Bidder(Base):
    __tablename__ = 'bidders'
    
    id = Column(String, primary_key=True, index=True)
    country = Column(String, nullable=False, index=True)
    supplies = relationship("Supply", secondary=supply_bidder, back_populates="bidders")
