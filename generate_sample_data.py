"""
generate_sample_data.py — Creates sample CSV datasets for the AI Data Analyst demo.
Run: python generate_sample_data.py
"""
import pandas as pd
import random
from datetime import datetime, timedelta

def make_sales():
    random.seed(42)
    products = ['Laptop','Monitor','Keyboard','Mouse','Headphones','Webcam','Docking Station','Tablet']
    regions = ['North','South','East','West','Central']
    start = datetime(2023,1,1)
    rows = []
    for i in range(500):
        date = start + timedelta(days=random.randint(0,364))
        units = random.randint(1,50)
        price = round(random.uniform(20,800), 2)
        disc  = round(random.uniform(0,0.3), 2)
        cost  = round(random.uniform(10,400), 2)
        rev   = round(price * units * (1 - disc), 2)
        profit= round(rev - cost * units, 2)
        # inject outliers
        if i in [50,150,250,350,450]:
            rev   = round(rev   * 8, 2)
            profit= round(profit* 8, 2)
        rows.append({
            'date': date.strftime('%Y-%m-%d'),
            'product': random.choice(products),
            'region': random.choice(regions),
            'units_sold': units,
            'unit_price': price,
            'discount': disc,
            'cost': cost,
            'revenue': rev,
            'profit': profit,
        })
    pd.DataFrame(rows).to_csv('data/sample_sales.csv', index=False)
    print('sample_sales.csv ok')

def make_ecommerce():
    random.seed(99)
    categories = ['Electronics','Clothing','Books','Home & Garden','Sports','Beauty','Toys','Food']
    start = datetime(2023,1,1)
    rows = []
    for i in range(300):
        qty = random.randint(1,10)
        price = round(random.uniform(5,500), 2)
        total = round(price * qty, 2)
        disc  = round(random.uniform(0,0.25), 2)
        rows.append({
            'order_id': f'ORD-{1000+i}',
            'customer_id': f'CUST-{random.randint(100,500)}',
            'order_date': (start+timedelta(days=random.randint(0,364))).strftime('%Y-%m-%d'),
            'category': random.choice(categories),
            'price': price,
            'quantity': qty,
            'rating': round(random.uniform(1,5), 1),
            'return_flag': random.choices([0,1], weights=[85,15])[0],
            'shipping_days': random.randint(1,14),
            'total_amount': total,
            'discount_applied': disc,
            'net_amount': round(total * (1 - disc), 2),
        })
    pd.DataFrame(rows).to_csv('data/sample_ecommerce.csv', index=False)
    print('sample_ecommerce.csv ok')

if __name__ == '__main__':
    import os
    os.makedirs('data', exist_ok=True)
    make_sales()
    make_ecommerce()
    print('Done!')
