CREATE DATABASE IF NOT EXISTS enterprise_assistant_memory
    DEFAULT CHARACTER SET utf8mb4;

GRANT ALL PRIVILEGES ON enterprise_assistant_memory.*
    TO 'enterprise_app'@'%';
