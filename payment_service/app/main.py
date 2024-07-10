# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from sqlmodel import Field, Session, SQLModel, select, Sequence
from fastapi import FastAPI, Depends,HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.deps import get_kafka_producer,get_session
from app.models.payment_model import Payment,PaymentUpdate
from app.crud.payment_crud import add_new_payment,delete_payment_by_id,get_all_payments,get_payment_by_id,update_payment_by_id


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    # task = asyncio.create_task(consume_messages(settings.KAFKA_ORDER_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    # servers=[
    #     {
    #         "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
    #         "description": "Development Server"
    #     }
    #     ]
        )



@app.get("/")
def read_root():
    return {"Payment": "Service"}



@app.post("/payments/", response_model=Payment)
def create_new_payment(payment: Payment, session: Annotated[Session, Depends(get_session)]):
    """Create a new payment"""
    payment_data = add_new_payment(payment=payment, session=session)
    return payment_data


@app.get("/payments/", response_model=list[Payment])
def read_payments(session: Annotated[Session, Depends(get_session)]):
    """Get all payments"""
    return get_all_payments(session)


@app.get("/payments/{payment_id}", response_model=Payment)
def read_single_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single payment by ID"""
    try:
        return get_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e


@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, session: Annotated[Session, Depends(get_session)]):
    """Delete a single payment by ID"""
    try:
        return delete_payment_by_id(payment_id=payment_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/payments/{payment_id}", response_model=PaymentUpdate)
def update_payment(payment_id: int, payment: PaymentUpdate, session: Annotated[Session, Depends(get_session)]):
    """Update a single payment by ID"""
    try:
        return update_payment_by_id(payment_id=payment_id, to_update_payment_data=payment, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
