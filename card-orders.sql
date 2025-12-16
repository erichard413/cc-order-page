
.echo on
.print 'Initializing card-orders database...'

-- Drop all tables if they exist (add more as needed)
PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS banks;
DROP TABLE IF EXISTS order_items;
-- Add all other tables here in correct dependency order

PRAGMA foreign_keys = ON;

.read card-orders-schema.sql
.read card-orders-seed.sql

.print 'card-orders database initialized!'

--------------------------------------------------------------------------------

