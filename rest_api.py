import uvicorn
from fastapi import (FastAPI, HTTPException,
                     Depends, status,
                     Response, WebSocket,
                     Request)
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from db_utils import MongoManager
from background_tasks import data_gathering_task, stop_data_gathering

app = FastAPI()
db_manager = MongoManager()


class client_model(BaseModel):
    username: str
    password: str
    api_key: str
    api_secret: str


@app.post("/add_client", response_class=ORJSONResponse)
async def add_client(new_client: client_model):
    added_client = db_manager.register_client(dict(new_client))
    if added_client:
        return {"message": f"{new_client.username} added"}
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="already registered"
        )


@app.get("/activate_client", response_class=ORJSONResponse)
async def activate_client(client: str, password: str):
    # TODO login with token here
    result = db_manager.add_client(client, password)
    if result == 200:
        return Response(status_code=200)
    elif result == 404:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no client under that username was found"
            )
    elif result == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="login or password incorrect"
        )


@app.get("/start_gathering_symbol", response_class=ORJSONResponse)
async def start_gathering_symbol(symbol: str, client: str, password: str, minute_interval: int):
    gather_task = data_gathering_task.delay(symbol, client, password, minute_interval)
    return {"message": f"{symbol} gathering started", "task_id": gather_task.id}


@app.get("/stop_gathering_symbol", response_class=ORJSONResponse)
async def stop_gathering_symbol(task_id: str):
    stop_data_gathering(task_id)
    return {"message": f"{task_id} gathering stopped"}


@app.get("/init_symbol", response_class=ORJSONResponse)
async def init_symbol(symbol: str, client: str):
    init_symbol = db_manager.setup_symbol(symbol, client)
    if init_symbol == 200:
        return Response(status_code=200)
    if init_symbol == 403:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="client isn't activated"
            )


@app.get("/get_current_data", response_class=ORJSONResponse)
async def get_current_data(symbol: str):
    current_candlestick = db_manager.get_current_data(symbol)
    if current_candlestick == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    else:
        return {"message": f"{symbol} found", "data": current_candlestick}


@app.get("/get_current_sma", response_class=ORJSONResponse)
async def get_current_sma(symbol: str):
    current_sma = db_manager.recount_sma(symbol)
    if current_sma == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    else:
        return {"message": f"{symbol} sma recounted", "data": current_sma}


@app.get("/get_current_ema", response_class=ORJSONResponse)
async def get_current_ema(symbol: str):
    current_ema = db_manager.recount_ema(symbol)
    if current_ema == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    else:
        return {"message": f"{symbol} ema recounted", "data": current_ema}


@app.get("/get_current_rsi", response_class=ORJSONResponse)
async def get_current_rsi(symbol: str):
    current_rsi = db_manager.recount_rsi(symbol)
    if current_rsi == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    else:
        return {"message": f"{symbol} rsi recounted", "data": current_rsi}


if __name__ == "__main__":
    uvicorn.run("rest_api:app", host="127.0.0.1",
                port=8080, reload=True,
                log_level="info")
