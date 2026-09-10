CREATE TABLE sales (
    id BIGSERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    product VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity>0),
    revenue NUMERIC(12,2)  OT NULL CHECK (revenue>=0)
)