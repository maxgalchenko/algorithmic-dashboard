from typing import Union
from fastapi import FastAPI, HTTPException
from schemas import BacktestRequest, BacktestResponse
from strategy import run_backtest


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/backtest", response_model=BacktestResponse)
def backtest(request: BacktestRequest) -> BacktestResponse:
    # Validate inputs (Systematic safeguards)
    if request.fast_ma >= request.slow_ma:
        raise HTTPException(
            status_code=400, detail="Fast MA must be smaller than Slow MA"
        )

    try:
        result = run_backtest(request.ticker, request.fast_ma, request.slow_ma)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
