from contextlib import asynccontextmanager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.routing import Route


async def home(request: Request) -> JSONResponse:
    print(request.app.state.EMAIL)
    return JSONResponse({"hello": "world"})


@asynccontextmanager
async def lifespan(app):
    print("startup")
    app.state.EMAIL = "admin@example.com"
    yield
    print("shutdown")


routes = [Route("/", home)]

app = Starlette(debug=True, routes=routes, lifespan=lifespan)
