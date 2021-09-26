
from fastapi import APIRouter,Depends,status
from fastapi_jwt_auth import AuthJWT
from models import User,Order
from schemas import OrderModel,OrderStatusModel
from fastapi.exceptions import HTTPException
from database import Session,engine
from fastapi.encoders import jsonable_encoder


order_router = APIRouter(
prefix='/orders',
tags=['orders']

)

session=Session(bind=engine)

"""@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
   
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    return{"message":"hello World"}"""

 
@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel ,Authorize:AuthJWT=Depends()):

    """
        ## Placing an Order API
        Parameters=OrderModelObject:
        - quantity : integer
        - pizza_size: str

        Returns the order object created
    
    """ 
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")

    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    new_order= Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity

    )
    new_order.user=user
    session.add(new_order)
    session.commit()
    response={
        "pizza_size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "id":new_order.id,
        "order_status":new_order.order_status
    }
    return jsonable_encoder(response)


@order_router.get('/orders')
async def list_all_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get All orders
        

        Returns all the orders for all users
    
    """ 
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        orders=session.query(Order).all()
        return jsonable_encoder(orders)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not authorized")


@order_router.get('/orders/{id}')
async def get_order_by_id(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Get an order by its id
        This is an api to get order details by id and only staff can access it
        
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        order=session.query(Order).filter(Order.id==id).first()
        return jsonable_encoder(order)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not allowed to carryout the request")

@order_router.get('/user/orders')
async def get_user_orders(Authorize:AuthJWT=Depends()):
    """
        ## Get all orders for current user
        This is an api to get all order details for current user
        
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()

    return jsonable_encoder(user.orders)

@order_router.get('/user/order/{id}')
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):
    """
        ## Get specific order detail  for current user
        

        Returns oder details of the order id passed for current user
    
    """ 
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    orders=user.orders
    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)


    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No Order found with such id")

@order_router.put('/order/update/{id}')
async def update_order(id:int,order:OrderModel,Authorize:AuthJWT=Depends()):
    """
        ## Updating an order
        id to be passed in query
        This udates an order and requires the following fields to be passed from body
        - quantity : integer
        - pizza_size: str
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    order_to_update=session.query(Order).filter(Order.id==id).first()

    order_to_update.quantity=order.quantity
    order_to_update.pizza_size=order.pizza_size
    session.commit()
    response={
            "quantity":order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status,
            "id":order_to_update.id

        }
    return jsonable_encoder(response)

@order_router.patch('/order/status/{id}')
async def update_order_status(id:int,order:OrderStatusModel, Authorize:AuthJWT=Depends()):

    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in str format
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    current_user=Authorize.get_jwt_subject()
    user=session.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        order_to_update=session.query(Order).filter(Order.id==id).first()
        order_to_update.order_status=order.order_status
        session.commit()
        response={
            "quantity":order_to_update.quantity,
            "pizza_size":order_to_update.pizza_size,
            "order_status":order_to_update.order_status,
            "id":order_to_update.id

        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not allowed to carryout the request")


@order_router.delete('/order/delete/{id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int,Authorize:AuthJWT=Depends()):
    """
        ## Delete an Order
        This deletes an order by its ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    
    order_to_delete =session.query(Order).filter(Order.id==id).first()
    
    session.delete(order_to_delete)
    
    session.commit()
    return order_to_delete






