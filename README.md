# 🚀 Mi Aplicación AWS - Pipeline CI/CD

## Descripción
Aplicación web desplegada en AWS usando:
- **CodePipeline**: Orquestación del pipeline CI/CD
- **CodeBuild**: Construcción del proyecto
- **S3**: Almacenamiento de archivos estáticos
- **CloudFront**: CDN para distribución global

## Estructura del Proyecto
```
├── index.html       # Página principal
├── styles.css       # Estilos
├── script.js        # Lógica JavaScript
├── buildspec.yml    # Configuración de CodeBuild
└── README.md        # Documentación
```

## Despliegue Automático
Cada push a la rama `main` activa automáticamente el pipeline de despliegue.

## URL de Producción
La aplicación estará disponible en tu distribución de CloudFront después del despliegue.

## Autor
Antonio Contreras Rodriguez

## Licencia
MIT