from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Drugs(Base):
    __tablename__ = 'Drugs'
    DrugID = Column(Integer, primary_key=True)
    DrugName = Column(String(255))
    DrugTypeID = Column(Integer, ForeignKey('DrugTypes.DrugTypeID'))  # Foreign Key to DrugTypes
    ExpiryDate = Column(DateTime)
    
    # Correct back_populates reference to `drugs`
    drug_type = relationship("DrugTypes", back_populates="drugs")
    drug_dosages = relationship("DrugDosages", back_populates="drug", cascade="all, delete-orphan")


class DrugTypes(Base):
    __tablename__ = 'DrugTypes'
    DrugTypeID = Column(Integer, primary_key=True)
    TypeName = Column(String(255))
    
    # Correct relationship name `drugs` (lowercase) to match the back_populates in Drugs
    drugs = relationship("Drugs", back_populates="drug_type")


class DrugDosages(Base):
    __tablename__ = 'DrugDosages'
    DrugDosageID = Column(Integer, primary_key=True)
    DrugID = Column(Integer, ForeignKey('Drugs.DrugID'))  # Foreign Key to Drugs
    DosageFormID = Column(Integer, ForeignKey('DosageForms.DosageFormID'))  # Foreign Key to DosageForms
    Quantity = Column(Integer)

    # Correct relationship name `drug` (lowercase) and `dosage_form`
    drug = relationship("Drugs", back_populates="drug_dosages")
    dosage_form = relationship("DosageForms", back_populates="drug_dosages")


class DosageForms(Base):
    __tablename__ = 'DosageForms'
    DosageFormID = Column(Integer, primary_key=True)
    DosageFormName = Column(String(255))
    Unit = Column(String(255))

    # Correct relationship name `drug_dosages`
    drug_dosages = relationship("DrugDosages", back_populates="dosage_form")
