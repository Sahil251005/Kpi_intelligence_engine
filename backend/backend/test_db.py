import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="business_intelligence",
    user="postgres",
    password="Sahil@123",
    port="5432"
)

print("Database connection successful!")

conn.close()