from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from . import models, schemas, database
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/creators/register", response_model=schemas.Creator)
def create_creator(creator: schemas.CreatorCreate, db: Session = Depends(get_db)):
    existing_creator = db.query(models.Creator).filter(
        (models.Creator.emailName == creator.emailName) | 
        (models.Creator.userId == creator.userId)
    ).first()
    
    if existing_creator:
        raise HTTPException(status_code=400, detail="Email or User ID already registered")
    
    hashed_password = hash_password(creator.userPwd)
    creator_data = models.Creator(**creator.dict(exclude={"userPwd"}), userPwd=hashed_password)

    db.add(creator_data)
    db.commit()
    db.refresh(creator_data)
    
    return creator_data

@router.post("/creators/login", response_model=schemas.CreatorResponse)
def login_creator(userId: str, userPwd: str, db: Session = Depends(get_db)):
    creator = db.query(models.Creator).filter(models.Creator.userId == userId).first()

    if not creator or not pwd_context.verify(userPwd, creator.userPwd):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return creator

@router.post("/unions/create/{creator_id}", response_model=schemas.UnionResponse)
def create_union(creator_id: int, union: schemas.UnionCreate, db: Session = Depends(get_db)):
    union_data = models.Union(**union.dict(), creator_id=creator_id)

    db.add(union_data)
    db.commit()
    db.refresh(union_data)

    return union_data


@router.get("/unions/create/{creator_id}", response_model=schemas.UnionResponse)
def create_union(creator_id: int, union: schemas.UnionCreate, db: Session = Depends(get_db)):
    union_data = models.Union(**union.dict(), creator_id=creator_id)

    db.add(union_data)
    db.commit()
    db.refresh(union_data)

    return union_data






# @router.get("/unions/{creator_id}", response_model=schemas.UnionByCreatorResponse)
# def read_unions_by_creator_id(creator_id: int, db: Session = Depends(get_db)):
    










