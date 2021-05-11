from io import BytesIO
import json
import traceback
import requests

from starlette.responses import StreamingResponse
from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.logger import logger

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def manage_exception(module_name, exc):
    logger.exception(module_name + " error")

    detail = {
        "customData": {
            "module": module_name,
            "type": type(exc).__name__,
            "message": str(exc)
        }
    }
    raise HTTPException(status_code=500, detail=detail)

@app.on_event("startup")
async def load_language_config():
    with open("language_config.json") as fd:
        app.state.data = json.load(fd)

@app.get("/")
async def get_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/available_languages")
async def available_languages(request: Request):
    language_config = request.app.state.data
    
    data = {}
    data["speech2text"] = list(language_config["speech2text"].keys())

    data["translation"] = {}
    for source_language in language_config["translation"].keys():
        data["translation"][source_language] = list(language_config["translation"][source_language].keys())

    data["text2speech"] = list(language_config["text2speech"].keys())
    
    return data


@app.post("/recognise_audio")
async def recognise_audio(request: Request, audio: UploadFile = File(...), language: str = Form("es")):

    try:
        speech2text_url = request.app.state.data["speech2text"].get(language)
        if speech2text_url is None:
            raise Exception(f"Speech2Text: Language '{language}' not supported!")

        file_data = {'file': (audio.filename, audio.file, audio.content_type)}
        req = requests.post(speech2text_url, files=file_data)
        if req.status_code != 200:
            raise Exception(f"Error thrown by the component ({req.status_code})!")

        response =  {"text": req.text}
        logger.info(response)
    
        return response

    except Exception as exc:
        manage_exception("Speech recognition", exc)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) #, ssl_keyfile="localhost.key", ssl_certfile="localhost.crt")
