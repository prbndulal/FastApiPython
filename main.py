from typing import Optional
from fastapi import FastAPI

app=FastAPI()



#p@app. is pathoperation decorator 
@app.get('/')# path inside operation
async def index():# path operation function
    return {'data':{'name':'prabin'}}


@app.get('/about')
async def about():
    return {'data':'about page'}