import requests
import pandas as pd
from typing import List, Dict, Any

class ProductService:
    PRODUCT_ENDPOINT = 'https://chp.co.il/autocompletion/product_extended'

    async def find_products(self, query: str, shopping_address: str = "גבעתיים", num_results: int = 40) -> List[Dict[str, Any]]:
        """Search for products based on query string"""
        results = []
        offset = 0
        
        while len(results) < num_results:
            r = requests.get(self.PRODUCT_ENDPOINT, params={
                'term': query,
                'from': offset,
                'shopping_address': shopping_address,
            })
            batch = r.json()
            results.extend(batch)
            
            if len(batch) < 10:  # Less than 10 results returned, no more to fetch
                break
                
            offset += 10
            
            if len(results) >= num_results:
                results = results[:num_results]  # Trim to exact number requested
                break
        
        if r.status_code != 200:
            return []

        # Convert response to DataFrame and process it
        df = pd.DataFrame(results)
        df = pd.concat([df.drop('parts', axis=1), pd.json_normalize(df['parts'].dropna())], axis=1)
        df['manufacturer'] = df['manufacturer_and_barcode'].str.extract(r'יצרן/מותג: ([^,]+),')
        df['barcode'] = df['manufacturer_and_barcode'].str.extract(r'ברקוד: (\d+)$')
        
        # Convert DataFrame to list of dictionaries
        products = df.dropna(axis=0, how='any').to_dict('records')
        
        # Format the response
        formatted_products = []
        for product in products:
            formatted_products.append({
                'id': product['id'],
                'label': product['label'],
                'manufacturer': product['manufacturer'],
                'barcode': product['barcode'],
                'image': product['small_image'],
                'price_range': product['price_range']
            })
            
        return formatted_products 