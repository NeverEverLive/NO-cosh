from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from model import AdvertisementSchema

general_pages_router = APIRouter()
# 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

@general_pages_router.get("/")
async def home(request: Request):
    response = {
        "message": "hello"
    }
    return JSONResponse({"data": response, "status": 0})
    # return JSONResponse({"data": await request.json(), "status": 0})


@general_pages_router.get("/test")
def test():
    ad = AdvertisementSchema(1, "test")

    print(dict(ad))
    # print(ad.id, ad.text)