// Asegura que el DOM esté listo
document.addEventListener("DOMContentLoaded", function() {
  const btnGenerar = document.getElementById("btn-generar-memoria");
  const previewContainer = document.getElementById("memoria-preview-container");
  const previewContent = document.getElementById("memoria-preview-content");
  const btnConfirmar = document.getElementById("btn-confirmar-descarga");
  const robot = document.getElementById("robot-progress");
  const bar = document.querySelector(".progress-bar");

  // Auto-refresh si el plano está procesando (p.ej. backend en curso)
  if (window.planoEstado === "procesando") {
    setTimeout(function () {
      location.reload();
    }, 5000);
  }

  // Listener del botón Generar
  if (btnGenerar) {
    btnGenerar.addEventListener("click", function() {
      // Mostrar contenedor y mensaje inicial
      if (previewContainer) previewContainer.style.display = "block";
      if (previewContent) previewContent.innerHTML = "<p>Generando memoria descriptiva con IA...</p>";

      // Mostrar robot y resetear barra
      if (robot) robot.style.display = "block";
      if (bar) bar.style.width = "0%";

      // Disparar animación progresiva + fetch real
      iniciarGeneracion({ previewContent, btnConfirmar, bar, robot });
    });
  }

  // Descargar memoria generada
  if (btnConfirmar) {
    btnConfirmar.addEventListener("click", function() {
      window.location.href = `/panel/descargar_memoria/${planoId}/`;
    });
  }
});

function iniciarGeneracion(ctx) {
  const { previewContent, btnConfirmar, bar, robot } = ctx;
  const robotImg = document.querySelector(".robot-progress img");

  let progress = 0;
  const tickMs = 200;
  const step = 100 / (100 / (tickMs / 1000)); // 100s / 0.2s = 500 ticks → 0.2% por tick

  const interval = setInterval(() => {
    progress += step;
    if (progress >= 100) {
      progress = 100;
      clearInterval(interval);
    }
    bar.style.width = progress + "%";
    robotImg.style.filter = `grayscale(${100 - progress}%)`; // se desgrisa progresivamente
  }, tickMs);

  fetch(`/panel/generar_memoria/${planoId}/`)
    .then(r => r.json())
    .then(data => {
      previewContent.innerHTML = "<pre>" + (data.memoria || "Memoria vacía") + "</pre>";
      btnConfirmar.style.display = "inline-block";

      clearInterval(interval);
      bar.style.width = "100%";
      robotImg.style.filter = "grayscale(0%)"; // color completo
    })
    .catch(error => {
      console.error(error);
      previewContent.innerHTML = "<p>Error al generar la memoria.</p>";
      clearInterval(interval);
      bar.style.width = "100%";
      bar.style.background = "#e53935";
    });
}
