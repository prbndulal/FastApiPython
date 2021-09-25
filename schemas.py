from pydantic import BaseModel
from typing import Optional

 

class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]


    class Config:
        orm_mode=True,
        schema_extra={
        'example':{
            "username":"johndoe",
            "email":"johndoe@gmail.com",
            "password":"password",
            "is_staff":False,
            "is_active":True
        }

        }
    
class Settings(BaseModel):
    authjwt_secret_key:str='b9d3db31fe8b3c4a57acfae32fba7654f2657865e38140e2e34eccfeafb847e6'

class LoginModel(BaseModel):
    username:str
    password:str