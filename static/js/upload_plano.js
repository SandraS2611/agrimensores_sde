// static/js/upload_plano.js

  // File input handling
  const fileInput = document.getElementById('archivo_pdf');
  const fileName = document.getElementById('fileName');
  const dropZone = document.getElementById('dropZone');

  fileInput.addEventListener('change', function() {
    if (this.files && this.files[0]) {
      fileName.textContent = '📄 ' + this.files[0].name;
      fileName.classList.add('visible');
    }
  });

  // Drag and drop
  dropZone.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('dragover');
  });

  dropZone.addEventListener('dragleave', function(e) {
    e.preventDefault();
    this.classList.remove('dragover');
  });

  dropZone.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('dragover');
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      fileInput.files = e.dataTransfer.files;
      fileName.textContent = '📄 ' + e.dataTransfer.files[0].name;
      fileName.classList.add('visible');
    }
  });

  // 3D tilt effect
  const container = document.querySelector('.upload-container');
  
  document.addEventListener('mousemove', function(e) {
    const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
    const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
    container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
  });

  document.addEventListener('mouseleave', function() {
    container.style.transform = 'rotateY(0deg) rotateX(0deg)';
  });

// Mostrar nombre del archivo seleccionado
function showFileName(input) {
  const fileName = document.getElementById("fileName");
  if (input.files && input.files[0]) {
    fileName.textContent = "✓ " + input.files[0].name;
  }
}

// Spinner de carga al enviar el formulario
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("uploadForm");

  form.addEventListener("submit", function () {
    // Crear overlay con spinner
    const overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(255,255,255,0.8)";
    overlay.style.display = "flex";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "9999";

    overlay.innerHTML = `
      <div class="spinner"></div>
      <p style="margin-top:20px;font-size:18px;">Procesando plano...</p>
    `;

    document.body.appendChild(overlay);
  });
});
