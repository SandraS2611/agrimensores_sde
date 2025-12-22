
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, HeadingLevel, 
        AlignmentType, BorderStyle, WidthType, LevelFormat, PageBreak, Header, Footer, 
        PageNumber, ShadingType } = require('docx');

// Datos extraídos del plano
const datos = {
    objeto: "-27°27'48.99\"S ; -63°16'08.83\"O(B) -27°30'18.53\"S ; -63°17'05.36\"O(A) BARICENTRO GEOGRÁFICO: Ruta Provincial N°50 LUGAR CARTAVIO DEPARTAMENTO FIGUEROA RURAL URBANO NOMENCLATURA CATASTRAL MINISTERIO DE ECONOMIA PROVINCIA DE SANTIAGO DEL ESTERO DIRECCION GENERAL DE CATASTRO TOTAL L A - - M B - - N C - - O D - - P E - - A F-G-H-I-J-K- 4299Has 29As 79.14Cas 4299Has 29As 79.14Cas Sup. Cedida Para Camino VecinalR-S-T-U-C-V-W-X-Y-Q-R Fracc. 2 Ced. P/ Ruta Prov. N°50 Z-a-b-e-d-c-Z Fracc. 1 Ced. P/ Ruta Prov. N°50 o-f-g-n-o",
    lugar: "CARTAVIO DEPARTAMENTO FIGUEROA RURAL URBANO NOMENCLATURA CATASTRAL MINISTERIO DE ECONOMIA PROVINCIA DE SANTIAGO DEL ESTERO DIRECCION GENERAL DE CATASTRO TOTAL L A - - M B - - N C - - O D - - P E - - A F-G-H-I-J-K- 4299Has 29As 79.14Cas 4299Has 29As 79.14Cas Sup. Cedida Para Camino VecinalR-S-T-U-C-V-W-X-Y-Q-R Fracc. 2 Ced. P/ Ruta Prov. N°50 Z-a-b-e-d-c-Z Fracc. 1 Ced. P/ Ruta Prov. N°50 o-f-g-n-o",
    departamento: "FIGUEROA RURAL URBANO NOMENCLATURA CATASTRAL MINISTERIO DE ECONOMIA PROVINCIA DE SANTIAGO DEL ESTERO DIRECCION GENERAL DE CATASTRO TOTAL L A - - M B - - N C - - O D - - P E - - A F-G-H-I-J-K- 4299Has 29As 79.14Cas 4299Has 29As 79.14Cas Sup. Cedida Para Camino VecinalR-S-T-U-C-V-W-X-Y-Q-R Fracc. 2 Ced. P/ Ruta Prov. N°50 Z-a-b-e-d-c-Z Fracc. 1 Ced. P/ Ruta Prov. N°50 o-f-g-n-o",
    fecha: "16/02/2024",
    instrumental: "No especificado",
    propietarios: [{ nombre: "Julian Vital, Andrea Marcela", dni: "22.242.021", cuil: "27-22242021-6" },{ nombre: "Julian, Luis Humberto", dni: "07.203.770", cuil: "20-07203770-8" },{ nombre: "Julian, Ramiro Daniel", dni: "27.185.603", cuil: "20-27185603-3" },{ nombre: "Julian, Jorge Armando", dni: "12.974.435", cuil: "23-12974435-9" },{ nombre: "Julian Vital, Ernesto Abdala", dni: "12.387.442", cuil: "20-12387442-9" },{ nombre: "Julian VItal, Pedro Humberto", dni: "20.564.542", cuil: "20-20564542-0" },{ nombre: "Julian de Maffini, Maria Ynes", dni: "11.162.412", cuil: "27-11162412-2" },{ nombre: "Julian de Salas, Olga Mabel", dni: "10.450.548", cuil: "27-10450548-7" }],
    lotes: [{ nombre: "LOTE U-2", has: "5", as: "43", cas: "30.94" },{ nombre: "LOTE U-1", has: "105", as: "58", cas: "22.39" },{ nombre: "LOTE U-6", has: "268", as: "91", cas: "83.57" },{ nombre: "LOTE U-5", has: "5", as: "43", cas: "30.94" }],
    colindantes: [{ lote: "Lote 3", propietario: "Pedro Herrera Serrano y Otros" },{ lote: "Lote 3", propietario: "Pedro Herrera Serrano y Otros" },{ lote: "Lote 3", propietario: "Pedro Herrera Serrano y Otros" },{ lote: "Lote 1", propietario: "Pedro Herrera Serrano y Otros" }]
};

