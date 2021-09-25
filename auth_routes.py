from fastapi import APIRouter,status,Depends
from database import Session,engine
from schemas import SignUpModel,LoginModel
from models import User
from fastapi.exceptions import HTTPException
from werkzeug.security import generate_password_hash,check_password_hash
from fastapi.encoders import jsonable_encoder
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schemas import Settings
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

auth_router = APIRouter(
prefix='/auth',
tags=['auths']

)

session=Session(bind=engine)

SECRET_KEY='09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM='HS256'

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@auth_router.post('/token')
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user=session.query(User).filter(User.username==form_data.username).first()
    if db_user and check_password_hash(db_user.password, form_data.password):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token=create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
        return {'access_token' :  access_token}


@auth_router.get('/')
async def hello(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
    except JWTError:
        raise credentials_exception
    return {"message":"Hello World"}
     

@auth_router.post('/signup',
    status_code=status.HTTP_201_CREATED#,response_model=SignUpModel
)
async def signup(user:SignUpModel):
    """
        ## Create a user
        This requires the following
        ```
                username:int
                email:str
                password:str
                is_staff:bool
                is_active:bool
        ```
    
    """


    db_email=session.query(User).filter(User.email==user.email).first()

    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the email already exists"
        )

    db_username=session.query(User).filter(User.username==user.username).first()

    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with the username already exists"
        )

    new_user=User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff
    )

    session.add(new_user)
    session.commit()

    return new_user

#login route
@auth_router.post('/login',status_code=200)
async def login(user:LoginModel,Authorize:AuthJWT=Depends()):
    db_user=session.query(User).filter(User.username==user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_token=Authorize.create_access_token(subject=db_user.username)
        refresh_token=Authorize.create_refresh_token(subject=db_user.username)
        response={
            "acces_token":access_token,
            "refresh_token":refresh_token
        }
        return  jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Username or Password")


