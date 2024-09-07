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

#show existing unions (unionName, qrcodelink, signCOunt, checkprofileTF)
@router.get("/unions/read/{creator_id}", response_model=schemas.UnionByCreatorResponseList)
def read_unions_by_creators(creator_id: int, db: Session = Depends(get_db)):
    unions = db.query(models.Union).filter(models.Union.creator_id == creator_id).all()

    union_list = [
        schemas.UnionByCreatorResponse(
            unionName=union.unionName,
            qrCodeLink=union.qrCodeLink,
            signedCount=union.signedCount if union.signedCount is not None else 0,  
            checkProfileTF=(union.signedCount is not None and union.signedCount >= 10)  
        )
        for union in unions
            
    ]

    return schemas.UnionByCreatorResponseList(unions=union_list)


# #about unions
# @router.get("unions/{unionName}", response_model=schemas.)
# def read_unions_by_qr():
    
# #non user signing page (name, employeeId, jobtitle, department, email, phonenum) signcount +1
# @router.post("sign/{union_name}")
# def nonuser_signing():

# #checkprofile if more than 10 show all info 
# def check_profiles():
    
# #








# @router.get("/unions/{creator_id}", response_model=schemas.UnionByCreatorResponse)
# def read_unions_by_creator_id(creator_id: int, db: Session = Depends(get_db)):
    










