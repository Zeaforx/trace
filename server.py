import json
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Trace")
app.mount("/static", StaticFiles(directory=BASE_DIR / "web" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "web" / "templates"))


def load_concepts():
    with open(BASE_DIR / "concepts.json") as f:
        return json.load(f)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    data = load_concepts()
    print("Loaded concepts:", data["courses"])
    return templates.TemplateResponse(
        request, "index.html", {"courses": data["courses"]}
    )


@app.post("/run")
async def run_animation(request: Request):
    body = await request.json()
    concept_file = body.get("file")
    params = body.get("params", {})

    script_path = BASE_DIR / concept_file
    if not script_path.exists():
        return JSONResponse({"error": f"File not found: {concept_file}"}, status_code=404)

    cmd = [sys.executable, str(script_path)]
    for key, value in params.items():
        if value != "" and value is not None:
            cmd += [f"--{key}", str(value)]

    try:
        subprocess.Popen(cmd)
        return JSONResponse({"status": "launched", "cmd": " ".join(cmd)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
