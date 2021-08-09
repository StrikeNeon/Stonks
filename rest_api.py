import uvicorn
from fastapi import (FastAPI, HTTPException,
                     Depends, status,
                     Response, WebSocket,
                     Request)
from pydantic import BaseModel
from db_utils import MongoManager

app = FastAPI()
db_manager = MongoManager()


class symbol_model(BaseModel):
    symbol_name: str
    candlestick_data: dict
    sma_data: dict
    ema_data: dict
    rsi_data: dict


class client_model(BaseModel):
    username: str
    password: str
    api_key: str
    api_secret: str


@app.post("/add_client")
async def add_client(new_client: client_model):
    added_client = db_manager.register_client(dict(new_client))
    if added_client:
        return {"message": f"{new_client.username} added under id {added_client}"}
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="already registered"
        )

@app.get("/activate_client")
async def activate_client(client: str):
    # TODO login with token here
    result = db_manager.add_client(client)
    if result == 200:
        return Response(status_code=200)
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no client under that username was found"
        )

@app.get("/start_gathering_symbol")
async def start_gathering_symbol(client: str, symbol: str):
    return {"message": f"{symbol} gathering started"}

@app.get("/stop_gathering_symbol")
async def stop_gathering_symbol(client: str, symbol: str):
    return {"message": f"{symbol} gathering stopped"}

@app.get("/init_symbol")
async def init_symbol(symbol: str, client: str):
    init_symbol = db_manager.setup_symbol(symbol, client)
    if init_symbol == 200:
        return Response(status_code=200)
    if init_symbol == 403:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="client isn't activated"
            )

@app.get("/get_current_data")
async def get_current_data(symbol: str):
    return {"message": f"{symbol} data"}


@app.get("/get_current_sma")
async def get_current_sma(symbol: str):
    return {"message": f"{symbol} sma"}


@app.get("/get_current_ema")
async def get_current_ema(symbol: str):
    return {"message": f"{symbol} ema"}


@app.get("/get_current_rsi")
async def get_current_rsi(symbol: str):
    return {"message": f"{symbol} rsi"}


if __name__ == "__main__":
    uvicorn.run("rest_api:app", host="127.0.0.1",
                port=8080, reload=True,
                log_level="info")
