# ia_validacion.py
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai.errors import ClientError

load_dotenv()

def validar_y_corregir(datos):
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    prompt = f"""
    Analiza este diccionario de datos extraídos de un plano de mensura.
    - Completa los campos vacíos o "No especificado" usando el campo 'texto_completo'.
    - Corrige errores de OCR (números mal formateados, coordenadas incompletas).
    - Devuelve únicamente un JSON válido y completo, sin explicaciones ni código extra.

    Datos:
    {datos}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        # Intentar parsear directamente a dict
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Si no es JSON válido, devolver dict con error y texto crudo
            return {"error": "Respuesta no es JSON válido", "raw": text}

    except ClientError as e:
        return {"error": f"Error de cliente: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}
