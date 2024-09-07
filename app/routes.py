from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from . import models, schemas, database, llm
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

@router.post("/creators/login", response_model=schemas.CreatorIdResponse)
def login_creator(userId: str, userPwd: str, db: Session = Depends(get_db)):
    creator = db.query(models.Creator).filter(models.Creator.userId == userId).first()

    if not creator or not pwd_context.verify(userPwd, creator.userPwd):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return schemas.CreatorIdResponse(userId=creator.userId, creator_id=creator.id)

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
    for union in unions:
        print(f'union.signedCount: {union.signedCount}')
        print(type(union.signedCount))
        checkProfileTF=(union.signedCount >= 10)
        print(f'checkProfileTF: {checkProfileTF}')
        


    union_list = [
        schemas.UnionByCreatorResponse(
            unionName=union.unionName,
            qrCodeLink=union.qrCodeLink,
            signedCount=union.signedCount,
            checkProfilesTF=(union.signedCount >= 10)
        )
        for union in unions
            
    ]
    return schemas.UnionByCreatorResponseList(unions=union_list)


#about unions (qr)
@router.get("/unions/{unionName}", response_model=List[schemas.UnionByCreatorResponse])
def read_unions_by_qr(unionName: str, db: Session = Depends(get_db)):

    unions = db.query(models.Union).filter(models.Union.unionName == unionName).all()
    
    if not unions:
        raise HTTPException(status_code=404, detail="No unions found with this name")

    return [schemas.UnionByCreatorResponse(
        unionName=union.unionName,
        qrCodeLink=union.qrCodeLink,
        signedCount=union.signedCount,
        checkProfilesTF=(union.signedCount >= 10)  
    ) for union in unions]
    
#non user signing page (name, employeeId, jobtitle, department, email, phonenum) signcount +1
@router.post("/sign/{union_name}")
def nonuser_signing(union_name: str, non_user: schemas.NonUserBase, db: Session = Depends(get_db)):
    union = db.query(models.Union).filter(models.Union.unionName == union_name).first()

    if not union:
        raise HTTPException(status_code=404, detail="Union not found")

    new_non_user = models.NonUser(  
        nonUserName=non_user.nonUserName,
        employeeId=non_user.employeeId,
        jobTitle=non_user.jobTitle,
        department=non_user.department,
        nonUserEmail=non_user.nonUserEmail,
        nonUserPhoneNum=non_user.nonUserPhoneNum,
        registered_union_id=union.id 
    )

    db.add(new_non_user)
    db.commit()
    db.refresh(new_non_user)

    union.signedCount += 1
    db.commit()

    return {"message": "Successfully signed", "unionName": union.unionName, "signedCount": union.signedCount}


#check nonuser list if more than 10 show all info 
@router.get("/nonUserList/{union_name}")
def check_profiles(union_name: str, db: Session = Depends(get_db)):

    union = db.query(models.Union).filter(models.Union.unionName == union_name).first()

    if not union:
        raise HTTPException(status_code=404, detail="Union not found.")

    # if union.signedCount < 10:
    #     raise HTTPException(status_code=404, detail="Union signed count is less than 10.")

    print(f"Union ID: {union.id}")

    non_users = db.query(models.NonUser).filter(models.NonUser.registered_union_id == union.id).all()
    
    if not non_users:
        print('-------------------------')

    return non_users  

@router.post("/chatbot")
def union_chatbot(request: schemas.ChatRequest):
    try:
        response = llm.generate_response(request.input)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))