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

/**
 * Animación en dos fases:
 * - Fase 1: hasta 70% en 100s (1:40)
 * - Fase 2: al finalizar fetch, completa 100% y colorea
 */
function iniciarGeneracion(ctx) {
  const { previewContent, btnConfirmar, bar, robot } = ctx;
  const robotImg = document.querySelector(".robot-progress img");

  // Seguridad: si faltan elementos, salir
  if (!bar || !robotImg || !previewContent || !btnConfirmar) {
    console.warn("Faltan elementos del DOM para la animación/preview.");
    return;
  }

  let progress = 0;

  // Opcional: marca visual de "en ejecución"
  if (robot) robot.classList.add("running");

  // Fase 1: avanzar hasta 70% en exactamente 100s
  // Elegimos tick de 200ms para fluidez:
  // 100s / 0.2s = 500 ticks → step = 70 / 500 = 0.14% por tick
  const tickMs = 200;
  const step = 70 / (100 / (tickMs / 1000)); // equivalente a 0.14%
  const interval = setInterval(() => {
    progress += step;
    if (progress >= 70) {
      progress = 70;
      clearInterval(interval); // detener en 70%
    }
    bar.style.width = progress + "%";
    robotImg.style.filter = `grayscale(${Math.max(0, 100 - progress)}%)`;
  }, tickMs);

  // Fase 2: proceso real con fetch (cuando termina, completar 100%)
  fetch(`/panel/generar_memoria/${planoId}/`)
    .then(response => {
      if (!response.ok) {
        throw new Error("Respuesta HTTP no OK: " + response.status);
      }
      return response.json();
    })
    .then(data => {
      // Mostrar la memoria generada
      previewContent.innerHTML = "<pre>" + (data.memoria || "Memoria vacía") + "</pre>";

      // Mostrar botón de descarga
      btnConfirmar.style.display = "inline-block";

      // Completar al 100% y color total
      clearInterval(interval);
      bar.style.width = "100%";
      robotImg.style.filter = "grayscale(0%)";

      // Opcional: remover clase running para estado final
      if (robot) robot.classList.remove("running");
    })
    .catch(error => {
      console.error("Error al generar la memoria:", error);
      previewContent.innerHTML = "<p>Error al generar la memoria.</p>";

      // Detener animación si hubo error
      clearInterval(interval);

      // Opcional: feedback visual de error (rojo)
      bar.style.width = "100%";
      bar.style.background = "#e53935";
      if (robot) robot.classList.remove("running");
    });
}
