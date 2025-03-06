from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import date, timedelta
import random

# Database setup
DATABASE_URL = "sqlite:///./workday_poc.db"  # Replace with PostgreSQL for production
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)
    salary = Column(Float)
    hire_date = Column(Date, default=date.today)

class Payroll(Base):
    __tablename__ = "payroll"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    salary_paid = Column(Float)
    tax_deduction = Column(Float)
    date_paid = Column(Date, default=date.today)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Employee Management Endpoints
@app.post("/employees/")
def create_employee(name: str, role: str, salary: float, db: Session = Depends(get_db)):
    employee = Employee(name=name, role=role, salary=salary)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

@app.get("/employees/")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()

@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted"}

# Payroll Automation Endpoint
@app.post("/payroll/{employee_id}")
def process_payroll(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    tax = employee.salary * 0.15  # Assuming 15% tax deduction
    net_salary = employee.salary - tax
    payroll_entry = Payroll(employee_id=employee.id, salary_paid=net_salary, tax_deduction=tax)
    db.add(payroll_entry)
    db.commit()
    return {"employee": employee.name, "salary_paid": net_salary, "tax_deducted": tax}

# AI-Driven Payroll Prediction (Simple Trend-Based Estimate)
@app.get("/payroll/predict")
def predict_next_month_payroll(db: Session = Depends(get_db)):
    total_salaries = db.query(func.sum(Employee.salary)).scalar() or 0
    expected_growth = random.uniform(1.02, 1.05)  # Simulating payroll increase
    predicted_payroll = total_salaries * expected_growth
    return {"predicted_next_month_payroll": round(predicted_payroll, 2)}

# Run the app with: uvicorn filename:app --reload
