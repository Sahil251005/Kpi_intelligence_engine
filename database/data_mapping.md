# BusinessIntelligence.ai - Data Mapping

## Core Tables

### 1. orders
Source: olist_orders_dataset.csv

Purpose:
Main order-level information and time dimension.

Important columns:
- order_id
- customer_id
- order_status
- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date


### 2. order_items
Source: olist_order_items_dataset.csv

Purpose:
Product-level sales and revenue calculation.

Important columns:
- order_id
- order_item_id
- product_id
- seller_id
- shipping_limit_date
- price
- freight_value


### 3. customers
Source: olist_customers_dataset.csv

Purpose:
Customer location and regional segmentation.

Important columns:
- customer_id
- customer_unique_id
- customer_zip_code_prefix
- customer_city
- customer_state


### 4. products
Source: olist_products_dataset.csv

Purpose:
Product and category analysis.

Important columns:
- product_id
- product_category_name


### 5. reviews
Source: olist_order_reviews_dataset.csv

Purpose:
Customer feedback and unstructured evidence.

Important columns:
- review_id
- order_id
- review_score
- review_comment_title
- review_comment_message
- review_creation_date
- review_answer_timestamp


### 6. payments
Source: olist_order_payments_dataset.csv

Purpose:
Payment information and revenue validation.

Important columns:
- order_id
- payment_sequential
- payment_type
- payment_installments
- payment_value


### 7. sellers
Source: olist_sellers_dataset.csv

Purpose:
Seller-level analysis.

Important columns:
- seller_id
- seller_zip_code_prefix
- seller_city
- seller_state


## Supporting Tables

### 8. geolocation
Source: olist_geolocation_dataset.csv

Purpose:
Optional geographic enrichment.

Important columns:
- geolocation_zip_code_prefix
- geolocation_lat
- geolocation_lng
- geolocation_city
- geolocation_state


### 9. product_category_translation
Source: product_category_name_translation.csv

Purpose:
Convert Portuguese product categories into English.

Important columns:
- product_category_name
- product_category_name_english