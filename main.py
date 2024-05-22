from fastapi import FastAPI, HTTPException, Depends, Request

from pydantic import BaseModel, EmailStr, Field, ValidationError
from sqlalchemy import create_engine, Column, Integer, String, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import smtplib
from email.mime.text import MIMEText
from typing import List, Optional
from datetime import date

DATABASE_URL = 'postgresql://postgres:root@34.47.8.24/test1'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# Define your database models
class Project1UserDB(Base):
    __tablename__ = "project1_users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    f_name = Column(String, nullable=False)
    l_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Project2UserDB(Base):
    __tablename__ = "project2_users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    mobile_num = Column(String, unique=True, nullable=False)
    f_name = Column(String, nullable=False)
    l_name = Column(String, nullable=False)
    hashtag = Column(String, nullable=False)

class Project3UserDB(Base):
    __tablename__ = "project3_users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True, index=True)
    mobile = Column(String, unique=True, nullable=False)
    f_name = Column(String, nullable=False)
    l_name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    
class UserProject(Base):
    __tablename__ = "user_projects"
    id = Column(Integer, Sequence('user_project_id_seq'), primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    project_id = Column(Integer, nullable=False)
Base.metadata.create_all(bind=engine)

# Pydantic models for request validation
class Project1User(BaseModel):
    company_name: str
    f_name: str
    l_name: str
    email: EmailStr
    password: str

class Project2User(BaseModel):
    mobile_num: str
    f_name: str
    l_name: str
    hashtag: str

class Project3User(BaseModel):
    mobile: str
    f_name: str
    l_name: str
    dob: date

class UserRequest(BaseModel):
    data: dict

# Dependency for database session
def get_session_local():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to add users for different projects
@app.post("/add_user/")
async def add_user(user_request: UserRequest, db: Session = Depends(get_session_local)):
    print(user_request.data)
    try:
        if user_request.data['project_id'] == 1:
            user_data = Project1User(**user_request.data)
            db_user = Project1UserDB(
                company_name=user_data.company_name,
                f_name=user_data.f_name,
                l_name=user_data.l_name,
                email=user_data.email,
                password=user_data.password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            id = db_user.id
            user_Map_data = UserProject(user_id = id, project_id = 1)
            db.add(user_Map_data)
            db.commit()
            db.refresh(user_Map_data)
            return {"status": "success", "project": 1, "data": user_data}

        elif user_request.data['project_id'] == 2:
            user_data = Project2User(**user_request.data)
            db_user = Project2UserDB(
                mobile_num=user_data.mobile_num,
                f_name=user_data.f_name,
                l_name=user_data.l_name,
                hashtag=user_data.hashtag
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            id = db_user.id
            user_Map_data = UserProject(user_id = id, project_id = 2)
            db.add(user_Map_data)
            db.commit()
            db.refresh(user_Map_data)
            return {"status": "success", "project": 2, "data": user_data}

        elif user_request.data['project_id'] == 3:
            user_data = Project3User(**user_request.data)
            db_user = Project3UserDB(
                mobile=user_data.mobile,
                f_name=user_data.f_name,
                l_name=user_data.l_name,
                dob=user_data.dob
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            id = db_user.id
            user_Map_data = UserProject(user_id = id, project_id = 3)
            db.add(user_Map_data)
            db.commit()
            db.refresh(user_Map_data)
            return {"status": "success", "project": 3, "data": user_data}

        else:
            raise HTTPException(status_code=400, detail="Invalid project_id")

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

# CRUD Endpoints
@app.get("/get_users", response_model=List[UserRequest])
def get_users(db: Session = Depends(get_session_local)):
    users_project1 = db.query(Project1UserDB).all()
    users_project2 = db.query(Project2UserDB).all()
    users_project3 = db.query(Project3UserDB).all()

    users = []

    # Convert Project1UserDB objects to UserRequest objects
    for user in users_project1:
        user_data = {
            
               "data" :{
                "id": user.id,
                "company_name": user.company_name,
                "f_name": user.f_name,
                "l_name": user.l_name,
                "email": user.email,
                "password": user.password
               }
            
        }
        users.append(UserRequest(**user_data))

    # Convert Project2UserDB objects to UserRequest objects
    for user in users_project2:
        user_data = {
                "data" :{
                "id": user.id,
                "mobile_num": user.mobile_num,
                "f_name": user.f_name,
                "l_name": user.l_name,
                "hashtag": user.hashtag
                }
        }
        users.append(UserRequest(**user_data))

    # Convert Project3UserDB objects to UserRequest objects
    for user in users_project3:
        user_data = {
            "data" :{
                "id": user.id,
                "mobile": user.mobile,
                "f_name": user.f_name,
                "l_name": user.l_name,
                "dob": user.dob
            }
        }
        users.append(UserRequest(**user_data))

    return users

@app.patch("/update_user/{user_id}", response_model=UserRequest)
def update_user(user_id: int, user: UserRequest, db: Session = Depends(get_session_local)):
    project_id  = db.query(UserProject).filter(UserProject.user_id == user_id).first().project_id
    if project_id == 1:
        db_user = db.query(Project1UserDB).filter(Project1UserDB.id == user_id).first()
    elif project_id == 2:
        db_user = db.query(Project2UserDB).filter(Project2UserDB.id == user_id).first()
    elif project_id == 3:
        db_user = db.query(Project3UserDB).filter(Project3UserDB.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user.data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return user

@app.delete("/delete_user/{user_id}", response_model=dict)
def delete_user(user_id: int,db: Session = Depends(get_session_local)):

    if db.query(UserProject).filter(UserProject.user_id == user_id).first() is None:
        raise HTTPException(status_code=404, detail="User not found")
    project_id  = db.query(UserProject).filter(UserProject.user_id == user_id).first().project_id
    if project_id == 1:
        db_user = db.query(Project1UserDB).filter(Project1UserDB.id == user_id).first()
    elif project_id == 2:
        db_user = db.query(Project2UserDB).filter(Project2UserDB.id == user_id).first()
    elif project_id == 3:
        db_user = db.query(Project3UserDB).filter(Project3UserDB.id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid project_id")

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

@app.post("/send_invite")
def send_invite():
    msg = MIMEText("Please check the API documentation at /docs")
    msg["Subject"] = "API Documentation Link"
    msg["From"] = "student.gec416@gmail.com"
    msg["To"] = "shraddha@aviato.consulting, pooja@aviato.consulting"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("student.gec416@gmail.com", "tsnf vdnu jnpo fbiy")
            server.sendmail(msg["From"], msg["To"].split(", "), msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"detail": "Invitation sent"}
