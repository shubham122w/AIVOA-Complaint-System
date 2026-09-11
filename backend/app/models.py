from sqlalchemy import Column, Integer, String, Text, Date
from app.database.connection import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    complaint_source = Column(String(100))
    customer_name = Column(String(255))

    product_name = Column(String(255))
    product_strength = Column(String(100))
    batch_number = Column(String(100))

    manufacturing_date = Column(Date)
    expiry_date = Column(Date)
    quantity_affected = Column(String(50))

    complaint_type = Column(String(100))
    complaint_date = Column(Date)
    detailed_description = Column(Text)

    initial_severity = Column(String(50))
    priority = Column(String(50))

    ai_risk_assessment = Column(String(50))