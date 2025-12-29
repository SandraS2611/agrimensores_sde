import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generar_memoria_gemini(datos):
    prompt = f"""
    Eres un asistente experto en agrimensura y documentación técnica.
    Tu tarea es redactar una MEMORIA DESCRIPTIVA completa y formal de un plano de mensura y división.
    Usa exclusivamente los datos extraídos del PDF que te paso en formato JSON.

    Datos extraídos del PDF:
    {datos}

    Instrucciones:
    - Incluye encabezado: "MEMORIA DESCRIPTIVA".
    - Completa los campos: Departamento, Padrones, Lugar, Dominio, Baricentro geográfico, Objeto, Inmueble, Titular, Fecha de operación.
    - Redacta un extracto de título con Dominio, Inmueble y medidas/linderos.
    - Genera la Planilla de Superficies en tabla.
    - Genera la Planilla de Lados del polígono principal.
    - Genera la tabla de Coordenadas Geodésicas POSGAR 07.
    - Incluye las Notas oficiales y Referencias.
    - Finaliza con la fórmula institucional.
    """

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",  # usa el modelo que viste en list_models.py
        contents=prompt
    )
    return response.text
