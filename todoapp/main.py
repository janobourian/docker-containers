from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route
import uuid


async def home(request: Request) -> JSONResponse:
    print(request.app.state.EMAIL)
    return JSONResponse(
        {
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "path_params": request.path_params,
        }
    )


async def form_page(request: Request) -> JSONResponse:
    form = await request.form()
    imagen = form.get("imagen")
    data = await imagen.read()
    await imagen.close()
    file_content_type = dict(imagen.headers).get("content-type").split("/")[-1]
    new_filename = f"{uuid.uuid4()}.{file_content_type}"
    with open(f"./todoapp/static/images/{new_filename}", "wb") as f:
        f.write(data)
    return JSONResponse({"new_filename": new_filename})


@asynccontextmanager
async def lifespan(app):
    print("startup")
    app.state.EMAIL = "admin@example.com"
    yield
    print("shutdown")


routes = [Route("/", home), Route("/form", form_page, methods=["POST"])]

app = Starlette(debug=True, routes=routes, lifespan=lifespan)
