from litestar import Litestar, get


@get("/")
async def hello_world() -> str:
    return "Hello, Query!"


app = Litestar([hello_world])
