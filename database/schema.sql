-- Create database
CREATE DATABASE IF NOT EXISTS latte_lounge_caffe;
USE latte_lounge_caffe;

-- Menu categories
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    time_range VARCHAR(50) NOT NULL COMMENT 'Time range when this category is available (e.g., "6-11" for breakfast)'
);

-- Menu items
CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INT NOT NULL,
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_drink BOOLEAN DEFAULT FALSE,
    is_dessert BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    order_type ENUM('pickup', 'delivery') NOT NULL,
    delivery_address TEXT,
    payment_method ENUM('cash', 'card') NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    menu_item_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);

-- Unrecognized customer queries for continuous service improvement
CREATE TABLE IF NOT EXISTS unknown_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    query TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);