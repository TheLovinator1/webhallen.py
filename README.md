# webhallen.py

A Python wrapper for the Webhallen API

## Installation

```bash
pip install webhallen
```

## Usage

```python
from webhallen import Webhallen

# Initialize the client
webhallen = Webhallen()

# Get a product by ID
try:
    product = webhallen.get_product(1234)
    print(product)
except ProductNotFoundError:
    print("Product not found")

# Search for products
products = webhallen.search("RTX 3080", limit=5)
for product in products:
    print(product['name'])
```

## Features

- Retrieve product details by ID
- Search for products
- Error handling for API interactions

## Requirements

- Python 3.8+
- httpx
