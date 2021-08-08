import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class symbol_model(BaseModel):
    symbol_name: str
    candlestick_data: dict
    sma_data: dict
    ema_data: dict
    rsi_data: dict


@app.get("/start_gathering_symbol")
async def start_gathering_symbol(symbol: str):
    return {"message": f"{symbol} gathering started"}


@app.get("/stop_gathering_symbol")
async def stop_gathering_symbol(symbol: str):
    return {"message": f"{symbol} gathering stopped"}


@app.get("/get_hourly_report")
async def get_hourly_report(symbol: str):
    return {"message": f"{symbol} hourly report"}


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


@app.get("/get_full_data")
async def get_full_data(symbol: str):
    return {"message": f"{symbol} data"}


@app.get("/get_full_sma")
async def get_full_sma(symbol: str):
    return {"message": f"{symbol} sma"}


@app.get("/get_full_ema")
async def get_full_ema(symbol: str):
    return {"message": f"{symbol} ema"}


@app.get("/get_full_rsi")
async def get_full_rsi(symbol: str):
    return {"message": f"{symbol} rsi"}


if __name__ == "__main__":
    uvicorn.run("rest_api:app", host="127.0.0.1",
                port=8080, reload=True,
                log_level="info")
