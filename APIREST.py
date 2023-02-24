from typing import Optional   
from fastapi import FastAPI, APIRouter, UploadFile, File, FileResponse
from pydantic import BaseModel  
from datetime import datetime
from time import sleep
import uvicorn
from os import getcwd
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

servidor = APIRouter()

@servidor.post("/upload")
async def post_upload(file: UploadFile = File(...)):
    with open(getcwd() + '/' + file.filename, "wb") as myfile:
        data = await file.read()
        myfile.write(data)
        mifile.close()
    return 'VIDEO RECIBIDO OK'

@servidor.get("/file/{name_file}")
def get_file(name_file:str):
    return FileResponse(getcwd() + "/" + name_file)

@servidor.get("/download/{name_file}")
def get_download(name_file: tr):
    return FileResponse(getcwd() + "/" + name_file, media_type ="aplication/octet-stream",filename= name_file)

if __name__ == "__main__":
    uvicorn.run(servidor, host="0.0.0.0", port=8000)