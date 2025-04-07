# Shopping Price Comparison App

A FastAPI-based web application for comparing grocery prices across different Israeli supermarkets.

## Features

- Search for products in Hebrew
- Add products to a shopping list
- Compare prices across different online supermarkets
- View the best deals for your entire shopping list
- Direct links to online stores

## Setup

1. Install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

3. Open your browser and navigate to `http://localhost:8000`

## Usage

1. Enter a product name in Hebrew in the search box
2. Click on products to add them to your shopping list
3. Once you've added all desired products, click "Compare Prices"
4. View the best deals and click through to the online stores

## API Endpoints

- `GET /api/products/search?query=<search_term>` - Search for products
- `POST /api/shops/compare` - Compare prices across shops for a list of products

## Technologies Used

- FastAPI
- Pandas
- TailwindCSS
- HTML/JavaScript 