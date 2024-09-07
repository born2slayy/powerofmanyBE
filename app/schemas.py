from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

# Creator 스키마
class CreatorBase(BaseModel):
    creatorName: str
    emailName: EmailStr
    birthDate: date
    phoneNum: str
    userId: str
    userPwd: str

class CreatorCreate(CreatorBase):
    pass

class Creator(CreatorBase):
    id: int
    unions: List['Union'] = []  # Union과의 관계를 포함

    class Config:
        orm_mode = True

class CreatorResponse(BaseModel):
    creatorName: str
    emailName: EmailStr
    birthDate: date
    phoneNum: str
    userId: str
    
# Union 스키마
class UnionBase(BaseModel):
    unionName: str
    whatWeDo: Optional[str] = None
    missionStatement: Optional[str] = None
    signedCount: Optional[int] = 0
    qrCodeLink: Optional[str] = None

class UnionCreate(UnionBase): 
    unionName: str
    whatWeDo: str
    missionStatement: str
    qrCodeLink: Optional[str]

class Union(UnionBase):
    id: int
    creator: Creator  # Creator와의 관계를 포함

    class Config:
        orm_mode = True
        
class UnionByCreatorResponse(BaseModel):
    unionName: str
    qrCodeLink: str
    signedCount: int
    checkProfilesTF: bool = False

class UnionByCreatorResponseList(BaseModel):
    unions : List[UnionByCreatorResponse]

class UnionResponse(BaseModel):
    unionName: str
    qrCodeLink: str
    signedCount: int
    
# NonUser 스키마
class NonUserBase(BaseModel):
    nonUserName: str
    employeeId: str
    jobTitle: str
    department: str
    nonUserEmail: EmailStr
    nonUserphoneNum: str

class NonUserCreate(NonUserBase):
    registered_union_id: int  

class NonUser(NonUserBase):
    id: int

    class Config:
        orm_mode = True
