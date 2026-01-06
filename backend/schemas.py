from pydantic import BaseModel


class BacktestRequest(BaseModel):
    ticker: str
    fast_ma: int
    slow_ma: int


class BacktestResponse(BaseModel):
    total_return: str
    sharpe_ratio: float
