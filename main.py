from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from diagram_functions import save_html_to_root
from IA import ask_IA

# Crear la aplicación FastAPI
app = FastAPI()

# Configuración de templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ruta para servir la página HTML
@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

# Ruta para manejar las consultas al asistente
@app.post("/query")
async def query_assistant(question: str = Form(...)):
    # try:
        # Llamar al asistente y obtener la respuesta
        response = ask_IA(question)
        # Guardar el resultado como HTML si es necesario
        # save_html_to_root(response['resp'])
        return {"success": True, "response": response['resp']}
    # except Exception as e:
    #     print('######', e)
    #     return {"success": False, "error": str(e)}
