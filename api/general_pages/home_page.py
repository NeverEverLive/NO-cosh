from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import JSONResponse
from model import AdvertisementSchema
from cloudinary import uploader
import cloudinary

general_pages_router = APIRouter()
# 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

@general_pages_router.get("/")
async def home(request: Request):
    response = {
        "message": "hello"
    }
    return JSONResponse({"data": response, "status": 0})
    # return JSONResponse({"data": await request.json(), "status": 0})


@general_pages_router.post("/test")
def test(file: UploadFile = File(...)):
    result = uploader.upload(file.file)
    url = result.get('url')
    return {"data": url}
    # print(ad.id, ad.text)