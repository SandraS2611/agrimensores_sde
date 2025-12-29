"""
Procesador de PDFs de planos de agrimensura
"""

import pdfplumber
import re
import logging
import pytesseract
from pdf2image import convert_from_path

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Procesa archivos PDF de planos y extrae información relevante"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.texto_completo = None

        # Compilar regex de encabezados básicos
        self.re_objeto = re.compile(r"OBJETO[:\s]+([^\n]+)", re.IGNORECASE)
        self.re_lugar = re.compile(r"LUGAR[:\s]+([^\n]+)", re.IGNORECASE)
        self.re_departamento = re.compile(r"DEPARTAMENTO[:\s]+([^\n]+)", re.IGNORECASE)

        # Propietarios (DNI/CUIL)
        self.re_propietarios = re.compile(
            r"([A-ZÁÉÍÓÚÑ\s,\.\(\)]+?)\s+D\.N\.I\.[:\s]*([\d\.]+)\s*C\.U\.I\.L\.[:\s]*([\d\-]+)",
            re.IGNORECASE
        )

        # Dominios (variantes comunes)
        self.re_dominios = re.compile(
            r"(M\.?\s*F\.?\s*R\.?\s*[\d\-\/]+|MFR\s*[\d\-\/]+|Mat\.?\s*F°R°\s*[\d\-\/]+|Matrícula\s*[\d\-\/]+)",
            re.IGNORECASE,
        )

        # Padrón
        self.re_padron = re.compile(r"PADR[ÓO]N[:\s]+([\d\-]+)", re.IGNORECASE)

        # Superficies (Has/As/Cas)
        self.re_superficies = re.compile(r"(\d+)\s*Has\s*(\d+)\s*As\s*([\d\.]+)\s*Cas")

        # Lados simples tipo "4-5=2117.00"
        self.re_lados_simple = re.compile(r"(\d+-\d+)\s*=\s*([\d.,]+)")

        # Coordenadas POSGAR (tabla sin símbolos)
        self.re_coordenadas_tabla = re.compile(
            r"""
            ^\s*
            (?P<punto>[A-Z]{1,6}\.?[0-9]*)                  # VERT.1 / VINC. / P / A...
            \s+
            (?P<lat_deg>-?\d{1,2})\s+(?P<lat_min>\d{1,2})\s+(?P<lat_sec>\d{1,2}\.\d+)
            \s+
            (?P<lon_deg>-?\d{1,3})\s+(?P<lon_min>\d{1,2})\s+(?P<lon_sec>\d{1,2}\.\d+)
            \s+
            (?P<norte>[0-9.,]+)
            \s+
            (?P<este>[0-9.,]+)
            """,
            re.MULTILINE | re.VERBOSE
        )

        # Coordenadas DMS con símbolos y cardinales
        self.re_coordenadas_dms_simbolos = re.compile(
            r"""
            (?P<punto>[A-Z]{1,6}\.?[0-9]*)?\s*
            (?P<lat>-?\d{1,2}\s*°\s*\d{1,2}\s*'\s*\d{1,2}\.\d+\s*"\s*[NS])\s*[,;]?\s*
            (?P<lon>-?\d{1,3}\s*°\s*\d{1,2}\s*'\s*\d{1,2}\.\d+\s*"\s*[EO])
            (?:\s*[,;]?\s*NORTE\s*GK\s*[:=]?\s*(?P<norte>[0-9.,]+))?
            (?:\s*[,;]?\s*ESTE\s*GK\s*[:=]?\s*(?P<este>[0-9.,]+))?
            """,
            re.IGNORECASE | re.VERBOSE
        )

        # Coordenadas DMS sin símbolos (espacios) y cardinales
        self.re_coordenadas_dms_espacios = re.compile(
            r"""
            (?P<punto>[A-Z]{1,6}\.?[0-9]*)?\s*
            (?P<lat>-?\d{1,2}\s+\d{1,2}\s+\d{1,2}\.\d+\s*[NS])\s*[,;]?\s*
            (?P<lon>-?\d{1,3}\s+\d{1,2}\s+\d{1,2}\.\d+\s*[EO])
            (?:\s*[,;]?\s*NORTE\s*GK\s*[:=]?\s*(?P<norte>[0-9.,]+))?
            (?:\s*[,;]?\s*ESTE\s*GK\s*[:=]?\s*(?P<este>[0-9.,]+))?
            """,
            re.IGNORECASE | re.VERBOSE
        )

        # Notas y referencias
        self.re_nota1 = re.compile(
            r"NOTA\s*1[\s\S]+?(?=NOTA\s*2|REFERENCIAS|COORDENADAS|$)", re.IGNORECASE
        )
        self.re_nota2 = re.compile(
            r"NOTA\s*2[\s\S]+?(?=REFERENCIAS|COORDENADAS|$)", re.IGNORECASE
        )
        self.re_referencias = re.compile(
            r"REFERENCIAS[\s\S]+?(?=NOTA|COORDENADAS|$)", re.IGNORECASE
        )

        # Fechas
        self.re_fecha_larga = re.compile(
            r"(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóú]+)\s+de\s+(\d{4})"
        )
        self.re_fecha_corta = re.compile(r"(\d{2}/\d{2}/\d{4})")

        # Inmueble
        self.re_inmueble = re.compile(r"Inmueble[:\s]+([^\n]+)", re.IGNORECASE)

    def extract_text(self):
        """Extrae texto del PDF, usando OCR si es necesario"""
        try:
            texto = ""
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        page_text = page_text.replace("\xa0", " ")
                        page_text = re.sub(r"[ \t]+", " ", page_text)
                        texto += page_text.strip() + "\n"

            # Si no se extrajo nada, aplicar OCR
            if not texto.strip():
                logger.info("No se encontró texto embebido, aplicando OCR...")
                images = convert_from_path(self.pdf_path)
                for img in images:
                    texto += pytesseract.image_to_string(img, lang="spa") + "\n"

            self.texto_completo = texto
            return texto
        except Exception as e:
            logger.error(f"Error crítico en PDF/OCR: {str(e)}")
            return ""

    def _clean_field(self, text, keywords_to_stop):
        if not text:
            return ""
        for word in keywords_to_stop:
            if word.upper() in text.upper():
                parts = re.split(rf"{re.escape(word)}", text, flags=re.IGNORECASE)
                text = parts[0]
        return text.strip()

    def extract_data(self):
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
            "coordenadas": self.extract_coordenadas(texto),
            "inmueble": self._clean_field(self.extract_inmueble(texto), stop_words),
            "descripcion": self.extract_descripcion(texto),
            "croquis": self.extract_croquis(texto),
            "nota1": self.extract_nota1(texto),
            "nota2": self.extract_nota2(texto),
            "referencias": self.extract_referencias(texto),
            "texto_completo": texto.strip(),
        }
        logger.debug("Datos procesados: %s", datos)
        return datos

    # Métodos de extracción individuales
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
        """Devuelve superficies como lista de diccionarios normalizados"""
        superficies = []
        for h, a, c in self.re_superficies.findall(texto):
            superficies.append(
                {
                    "designacion": "No especificado",
                    "sup_titulo": f"{h} Has {a} As {c} Cas",
                    "sup_mensura": "",
                    "diferencia": "",
                    "observaciones": "",
                }
            )
        # Deduplicación
        dedup, seen = [], set()
        for s in superficies:
            key = (s["designacion"], s["sup_titulo"], s["sup_mensura"], s["diferencia"])
            if key not in seen:
                seen.add(key)
                dedup.append(s)
        return dedup

    def extract_lados_mejorado(self, texto):
        lados = []
        for lado, medida in self.re_lados_simple.findall(texto):
            lados.append(
                {
                    "vertice": lado.split("-")[0],
                    "rumbo": "",
                    "lado": lado,
                    "mide": medida.replace(",", "."),
                    "angulo": "",
                    "linderos": "",
                }
            )
        return lados

    def extract_coordenadas(self, texto):
        """
        Extrae coordenadas POSGAR 07 desde:
          - Tabla estilo POSGAR (VERT.1 -27 26 21.33563 -63 15 07.30983 6965637.114 4475082.623)
          - Líneas DMS con símbolos º ' " y cardinales (S/O/N/E)
          - Líneas DMS con espacios y cardinales
        Normaliza Norte/Este (coma -> punto), deduplica por (punto, latitud, longitud).
        """
        coords = []

        def _norm_num(s):
            if not s:
                return ""
            return re.sub(r"\s+", "", s).replace(",", ".")

        def _to_dms_string(deg, min_, sec, cardinal=None):
            base = f"{deg}°{min_}'{sec}\""
            return f"{base}{cardinal or ''}"

        # 1) Formato tabla POSGAR
        for m in self.re_coordenadas_tabla.finditer(texto):
            lat = _to_dms_string(m.group("lat_deg"), m.group("lat_min"), m.group("lat_sec"))
            lon = _to_dms_string(m.group("lon_deg"), m.group("lon_min"), m.group("lon_sec"))
            coords.append({
                "punto": m.group("punto"),
                "latitud": lat,
                "longitud": lon,
                "norte_gk": _norm_num(m.group("norte")),
                "este_gk": _norm_num(m.group("este")),
                "observacion": ""
            })

        # 2) DMS con símbolos y cardinales
        for m in self.re_coordenadas_dms_simbolos.finditer(texto):
            coords.append({
                "punto": (m.group("punto") or "").strip(),
                "latitud": m.group("lat").replace(" ", ""),
                "longitud": m.group("lon").replace(" ", ""),
                "norte_gk": _norm_num(m.group("norte") or ""),
                "este_gk": _norm_num(m.group("este") or ""),
                "observacion": ""
            })

        # 3) DMS con espacios y cardinales
        for m in self.re_coordenadas_dms_espacios.finditer(texto):
            coords.append({
                "punto": (m.group("punto") or "").strip(),
                "latitud": re.sub(r"\s+", "", m.group("lat")),
                "longitud": re.sub(r"\s+", "", m.group("lon")),
                "norte_gk": _norm_num(m.group("norte") or ""),
                "este_gk": _norm_num(m.group("este") or ""),
                "observacion": ""
            })

        # Deduplicación por (punto, latitud, longitud)
        dedup, seen = [], set()
        for c in coords:
            key = (c.get("punto", ""), c.get("latitud", ""), c.get("longitud", ""))
            if key in seen:
                continue
            seen.add(key)
            dedup.append(c)

        return dedup

    def extract_fecha(self, texto):
        """Extrae fecha de operaciones en formato 'dd/mm/yyyy' o 'dd de Mes de yyyy'"""
        m = self.re_fecha_larga.search(texto)
        if m:
            return f"{m.group(1)} de {m.group(2)}"
        m = self.re_fecha_corta.search(texto)
        return m.group(1) if m else "No especificado"

    def extract_inmueble(self, texto):
        """Extrae texto posterior a 'Inmueble:' en la misma línea"""
        m = self.re_inmueble.search(texto)
        return m.group(1).strip() if m else "No especificado"

    def extract_descripcion(self, texto):
        """Narrativa básica: usa sección explícita o compone con lados encontrados"""
        m = re.search(r"(DESCRIPCIÓN[\s\-:]+[^\n]+)", texto, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        lados = self.re_lados_simple.findall(texto)
        if lados:
            partes = [f"{lado} = {medida.replace(',', '.')}" for lado, medida in lados[:10]]
            return " ; ".join(partes)
        return (self.texto_completo or "").strip()[:800]

    def extract_croquis(self, texto):
        """Extrae segmento de 'CROQUIS' hasta el siguiente encabezado conocido"""
        m = re.search(
            r"(CROQUIS[\s\S]+?)(?:NOTA|DIRECCION|COORDENADAS|\Z)", texto, re.IGNORECASE
        )
        if m:
            segmento = m.group(1).strip()
            return re.sub(r"\s{2,}", " ", segmento)
        # fallback: líneas con ‘CROQUIS’
        croquis_lines = []
        for line in texto.splitlines():
            if re.search(r"CROQUIS", line, re.IGNORECASE):
                croquis_lines.append(line.strip())
        return "\n".join(croquis_lines) if croquis_lines else "No especificado"

    def extract_nota1(self, texto):
        """Extrae bloque de NOTA 1"""
        m = self.re_nota1.search(texto)
        if m:
            return m.group(0).strip()
        m2 = re.search(
            r"(NOTA\s*1[\s\S]+?)(?:NOTA\s*2|REFERENCIAS|COORDENADAS|$)",
            texto,
            re.IGNORECASE,
        )
        return m2.group(1).strip() if m2 else ""

    def extract_nota2(self, texto):
        """Extrae bloque de NOTA 2"""
        m = self.re_nota2.search(texto)
        if m:
            return m.group(0).strip()
        m2 = re.search(
            r"(NOTA\s*2[\s\S]+?)(?:REFERENCIAS|COORDENADAS|$)", texto, re.IGNORECASE
        )
        return m2.group(1).strip() if m2 else ""

    def extract_referencias(self, texto):
        """Extrae bloque de referencias y limpia espacios repetidos"""
        m = self.re_referencias.search(texto)
        if m:
            bloque = m.group(0)
            return re.sub(r"\s{2,}", " ", bloque).strip()
        # fallback: listar palabras clave detectadas
        keys = []
        for line in texto.splitlines():
            if re.search(
                r"(LINEA DE MENSURA|LINEA AUXILIAR|HUELLA|ALAMBRADO|MONTE|POSTE|CASAS\-GALPONES|CASAS|GALPONES)",
                line,
                re.IGNORECASE,
            ):
                keys.append(line.strip())
        return "\n".join(keys)


def generar_memoria(datos):
    partes = []

    # Encabezado
    partes.append("MEMORIA DESCRIPTIVA")
    partes.append(f"Departamento: {datos.get('departamento', '')}")
    partes.append(f"Padrón: {', '.join(datos.get('padrones', []))}")
    partes.append(f"Lugar: {datos.get('lugar', '')}")
    if datos.get("dominios"):
        partes.append(f"Dominio: {datos['dominios'][0].get('matricula', '')}")
    partes.append(f"Baricentro geográfico: {datos.get('baricentro', '')}")
    partes.append(f"Objeto: {datos.get('objeto', '')}")
    partes.append(f"Inmueble: {datos.get('inmueble', '')}")
    if datos.get("propietarios"):
        partes.append(f"Titular: {datos['propietarios'][0].get('nombre', '')}")
    partes.append(f"Fecha de operación: {datos.get('fecha_operaciones', '')}")

    # Extracto de título
    partes.append("\nExtracto de título")
    if datos.get("dominios"):
        partes.append(f"Dominio: {datos['dominios'][0].get('matricula', '')}")
    partes.append(f"Inmueble: {datos.get('inmueble', '')}")
    partes.append("Medidas y linderos: Según plano de mensura")

    # Planilla de superficies
    partes.append("\nPlanilla de superficies")
    partes.append("Lote\tPolígono\tSup. s/Título\tSup. s/Mensura\tDiferencia\tObservaciones")
    for sup in datos.get("superficies", []):
        partes.append(
            f"{sup.get('designacion', '')}\t\t{sup.get('sup_titulo', '')}\t"
            f"{sup.get('sup_mensura', '')}\t{sup.get('diferencia', '')}\t"
            f"{sup.get('observaciones', '')}"
        )

    # Lados
    partes.append("\nPlanilla de lados del polígono principal")
    partes.append("Vértice\tLado\tMide (m)\tObservaciones")
    for lado in datos.get("lados", []):
        partes.append(
            f"{lado.get('vertice', '')}\t{lado.get('lado', '')}\t"
            f"{lado.get('mide', '')}\t{lado.get('linderos', '')}"
        )

    # Coordenadas
    partes.append("\nCoordenadas geodésicas POSGAR 07")
    partes.append("Punto\tLatitud\tLongitud\tNorte GK\tEste GK\tObserv.")
    for c in datos.get("coordenadas", []):
        partes.append(
            f"{c.get('punto', '')}\t{c.get('latitud', '')}\t{c.get('longitud', '')}\t"
            f"{c.get('norte_gk', '')}\t{c.get('este_gk', '')}\t{c.get('observacion', '')}"
        )

    # Notas
    partes.append("\nNotas oficiales y referencias")
    partes.append(f"Nota 1: {datos.get('nota1', '')}")
    partes.append(f"Nota 2: {datos.get('nota2', '')}")
    partes.append(f"Referencias: {datos.get('referencias', '')}")

    partes.append("\nCon esto se dan por finalizadas las operaciones de mensura y división.")
    partes.append(f"Santiago del Estero, {datos.get('fecha_operaciones', '')}")

    return "\n".join(partes)


def validar_datos(datos):
    faltantes = []
    for campo, valor in datos.items():
        if isinstance(valor, str):
            if valor.strip() in ["", "No especificado"]:
                faltantes.append(campo)
        elif isinstance(valor, list):
            if len(valor) == 0:
                faltantes.append(campo)
        elif valor is None:
            faltantes.append(campo)
    return faltantes
