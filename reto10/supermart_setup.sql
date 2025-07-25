-- Crear la base de datos principal
CREATE DATABASE supermart;

-- Conectarse a la nueva base de datos
\c supermart

-- Crear tabla de productos
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INTEGER NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    proveedor VARCHAR(100) DEFAULT 'No especificado'
);

-- Crear tabla de ventas
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    cantidad INTEGER NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar productos de ejemplo
INSERT INTO productos (nombre, precio, stock, categoria, proveedor) VALUES
('Arroz Diana 1kg', 2.50, 100, 'Granos', 'Distribuidora Central'),
('Leche Alpina 1L', 1.20, 80, 'Lácteos', 'Alpina S.A.'),
('Pan Tajado Bimbo', 1.80, 50, 'Panadería', 'Grupo Bimbo'),
('Aceite Gourmet 1L', 4.50, 40, 'Aceites', 'Aceites Colombia'),
('Pasta Doria 500g', 1.10, 120, 'Granos', 'Doria S.A.'),
('Pollo Entero kg', 5.00, 30, 'Carnes', 'Avícola Nacional'),
('Tomate kg', 2.20, 60, 'Verduras', 'Finca San Pedro'),
('Coca Cola 2L', 2.80, 90, 'Bebidas', 'Coca Cola Company'),
('Detergente Fab 1kg', 3.50, 25, 'Aseo', 'P&G Colombia'),
('Shampoo Head&Shoulders', 8.90, 15, 'Cuidado', 'P&G Colombia');

-- Insertar algunas ventas de ejemplo
INSERT INTO ventas (producto_id, cantidad, total) VALUES
(1, 2, 5.00),
(2, 1, 1.20),
(8, 3, 8.40);

-- Verificar que todo funcione
SELECT 'Productos insertados:', COUNT(*) FROM productos;
SELECT 'Ventas registradas:', COUNT(*) FROM ventas;
