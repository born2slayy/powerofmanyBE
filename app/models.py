from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Creator(Base):
    __tablename__ = 'creators'

    id = Column(Integer, primary_key=True, index=True)
    creatorName = Column(String(255), nullable=False)
    emailName = Column(String(255), unique=True, nullable=False)
    birthDate = Column(Date, nullable=False)
    phoneNum = Column(String(255), nullable=False)
    userId = Column(String(255), unique=True, nullable=False)
    userPwd = Column(String(255), nullable=False)

    unions = relationship("Union", back_populates="creator")  # 다대일 관계

class Union(Base):
    __tablename__ = 'unions'

    id = Column(Integer, primary_key=True, index=True)
    unionName = Column(String(255), index=True, nullable=False)
    whatWeDo = Column(String(255))
    missionStatement = Column(String(255))
    signedCount = Column(Integer)
    qrCodeLink = Column(String(255))

    creator_id = Column(Integer, ForeignKey('creators.id'), nullable=False)  # 외래 키 추가
    creator = relationship("Creator", back_populates="unions")

class NonUser(Base):
    __tablename__ = 'non_users'

    id = Column(Integer, primary_key=True, index=True)
    nonUserName = Column(String(255), nullable=False)
    employeeId = Column(String(255), nullable=False)
    jobTitle = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    nonUserEmail = Column(String(255), nullable=False)
    nonUserphoneNum = Column(String(255), nullable=False)
    registered_union_id = Column(Integer, ForeignKey('unions.id'))
