import requests
import pandas as pd
from io import StringIO
from typing import List, Dict, Any

class ShopService:
    COMPARE_ENDPOINT = 'https://chp.co.il/main_page/compare_results'

    async def compare_shops(self, product_ids: List[str]) -> Dict[str, Any]:
        """Compare prices across shops for given products"""
        all_prices = []
        
        for product_id in product_ids:
            response = requests.get(
                self.COMPARE_ENDPOINT,
                params={
                    'product_barcode': product_id,
                    'from': 0,
                    'num_results': 20
                }
            )
            
            if response.status_code != 200:
                continue

            # Parse HTML table from response
            try:
                dfs = pd.read_html(StringIO(response.text), flavor='lxml', match='אתר אינטרנט')
            except Exception as e:
                print(f"Error parsing HTML table: {e}")
                continue
                
            df = dfs[0].iloc[0::2].reset_index(drop=True)
            
            # Add product ID to track which prices belong to which product
            df['product_id'] = product_id
            all_prices.append(df)

        if not all_prices:
            return {
                'best_shops': [],
                'price_details': {}
            }

        # Combine all price data
        combined_df = pd.concat(all_prices, ignore_index=True)
        
        # Count how many products each shop has
        products_per_shop = combined_df.groupby('רשת')['product_id'].nunique()
        
        # Filter shops that don't have all products
        shops_with_all_products = products_per_shop[products_per_shop == len(product_ids)].index
        if len(shops_with_all_products) == 0:
            return {
                'best_shops': [],
                'price_details': {},
                'message': 'לא נמצאו חנויות עם כל המוצרים המבוקשים'
            }
            
        # Filter the dataframe to only include shops with all products
        combined_df = combined_df[combined_df['רשת'].isin(shops_with_all_products)]
        
        # Calculate total price per shop
        shop_totals = combined_df.groupby('רשת')['מחיר'].apply(lambda x: x.astype(float).sum()).sort_values()
        
        # Get top 3 cheapest shops
        best_shops = []
        for shop in shop_totals.head(3).index:
            shop_prices = combined_df[combined_df['רשת'] == shop]
            best_shops.append({
                'name': shop,
                'total_price': float(shop_totals[shop]),
                'website': shop_prices['אתר אינטרנט'].iloc[0],
                'prices': shop_prices[['product_id', 'מחיר']].to_dict('records')
            })

        return {
            'best_shops': best_shops,
            'price_details': combined_df.fillna(0).to_dict('records')
        } 