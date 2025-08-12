// Actualizar fecha
document.getElementById('date').textContent = new Date().toLocaleDateString('es-ES');

// Botón de prueba
document.getElementById('testBtn').addEventListener('click', function() {
    const messageDiv = document.getElementById('message');
    const messages = [
        '¡Pipeline funcionando perfectamente! 🚀',
        '¡CloudFront está distribuyendo tu contenido globalmente! 🌍',
        '¡CI/CD activo y listo! ⚡',
        '¡Tu aplicación está en la nube! ☁️',
        '¡Despliegue exitoso! ✅'
    ];
    
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    messageDiv.textContent = randomMessage;
    messageDiv.classList.add('show');
    
    // Animar el botón
    this.style.transform = 'scale(0.95)';
    setTimeout(() => {
        this.style.transform = 'scale(1)';
    }, 200);
    
    // Ocultar mensaje después de 3 segundos
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 3000);
});

// Efecto de aparición gradual
window.addEventListener('load', function() {
    document.querySelector('.container').style.animation = 'fadeIn 1s ease';
});

// Log para verificar que el script está funcionando
console.log('🚀 Aplicación AWS cargada correctamente');
console.log('Pipeline: CodePipeline ✓');
console.log('Build: CodeBuild ✓');
console.log('Storage: S3 ✓');
console.log('CDN: CloudFront ✓');