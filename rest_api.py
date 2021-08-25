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


class order_model(BaseModel):
    client: str
    symbol: str
    quantity: float
    price: float
    op_code: int


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

@app.get("/account_status", response_class=ORJSONResponse)
async def get_account_status(client: str):
    status_data, trade_status_data = db_manager.account_status(client)
    if status_data == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="login or password incorrect"
        )
    return {"message": f"{client} data retrieved",
            "status data": status_data,
            "trade status data": trade_status_data}

@app.get("/start_gathering_symbol", response_class=ORJSONResponse)
async def start_gathering_symbol(symbol: str, client: str, password: str, minute_interval: int):
    # TODO login with token here?
    # TODO add latest active task to current data task
    # This is a crutch, client activation (db_manager.add_client) should be a separate endpoint
    # and this should verify token, but celery doesn't detect changes in active clients
    # though binance care about ips and not connections
    gather_task = data_gathering_task.delay(symbol, client, password, minute_interval)
    return {"message": f"{symbol} gathering started", "task_id": gather_task.id}


@app.get("/stop_gathering_symbol", response_class=ORJSONResponse)
async def stop_gathering_symbol(task_id: str):
    stop_data_gathering(task_id)
    return {"message": f"{task_id} gathering stopped"}


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


@app.get("/get_current_bbands", response_class=ORJSONResponse)
async def get_current_sma(symbol: str):
    current_bbands = db_manager.recount_bbands(symbol)
    if current_bbands == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    else:
        return {"message": f"{symbol} sma recounted", "data": current_bbands}


@app.get("/compute_sma_scalp", response_class=ORJSONResponse)
async def compute_sma_scalp(symbol: str):
    current_signal = db_manager.get_sma_signal(symbol)
    if current_signal == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    elif current_signal == 1:
        return {"message": f"sell {symbol}"}
    elif current_signal == 0:
        return {"message": f"hold {symbol}"}
    elif current_signal == -1:
        return {"message": f"buy {symbol}"}

@app.get("/compute_sma_cross_scalp", response_class=ORJSONResponse)
async def compute_sma_cross_scalp(symbol: str):
    current_signal = db_manager.get_sma_cross_signal(symbol)
    if current_signal == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    elif current_signal == 1:
        return {"message": f"sell {symbol}"}
    elif current_signal == 0:
        return {"message": f"hold {symbol}"}
    elif current_signal == -1:
        return {"message": f"buy {symbol}"}

@app.get("/compute_bband_scalp", response_class=ORJSONResponse)
async def compute_bband_scalp(symbol: str):
    current_signal = db_manager.get_bbands_signal(symbol)
    if current_signal == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    elif current_signal == 1:
        return {"message": f"sell {symbol}"}
    elif current_signal == 0:
        return {"message": f"hold {symbol}"}
    elif current_signal == -1:
        return {"message": f"buy {symbol}"}


@app.get("/compute_rsi_scalp", response_class=ORJSONResponse)
async def compute_rsi_scalp(symbol: str, thresh: int):
    current_signal = db_manager.get_rsi_signal(symbol, thresh)
    if current_signal == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    elif current_signal == 1:
        return {"message": f"sell {symbol}"}
    elif current_signal == 0:
        return {"message": f"hold {symbol}"}
    elif current_signal == -1:
        return {"message": f"buy {symbol}"}


@app.get("/combined_signal", response_class=ORJSONResponse)
async def compute_combined_signal(symbol: str, thresh: int):
    current_sma = db_manager.get_sma_signal(symbol)
    current_bbands = db_manager.get_bbands_signal(symbol)
    current_rsi = db_manager.get_rsi_signal(symbol, thresh)
    print(current_sma == -1 and current_rsi == -1)
    if current_sma == 404 or current_bbands == 404 or current_rsi == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"symbol {symbol} not found"
        )
    elif current_bbands == 1:
        return {"message": f"sell {symbol}", "sma_signal": current_sma, "rsi_signal": current_rsi, "bbands_signal": current_bbands, "SIG": 1}
    elif current_sma == 1 and current_rsi == 1:
        return {"message": f"sell {symbol}", "sma_signal": current_sma, "rsi_signal": current_rsi, "bbands_signal": current_bbands, "SIG": 1}
    elif current_bbands == -1:
        return {"message": f"buy {symbol}", "sma_signal": current_sma, "rsi_signal": current_rsi, "bbands_signal": current_bbands, "SIG": -1}
    elif current_sma == -1 and current_rsi == -1:
        return {"message": f"buy {symbol}", "sma_signal": current_sma, "rsi_signal": current_rsi, "bbands_signal": current_bbands, "SIG": -1}
    else:
        return {"message": f"hold {symbol}", "sma_signal": current_sma, "rsi_signal": current_rsi, "bbands_signal": current_bbands, "SIG": 0}


@app.get("/sync_symbols", response_class=ORJSONResponse)
async def sync_symbols(symbol: str, client: str):
    current_bank = db_manager.sync_banks(symbol, client)
    if current_bank == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="login or password incorrect"
        )
    return {"message": f"{symbol} bank updated", "data": current_bank}


@app.get("/get_all_fees", response_class=ORJSONResponse)
async def get_fees(client: str):
    fees = db_manager.get_all_fees(client)
    if fees == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="login or password incorrect"
        )
    return {"message": f"{client} retrieved fees",
            "fees": fees}

@app.post("/make_test_order", response_class=ORJSONResponse)
async def make_test_order(order: order_model):
    result = db_manager.make_test_order(order.client, order.symbol, order.quantity, order.price, order.op_code)
    if result == 403:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API-key, IP, or permissions for action."
        )
    return {"message": f"{order.client} tested order",
            "result": result}

if __name__ == "__main__":
    uvicorn.run("rest_api:app", host="127.0.0.1",
                port=8082, reload=True,
                log_level="info")
