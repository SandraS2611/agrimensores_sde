import os
from django.conf import settings
from .utils.pdf_processor import PDFProcessor
from .utils.docx_generator import DocxGenerator
from .models import Plano

def procesar_pdf(plano: Plano):
    # 1. Procesar el PDF y extraer datos
    processor = PDFProcessor(plano.archivo_pdf.path)
    datos = processor.extract_data()
    plano.texto_extraido = datos.get("texto_completo", "")
    plano.datos_procesados = datos

    # 2. Generar la memoria descriptiva en Word
    generator = DocxGenerator(plano)
    memoria_full_path = generator.generate_memoria()  # devuelve la ruta completa

    # 3. Guardar la ruta relativa en el modelo
    plano.memoria_path = memoria_full_path.replace(str(settings.MEDIA_ROOT) + os.sep, "")
    plano.estado = "completado"
    plano.save()

    return plano
