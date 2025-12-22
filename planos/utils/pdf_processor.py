"""
Procesador de PDFs de planos de agrimensura
"""

import pdfplumber
import re
import logging

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Procesa archivos PDF de planos y extrae información relevante"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.texto_completo = None

        # Compilar regex para mejor rendimiento
        self.re_objeto = re.compile(r"OBJETO[:\s]+([^\n]+)", re.IGNORECASE)
        self.re_lugar = re.compile(r"LUGAR[:\s]+([^\n]+)", re.IGNORECASE)
        self.re_departamento = re.compile(r"DEPARTAMENTO[:\s]+([A-ZÁÉÍÓÚÑ\s]+)", re.IGNORECASE)
        self.re_propietarios = re.compile(r"([A-ZÁÉÍÓÚÑ\s,\.]+)\s+D\.N\.I\.[:\s]*([\d\.]+)\s*C\.U\.I\.L\.[:\s]*([\d\-]+)")
        self.re_dominios = re.compile(r"(M\.?\s*F\.?\s*R\.?\s*[\d\-\/]+|MFR\s*[\d\-\/]+|Matrícula\s*[\d\-\/]+)", re.IGNORECASE)
        self.re_padron = re.compile(r"PADR[ÓO]N[:\s]+([\d\-]+)", re.IGNORECASE)
        self.re_superficies = re.compile(r"(\d+)\s*Has\s*(\d+)\s*As\s*([\d\.]+)\s*Cas")
        self.re_lados = re.compile(r"(\d+|[A-Z])\s+([NS][\.\s][EO])\s+(\d+-\d+|[A-Z]-[A-Z])\s+([\d.,]+)\s*m?\s+(\d+º\d+['’]\d+['”\"])\s+([^\n]+)")
        self.re_fecha_larga = re.compile(r"(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+)\s+de\s+(\d{4})")
        self.re_fecha_corta = re.compile(r"(\d{2}/\d{2}/\d{4})")
        self.re_inmueble = re.compile(r"Inmueble[:\s]+([^\n]+)", re.IGNORECASE)

    def extract_text(self):
        """Extrae el texto manteniendo el layout para procesar tablas"""
        try:
            texto = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        page_text = page_text.replace("\xa0", " ")
                        texto += page_text + "\n"

            self.texto_completo = texto
            return texto
        except Exception as e:
            logger.error(f"Error crítico en PDF: {str(e)}")
            return ""

    def _clean_field(self, text, keywords_to_stop):
        """Corta el texto antes de cualquier palabra de corte para evitar arrastres"""
        if not text:
            return ""
        for word in keywords_to_stop:
            if word.upper() in text.upper():
                text = text.split(word)[0].split(word.upper())[0]
        return text.strip()

    def extract_data(self):
        """Punto de entrada para obtener el diccionario de datos"""
        if not self.texto_completo:
            self.extract_text()

        texto = self.texto_completo or ""
        stop_words = ["PADRON", "LUGAR", "DOMINIO", "OBJETO", "TITULAR", "MINISTERIO"]

        datos = {
            "objeto": self._clean_field(self.extract_objeto(texto), stop_words),
            "lugar": self._clean_field(self.extract_lugar(texto), stop_words),
            "departamento": self._clean_field(self.extract_departamento(texto), stop_words),
            "propietarios": self.extract_propietarios(texto),
            "dominios": self.extract_dominios(texto),
            "padrones": self.extract_padrones(texto),
            "superficies": self.extract_superficies(texto),
            "fecha_operaciones": self.extract_fecha(texto),
            "lados": self.extract_lados_mejorado(texto),
            "inmueble": self._clean_field(self.extract_inmueble(texto), stop_words),
            "descripcion": self.extract_descripcion(texto),
            "croquis": self.extract_croquis(texto),
            "texto_completo": texto.strip(),
        }
        logger.debug("Datos procesados: %s", datos)
        return datos

    def extract_objeto(self, texto):
        m = self.re_objeto.search(texto)
        return m.group(1).strip() if m else "No especificado"

    def extract_lugar(self, texto):
        m = self.re_lugar.search(texto)
        return m.group(1).strip() if m else "No especificado"

    def extract_departamento(self, texto):
        m = self.re_departamento.search(texto)
        return m.group(1).split("\n")[0].strip() if m else "No especificado"

    def extract_propietarios(self, texto):
        propietarios = []
        for nom, dni, cuil in self.re_propietarios.findall(texto):
            propietarios.append({"nombre": nom.strip(), "dni": dni, "cuil": cuil})
        return propietarios

    def extract_dominios(self, texto):
        return [{"matricula": mat.strip()} for mat in self.re_dominios.findall(texto)]

    def extract_padrones(self, texto):
        return self.re_padron.findall(texto)

    def extract_superficies(self, texto):
        """Devuelve superficies como lista de diccionarios"""
        superficies = []
        for h, a, c in self.re_superficies.findall(texto):
            superficies.append({
                "designacion": "No especificado",
                "valor": f"{h} Has {a} As {c} Cas",
                "observaciones": ""
            })
        return superficies

    def extract_lados_mejorado(self, texto):
        """Extrae lados con vértice, rumbo, tramo, medida, ángulo y linderos"""
        lados = []
        for vtx, rumbo, lado, mide, ang, lind in self.re_lados.findall(texto):
            lados.append({
                "vertice": vtx,
                "rumbo": rumbo,
                "lado": lado,
                "mide": mide.replace(",", "."),
                "angulo": ang,
                "linderos": lind.strip(),
            })
        return lados

    def extract_fecha(self, texto):
        m = self.re_fecha_larga.search(texto)
        if m:
            return f"{m.group(1)} de {m.group(2)}"
        m = self.re_fecha_corta.search(texto)
        return m.group(1) if m else "No especificado"

    def extract_inmueble(self, texto):
        m = self.re_inmueble.search(texto)
        return m.group(1).strip() if m else "No especificado"

    def extract_descripcion(self, texto):
        """Heurística simple: toma ‘DESCRIPCIÓN…’ si existe; si no, primeras ~800 chars."""
        m = re.search(r"(DESCRIPCIÓN[\s\-:]+[^\n]+)", texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return (self.texto_completo or "").strip()[:800]

    def extract_croquis(self, texto):
        """Extrae menciones de croquis si existen."""
        croquis_lines = []
        for line in texto.splitlines():
            if re.search(r"CROQUIS", line, re.IGNORECASE):
                croquis_lines.append(line.strip())
        return "\n".join(croquis_lines) if croquis_lines else "No especificado"
