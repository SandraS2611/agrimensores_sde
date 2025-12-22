// Manejo de input de archivo
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

// Efecto 3D tilt
const container = document.querySelector('.upload-container');
document.addEventListener('mousemove', function(e) {
  const xAxis = (window.innerWidth / 2 - e.pageX) / 50;
  const yAxis = (window.innerHeight / 2 - e.pageY) / 50;
  container.style.transform = `rotateY(${xAxis}deg) rotateX(${yAxis}deg)`;
});
document.addEventListener('mouseleave', function() {
  container.style.transform = 'rotateY(0deg) rotateX(0deg)';
});

// Overlay con spinner al enviar formulario
document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("uploadForm");

  form.addEventListener("submit", function () {
    // Crear overlay
    const overlay = document.createElement("div");
    overlay.id = "loadingOverlay";
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.background = "rgba(10,10,20,0.85)";
    overlay.style.display = "flex";
    overlay.style.flexDirection = "column";
    overlay.style.alignItems = "center";
    overlay.style.justifyContent = "center";
    overlay.style.zIndex = "9999";
    overlay.style.color = "var(--text-primary)";

    overlay.innerHTML = `
      <div class="spinner"></div>
      <p style="margin-top:20px;font-size:18px;">Procesando plano...</p>
    `;

    document.body.appendChild(overlay);
  });
});
