USE latte_lounge_caffe;

-- Insert categories
INSERT INTO categories (name, time_range) VALUES
('Breakfast', '6-11'),
('Lunch', '11-16'),
('Dinner', '16-22'),
('All Day', '6-22'),
('Bakery', '6-22');

-- Insert menu items
INSERT INTO menu_items (name, description, price, category_id, is_vegetarian, is_drink, is_dessert) VALUES
-- Breakfast items
('Avocado Toast', 'Sourdough bread with smashed avocado, cherry tomatoes, and feta', 850.00, 1, TRUE, FALSE, FALSE),
('Pancake Stack', 'Fluffy pancakes with maple syrup and fresh berries', 750.00, 1, TRUE, FALSE, FALSE),
('Eggs Benedict', 'English muffin with poached eggs, ham, and hollandaise', 950.00, 1, FALSE, FALSE, FALSE),
('Breakfast Burrito', 'Scrambled eggs, black beans, cheese, and salsa in a tortilla', 800.00, 1, FALSE, FALSE, FALSE),

-- Lunch items
('Caesar Salad', 'Romaine lettuce, croutons, parmesan, and Caesar dressing', 900.00, 2, FALSE, FALSE, FALSE),
('Veggie Burger', 'House-made patty with lettuce, tomato, and special sauce', 1050.00, 2, TRUE, FALSE, FALSE),
('Chicken Panini', 'Grilled chicken, mozzarella, and pesto on ciabatta', 1100.00, 2, FALSE, FALSE, FALSE),
('Margherita Pizza', 'Tomato sauce, fresh mozzarella, and basil', 1250.00, 2, TRUE, FALSE, FALSE),

-- Dinner items
('Pasta Carbonara', 'Spaghetti with creamy egg sauce, pancetta, and parmesan', 1400.00, 3, FALSE, FALSE, FALSE),
('Mushroom Risotto', 'Creamy arborio rice with wild mushrooms and herbs', 1350.00, 3, TRUE, FALSE, FALSE),
('Grilled Salmon', 'With roasted vegetables and lemon butter sauce', 1650.00, 3, FALSE, FALSE, FALSE),
('Beef Tenderloin', '8oz beef with mashed potatoes and red wine reduction', 1900.00, 3, FALSE, FALSE, FALSE),

-- All day items
('House Coffee', 'Freshly brewed coffee', 350.00, 4, TRUE, TRUE, FALSE),
('Iced Latte', 'Espresso with milk and ice', 450.00, 4, TRUE, TRUE, FALSE),
('Fresh Orange Juice', 'Cold-pressed orange juice', 400.00, 4, TRUE, TRUE, FALSE),
('Chocolate Cake', 'Rich chocolate cake with ganache', 650.00, 4, TRUE, FALSE, TRUE),
('Tiramisu', 'Classic Italian dessert with coffee flavor', 700.00, 4, TRUE, FALSE, TRUE),

-- Bakery & Pastry items
('Topan Virtles', 'Traditional golden bundt cake ring sprinkled with powdered sugar and vanilla aroma', 650.00, 5, TRUE, FALSE, TRUE),
('Spâtues', 'Soft artisan brioche ring baked with sweet cherries and caramelized glaze', 750.00, 5, TRUE, FALSE, TRUE),
('Artisan Choux Ring', 'Fluted choux pastry ring filled with light vanilla bean cream and powdered sugar', 680.00, 5, TRUE, FALSE, TRUE),
('Gueke Tmes', 'Twisted cinnamon brioche wreath with delicate sugar glaze', 590.00, 5, TRUE, FALSE, TRUE),
('Saper Cluter', 'Almond-crusted fluted cake dusted with confectioners sugar', 720.00, 5, TRUE, FALSE, TRUE),
('Saper Coldes', 'Golden sponge ring with rich mascarpone filling and toasted crumb', 820.00, 5, TRUE, FALSE, TRUE),
('Signature Raspberry Cake Slice', 'Layers of moist vanilla sponge, wild raspberry compote, and light cream', 850.00, 5, TRUE, FALSE, TRUE);
