-- Create database if not exists
CREATE DATABASE IF NOT EXISTS LoyolaDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON LoyolaDB.* TO 'loyola_user'@'%';
FLUSH PRIVILEGES;
