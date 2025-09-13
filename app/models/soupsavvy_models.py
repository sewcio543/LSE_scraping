from soupsavvy import ClassSelector, IdSelector, TypeSelector
from soupsavvy.models import BaseModel
from soupsavvy.operations import Operation, Text

import app.constants as consts


class StockScraperModel(BaseModel):
    __scope__ = IdSelector(consts.STOCK_SCOPE_ID)

    value = (
        ClassSelector(consts.PRICE_TAG_CLASS)
        | Text()
        | Operation(str.replace, ",", "")
        | Operation(float)
    )
    timestamp = (
        ClassSelector(consts.TIMESTAMP_ANCESTOR_CLASS)
        >> TypeSelector(consts.TIMESTAMP_TAG_TYPE)
    ) | Text()
