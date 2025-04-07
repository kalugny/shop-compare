from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from .services.product_service import ProductService
from .services.shop_service import ShopService

app = FastAPI(title="Shopping Price Comparison")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
product_service = ProductService()
shop_service = ShopService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/products/search")
async def search_products(query: str):
    """Search for products based on query string"""
    return await product_service.find_products(query)

@app.post("/api/shops/compare")
async def compare_shops(product_ids: list[str]):
    """Compare prices across shops for given products"""
    return await shop_service.compare_shops(product_ids) 