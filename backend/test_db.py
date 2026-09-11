from app.database.connection import engine, Base
from app.models import Complaint

Base.metadata.create_all(bind=engine)

print("Complaints table created successfully!")