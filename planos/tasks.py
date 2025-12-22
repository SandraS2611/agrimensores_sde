from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


@shared_task
def procesar_plano_task(plano_id):
    """
    Tarea asíncrona para procesar un plano PDF
    
    Args:
        plano_id: ID del plano a procesar
    
    Returns:
        dict: Resultado del procesamiento
    """
    
    from .models import Plano
    from .utils.pdf_processor import PDFProcessor
    from .utils.ocr_processor import OCRProcessor
    from .utils.normativa_validator import NormativaValidator
    from .utils.docx import DocxGenerator
    
    try:
        # Obtener el plano
        plano = Plano.objects.get(id=plano_id)
        plano.estado = 'procesando'
        plano.save()
        
        logger.info(f"Iniciando procesamiento del plano {plano_id}: {plano.titulo}")
        
        # 1. Procesar PDF
        pdf_processor = PDFProcessor(plano.archivo_pdf.path)
        texto_extraido = pdf_processor.extract_text()
        tablas = pdf_processor.extract_tables()
        coordenadas = pdf_processor.extract_coordinates()
        
        # 2. OCR si es necesario
        if not texto_extraido or len(texto_extraido) < 100:
            logger.info(f"Aplicando OCR al plano {plano_id}")
            ocr_processor = OCRProcessor(plano.archivo_pdf.path)
            texto_extraido = ocr_processor.extract_text()
        
        # 3. Guardar texto extraído
        plano.texto_extraido = texto_extraido
        
        # 4. Estructurar datos
        datos_procesados = {
            'texto': texto_extraido,
            'tablas': tablas,
            'coordenadas': coordenadas,
            'nomenclatura_catastral': None,  # Extraer de texto
            'superficie': None,  # Extraer de texto
            'propietario': None,  # Extraer de texto
        }
        
        plano.datos_procesados = datos_procesados
        
        # 5. Validar contra normativa
        validator = NormativaValidator(datos_procesados)
        reporte_cumplimiento = validator.generate_report()
        
        # Agregar reporte de cumplimiento a los datos
        datos_procesados['reporte_cumplimiento'] = reporte_cumplimiento
        plano.datos_procesados = datos_procesados
        
        # 6. Generar memoria descriptiva
        docx_generator = DocxGenerator(datos_procesados)
        memoria_path = docx_generator.generate_memoria()
        
        # 7. Actualizar estado
        plano.estado = 'completado'
        plano.save()
        
        logger.info(f"Plano {plano_id} procesado exitosamente")
        
        return {
            'status': 'success',
            'plano_id': plano_id,
            'mensaje': 'Plano procesado correctamente',
            'memoria_path': memoria_path
        }
        
    except ObjectDoesNotExist:
        logger.error(f"Plano {plano_id} no encontrado")
        return {
            'status': 'error',
            'plano_id': plano_id,
            'mensaje': 'Plano no encontrado'
        }
        
    except Exception as e:
        logger.error(f"Error procesando plano {plano_id}: {str(e)}")
        
        # Actualizar estado a error
        try:
            plano = Plano.objects.get(id=plano_id)
            plano.estado = 'error'
            plano.save()
        except:  # noqa: E722
            pass
        
        return {
            'status': 'error',
            'plano_id': plano_id,
            'mensaje': f'Error al procesar: {str(e)}'
        }


@shared_task
def generar_memoria_descriptiva_task(plano_id):
    """
    Tarea para generar solo la memoria descriptiva
    
    Args:
        plano_id: ID del plano
    
    Returns:
        dict: Resultado de la generación
    """
    
    from .models import Plano
    from .utils.docx import DocxGenerator
    
    try:
        plano = Plano.objects.get(id=plano_id)
        
        if not plano.datos_procesados:
            return {
                'status': 'error',
                'mensaje': 'El plano no ha sido procesado aún'
            }
        
        # Generar memoria
        docx_generator = DocxGenerator(plano.datos_procesados)
        memoria_path = docx_generator.generate_memoria()
        
        logger.info(f"Memoria descriptiva generada para plano {plano_id}")
        
        return {
            'status': 'success',
            'plano_id': plano_id,
            'memoria_path': memoria_path
        }
        
    except Exception as e:
        logger.error(f"Error generando memoria para plano {plano_id}: {str(e)}")
        return {
            'status': 'error',
            'mensaje': str(e)
        }