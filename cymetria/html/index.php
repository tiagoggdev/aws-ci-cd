<?php
$host = '<IP-publica-BD>';
$db = 'inventario';
$user = 'admin';
$pass = 'admin123';
$conn = pg_connect("host=$host dbname=$db user=$user password=$pass");

if (!$conn) {
    echo "<div style='font-family:Arial,sans-serif;text-align:center;color:#b30000;margin-top:50px;'>
            <h1>Error de conexión a la base de datos</h1>
            <p>Verifica que la instancia de base de datos esté activa y accesible.</p>
          </div>";
    exit;
}

$result = pg_query($conn, "SELECT * FROM productos");

echo "
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='UTF-8'>
    <title>Inventario de Productos</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f6f8;
            margin: 0;
            padding: 30px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        table {
            margin: 20px auto;
            width: 80%;
            border-collapse: collapse;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            border: 1px solid #ccc;
            text-align: center;
        }
        th {
            background-color: #007acc;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #eef6fc;
        }
        tr:hover {
            background-color: #d1e9ff;
        }
    </style>
</head>
<body>
    <h2>Listado de Productos</h2>
    <table>
        <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Cantidad</th>
            <th>Precio</th>
        </tr>";

while ($row = pg_fetch_assoc($result)) {
    echo "<tr>
            <td>{$row['id']}</td>
            <td>{$row['nombre']}</td>
            <td>{$row['cantidad']}</td>
            <td>$" . number_format($row['precio'], 2, '.', ',') . "</td>
          </tr>";
}

echo "
    </table>
</body>
</html>";
?>
