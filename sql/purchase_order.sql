CREATE TABLE purchase_order (
    id SERIAL PRIMARY KEY,
    board_id INTEGER NOT NULL,
    file_id INTEGER NOT NULL,
    filepath VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE,
    ordering_company VARCHAR(255),
    ordering_manager VARCHAR(255),
    -- order_date DATE,
    order_date VARCHAR(255),
    order_item TEXT,
    order_quantity INTEGER,
    order_amount NUMERIC,
    order_number VARCHAR(255),
    delivery_company VARCHAR(255),
    -- delivery_deadline DATE,
    delivery_deadline VARCHAR(255),
    customer_manager VARCHAR(255)
);