from pydantic import BaseModel


class StockRequest(BaseModel):
    company_name: str
    stock_code: str


class StockResponse(BaseModel):
    company_name: str
    stock_code: str
    timestamp: str | None = None
    value: float | None = None
