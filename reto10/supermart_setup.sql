-- Crear la base de datos principal
CREATE DATABASE supermart;

-- Conectarse a la nueva base de datos (psql)
\c supermart

-- Crear tabla de productos
CREATE TABLE productos (
    id         SERIAL PRIMARY KEY,
    nombre     VARCHAR(100)   NOT NULL,
    precio     DECIMAL(10,2)  NOT NULL CHECK (precio >= 0),
    stock      INTEGER        NOT NULL CHECK (stock >= 0),
    categoria  VARCHAR(50)    NOT NULL,
    proveedor  VARCHAR(100)   DEFAULT 'No especificado',
    creado_en  TIMESTAMP      NOT NULL DEFAULT NOW()   -- << agregado
);

-- Crear tabla de ventas
CREATE TABLE ventas (
    id          SERIAL PRIMARY KEY,
    producto_id INTEGER        NOT NULL REFERENCES productos(id),
    cantidad    INTEGER        NOT NULL CHECK (cantidad > 0),
    total       DECIMAL(10,2)  NOT NULL CHECK (total >= 0),
    fecha       TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insertar productos de ejemplo
INSERT INTO productos (nombre, precio, stock, categoria, proveedor) VALUES
('Arroz Diana 1kg',        2.50, 100, 'Granos',    'Distribuidora Central'),
('Leche Alpina 1L',        1.20,  80, 'Lácteos',   'Alpina S.A.'),
('Pan Tajado Bimbo',       1.80,  50, 'Panadería', 'Grupo Bimbo'),
('Aceite Gourmet 1L',      4.50,  40, 'Aceites',   'Aceites Colombia'),
('Pasta Doria 500g',       1.10, 120, 'Granos',    'Doria S.A.'),
('Pollo Entero kg',        5.00,  30, 'Carnes',    'Avícola Nacional'),
('Tomate kg',              2.20,  60, 'Verduras',  'Finca San Pedro'),
('Coca Cola 2L',           2.80,  90, 'Bebidas',   'Coca Cola Company'),
('Detergente Fab 1kg',     3.50,  25, 'Aseo',      'P&G Colombia'),
('Shampoo Head&Shoulders', 8.90,  15, 'Cuidado',   'P&G Colombia');

-- Insertar algunas ventas de ejemplo
INSERT INTO ventas (producto_id, cantidad, total) VALUES
(1, 2, 5.00),
(2, 1, 1.20),
(8, 3, 8.40);

-- Verificaciones rápidas
SELECT 'Productos insertados:' AS label, COUNT(*) FROM productos;
SELECT 'Ventas registradas:'   AS label, COUNT(*) FROM ventas;
