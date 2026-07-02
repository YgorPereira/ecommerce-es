from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.modules.addresses.router import address_router
from src.modules.cart_items.router import cart_item_router
from src.modules.carts.router import cart_router
from src.modules.categories.router import category_router
from src.modules.coupons.router import coupon_router
from src.modules.inventories.router import inventory_router
from src.modules.products.router import product_router
from src.modules.users.router import user_router
from src.modules.auth.router import auth_router
import uvicorn

from src.shared.exceptions import AppException

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(user_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(coupon_router)
app.include_router(inventory_router)
app.include_router(address_router)
app.include_router(cart_router)
app.include_router(cart_item_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
