import requests
import pandas as pd
from io import StringIO
from typing import List, Dict, Any
from collections import Counter


class ShopService:
    COMPARE_ENDPOINT = "https://chp.co.il/main_page/compare_results"

    async def compare_shops(self, product_ids: List[str]) -> Dict[str, Any]:
        """Compare prices across shops for given products"""
        all_prices = []
        
        # Count quantities for each product
        product_quantities = Counter(product_ids)
        unique_product_ids = list(product_quantities.keys())

        for product_id in unique_product_ids:
            response = requests.get(
                self.COMPARE_ENDPOINT,
                params={"product_barcode": product_id, "from": 0, "num_results": 20},
            )

            if response.status_code != 200:
                continue

            # Parse HTML table from response
            try:
                dfs = pd.read_html(
                    StringIO(response.text), flavor="lxml", match="אתר אינטרנט"
                )
            except Exception as e:
                print(f"Error parsing HTML table: {e}")
                continue

            df = dfs[0].iloc[0::2].reset_index(drop=True)

            # Add product ID and quantity to track which prices belong to which product
            df["product_id"] = product_id
            df["quantity"] = product_quantities[product_id]
            # Multiply price by quantity
            df["total_price"] = df["מחיר"].astype(float) * product_quantities[product_id]
            all_prices.append(df)

        if not all_prices:
            return {"shops": [], "price_details": {}}

        # Combine all price data
        combined_df = pd.concat(all_prices, ignore_index=True)

        # Count how many unique products each shop has
        products_per_shop = combined_df.groupby("רשת")["product_id"].nunique()

        # Calculate total price per shop using the total_price column
        shop_totals = (
            combined_df.groupby("רשת")["total_price"]
            .sum()
            .sort_values()
        )

        # Get all shops with their details
        shops = []
        for shop in shop_totals.index:
            shop_prices = combined_df[combined_df["רשת"] == shop]
            shops.append(
                {
                    "name": shop,
                    "total_price": float(shop_totals[shop]),
                    "website": shop_prices["אתר אינטרנט"].iloc[0],
                    "prices": shop_prices[["product_id", "מחיר", "quantity"]].to_dict("records"),
                    "has_all_products": str(products_per_shop[shop] == len(unique_product_ids)),
                    "product_count": int(products_per_shop[shop]),
                }
            )

        # Sort shops by total price for those that have all products first, then by product count
        shops.sort(key=lambda x: (not (x["has_all_products"] == "True"), x["total_price"]))

        return {
            "shops": shops,
            "price_details": combined_df.fillna(0).to_dict("records"),
            "total_products": len(unique_product_ids),
        }