// Crear documento
const doc = new Document({
    styles: {
        default: { 
            document: { 
                run: { font: "Arial", size: 24 } 
            } 
        },
        paragraphStyles: [
            {
                id: "Title",
                name: "Title",
                basedOn: "Normal",
                run: { size: 56, bold: true, color: "1F4788", font: "Arial" },
                paragraph: { spacing: { before: 240, after: 240 }, alignment: AlignmentType.CENTER }
            },
            {
                id: "Heading1",
                name: "Heading 1",
                basedOn: "Normal",
                run: { size: 32, bold: true, color: "1F4788", font: "Arial" },
                paragraph: { spacing: { before: 480, after: 240 }, outlineLevel: 0 }
            },
            {
                id: "Heading2",
                name: "Heading 2",
                basedOn: "Normal",
                run: { size: 28, bold: true, color: "2E75B5", font: "Arial" },
                paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 1 }
            }
        ]
    },
    numbering: {
        config: [
            {
                reference: "bullet-list",
                levels: [{
                    level: 0,
                    format: LevelFormat.BULLET,
                    text: "•",
                    alignment: AlignmentType.LEFT,
                    style: { paragraph: { indent: { left: 720, hanging: 360 } } }
                }]
            }
        ]
    },
    sections: [{
        properties: {
            page: {
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [
                    new Paragraph({
                        alignment: AlignmentType.RIGHT,
                        children: [
                            new TextRun({
                                text: "Memoria Descriptiva - " + datos.lugar,
                                size: 20,
                                color: "666666"
                            })
                        ]
                    })
                ]
            })
        },
        footers: {
            default: new Footer({
                children: [
                    new Paragraph({
                        alignment: AlignmentType.CENTER,
                        children: [
                            new TextRun({ text: "Página ", size: 20 }),
                            new TextRun({ children: [PageNumber.CURRENT], size: 20 }),
                            new TextRun({ text: " de ", size: 20 }),
                            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20 })
                        ]
                    })
                ]
            })
        },
        children: [
            // PORTADA
            new Paragraph({
                heading: HeadingLevel.TITLE,
                children: [new TextRun("MEMORIA DESCRIPTIVA")]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 120, after: 480 },
                children: [new TextRun({
                    text: datos.objeto,
                    size: 28,
                    bold: true,
                    color: "2E75B5"
                })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 240 },
                children: [new TextRun({
                    text: "Lugar: " + datos.lugar,
                    size: 24
                })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 240 },
                children: [new TextRun({
                    text: "Departamento: " + datos.departamento,
                    size: 24
                })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 960 },
                children: [new TextRun({
                    text: "Provincia de Santiago del Estero",
                    size: 24,
                    italics: true
                })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({
                    text: "Fecha: " + datos.fecha,
                    size: 22
                })]
            }),
            
            // SALTO DE PÁGINA
            new Paragraph({ children: [new PageBreak()] }),
            
            // 1. IDENTIFICACIÓN
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("1. IDENTIFICACIÓN DEL INMUEBLE")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Lugar: " + datos.lugar)]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Departamento: " + datos.departamento)]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Provincia: Santiago del Estero")]
            }),
            
            // 2. OBJETO
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("2. OBJETO DEL TRÁMITE")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun(datos.objeto)]
            }),
            
            // 3. TITULARES
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("3. TITULARES DEL DOMINIO")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Se identifican los siguientes propietarios condóminos:")]
            }),
            
            // Lista de propietarios
            ...datos.propietarios.map(prop => 
                new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun(prop.nombre + " - DNI: " + prop.dni + " - CUIL: " + prop.cuil)]
                })
            ),
            
            // 4. ANTECEDENTES DOMINIALES
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 480 },
                children: [new TextRun("4. ANTECEDENTES DOMINIALES")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun("Los inmuebles a unificar y dividir cuentan con los siguientes antecedentes de dominio debidamente inscriptos en el Registro correspondiente.")]
            }),
            
            // 5. DESCRIPCIÓN TÉCNICA
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("5. DESCRIPCIÓN TÉCNICA")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("5.1. Instrumental Utilizado")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun(datos.instrumental)]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("5.2. Sistema de Coordenadas")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun("Sistema: POSGAR 2007 - Proyección Gauss-Krüger")]
            }),
            
            // SALTO DE PÁGINA
            new Paragraph({ children: [new PageBreak()] }),
            
            // 6. UNIFICACIÓN
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("6. UNIFICACIÓN DE PARCELAS")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun("Se unifican los inmuebles originales formando una única parcela denominada LOTE U, conforme a las medidas y superficies que se detallan en la documentación gráfica adjunta.")]
            }),
            
            // 7. DIVISIÓN
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("7. DIVISIÓN DE LA PARCELA UNIFICADA")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("La parcela unificada (LOTE U) se divide en las siguientes fracciones:")]
            }),
            
            // Lista de lotes resultantes
            ...datos.lotes.map(lote => 
                new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun(lote.nombre + " - Superficie: " + lote.has + " Has " + lote.as + " As " + lote.cas + " Cas")]
                })
            ),
            
            // 8. COLINDANCIAS
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                spacing: { before: 480 },
                children: [new TextRun("8. COLINDANCIAS")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("El inmueble colinda con las siguientes propiedades:")]
            }),
            
            // Lista de colindantes
            ...datos.colindantes.slice(0, 10).map(col => 
                new Paragraph({
                    numbering: { reference: "bullet-list", level: 0 },
                    children: [new TextRun(col.lote + " - " + col.propietario)]
                })
            ),
            
            // SALTO DE PÁGINA
            new Paragraph({ children: [new PageBreak()] }),
            
            // 9. CUMPLIMIENTO NORMATIVO
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("9. CUMPLIMIENTO NORMATIVO")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("9.1. Código de Aguas (Ley 4.869)")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Se declara que el presente trabajo se ajusta a las disposiciones del Código de Aguas de la Provincia en lo referente a derechos de agua, concesiones y servidumbres hídricas.")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("9.2. Código Rural (Ley 1.734)")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Se respetan las disposiciones del Código Rural en materia de alambrados, caminos vecinales y demás obligaciones establecidas.")]
            }),
            new Paragraph({
                heading: HeadingLevel.HEADING_2,
                children: [new TextRun("9.3. Normativa Catastral")]
            }),
            new Paragraph({
                spacing: { after: 240 },
                children: [new TextRun("El presente trabajo se ajusta a las disposiciones de la Ley Provincial de Catastro N° 6.339 y sus reglamentaciones.")]
            }),
            
            // 10. OBSERVACIONES
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("10. OBSERVACIONES")]
            }),
            new Paragraph({
                spacing: { after: 120 },
                children: [new TextRun("Se respetaron linderos y hechos antiguos, no afectándose inmuebles colindantes. Las medidas y superficies consignadas surgen de las operaciones de mensura realizadas en el terreno con el instrumental detallado.")]
            }),
            
            // 11. CONCLUSIÓN
            new Paragraph({
                heading: HeadingLevel.HEADING_1,
                children: [new TextRun("11. CONCLUSIÓN")]
            }),
            new Paragraph({
                spacing: { after: 480 },
                children: [new TextRun("Se ha procedido a la mensura, unificación y división del inmueble conforme a lo solicitado por los titulares del dominio, respetando la normativa vigente y los derechos de terceros. La presente memoria descriptiva se presenta ante las autoridades competentes para su aprobación.")]
            }),
            
            // FIRMA
            new Paragraph({
                spacing: { before: 960, after: 240 },
                children: [new TextRun({
                    text: "Lugar y fecha: " + datos.lugar + ", " + datos.fecha,
                    size: 22
                })]
            }),
            new Paragraph({
                spacing: { before: 480 },
                alignment: AlignmentType.CENTER,
                children: [new TextRun({
                    text: "_______________________________",
                    size: 22
                })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({
                    text: "Firma y Sello del Profesional",
                    size: 22,
                    bold: true
                })]
            })
        ]
    }]
});

// Generar el archivo
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("C:\\Users\\Lohany\\Documents\\agrimensores_sde\\media\\outputs\\memorias\\Memoria_3_20251216_123054.docx", buffer);
    console.log("Memoria descriptiva generada exitosamente");
}).catch(err => {
    console.error("Error generando documento:", err);
    process.exit(1);
});
