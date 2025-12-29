from pdf_processor import PDFProcessor, generar_memoria
from ia_validacion import validar_y_corregir
import sys

def main(pdf_path):
    processor = PDFProcessor(pdf_path)
    datos = processor.extract_data()

    # Validación y corrección con IA
    datos_corregidos = validar_y_corregir(datos)

    if "error" in datos_corregidos:
        print("⚠️ Error en validación:", datos_corregidos)
        memoria = generar_memoria(datos)  # fallback con datos crudos
    else:
        print("✅ JSON corregido:", datos_corregidos)
        memoria = generar_memoria(datos_corregidos)

    # Mostrar la memoria descriptiva final
    print("\n=== Memoria descriptiva final ===")
    print(memoria)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_pdfprocessor.py archivo.pdf")
    else:
        main(sys.argv[1])
