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
 

auth_router = APIRouter(
prefix='/auth',
tags=['auths']

)

session=Session(bind=engine)

 
 

"""@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    return {"message":"Hello World"}
    """
     

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
    """     
        ## User Login Api
        Arguments
            ```
                username:str
                password:str
            ```
        and returns a token pair `access_token` and `refresh_token`
    """
    db_user=session.query(User).filter(User.username==user.username).first()
    if db_user and check_password_hash(db_user.password, user.password):
        access_token=Authorize.create_access_token(subject=db_user.username)
        refresh_token=Authorize.create_refresh_token(subject=db_user.username)
        response={
            "access_token":access_token,
            "refresh_token":refresh_token
        }
        return  jsonable_encoder(response)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Username or Password")

    #refresh_token 
@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    """     
        ## Create New Token from Refresh TOken
        This requires refresh token passed in header and returns fresh token in acces_token
    """
    try:
        Authorize.jwt_refresh_token_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED
        , detail="Please provide valid refresh token"
        
        )
    
    current_user=Authorize.get_jwt_subject()

    access_token=Authorize.create_access_token(subject=current_user)

    return jsonable_encoder({"access_token":access_token})


   


