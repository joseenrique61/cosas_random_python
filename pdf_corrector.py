import os
import shutil
from pathlib import Path
import fitz
import zipfile
from enum import Enum
from math import ceil, floor
from re import match


class ParagraphMode(Enum):
    TABULATION = 1
    VERTICAL_SEPARATION = 2


class ChapterMode(Enum):
    CENTERED = 1
    BOLD = 2
    BOTH = 3


def cambiar_ruta(funcion):
    def otra_funcion(nuevo_path, root, **kwargs):
        if not os.path.exists(nuevo_path):
            dividido = str(nuevo_path).split("\\")
            parcial = ""
            for carpeta in dividido:
                parcial += f"{carpeta}\\"
                if not os.path.exists(parcial):
                    os.mkdir(parcial.removesuffix("\\"))
        os.chdir(nuevo_path)
        if len(kwargs) > 0:
            result = funcion(kwargs)
        else:
            result = funcion()
        os.chdir(root)
        return result

    return otra_funcion


def leer_pdf(nombre_pdf: str, inicio: int, include_images: bool,
             _paragraph_mode: ParagraphMode, _chapter_mode: ChapterMode):
    with fitz.Document(nombre_pdf) as pdf:
        _capitulos = []
        completo = ""
        image_counter = 1
        images_xrefs = {}
        ultima_coordenada = 0
        last_was = "image"

        if (_paragraph_mode == ParagraphMode.VERTICAL_SEPARATION
                and input("¿Desea ingresar las coordenadas manualmente? Y/N ").upper() == "Y"):
            coordenadas = [int(input("Separación menor: ")), int(input("Separación mayor: "))]
        else:
            coordenadas = obtener_coordenadas(pdf, inicio, _paragraph_mode)

        for num_page, page in enumerate(pdf.pages(inicio), inicio):
            imagenes = page.get_images()
            if len(imagenes) > 0 and include_images:
                for imagen in imagenes:
                    if not imagen[0] in images_xrefs.keys():
                        images_xrefs[imagen[0]] = image_counter
                        pix = obtener_imagen(path_original, os.getcwd(), num=imagen[0], nombre_pdf=nombre_archivo)
                        guardar_imagen(path_images, os.getcwd(), pix=pix, num=image_counter, portada=False)
                        image_counter += 1

                    if not completo.endswith("</p>") and completo != "":
                        completo += "</p>"
                    completo += (f"<img src='images/img{images_xrefs[imagen[0]]}.jpg' "
                                 f"alt='Imagen {images_xrefs[imagen[0]]}' /><p>")
                    last_was = "image"

            for info in page.get_textpage().extractDICT()["blocks"]:
                if info["type"] == 0:
                    for line in info["lines"]:
                        for span in line["spans"]:
                            if span["text"] != "" and span["text"] != " ":
                                span["text"] = (span["text"].replace("&", "&amp;")
                                                .replace("<", "&lt;").replace(">", "&gt;"))

                                match _paragraph_mode:
                                    case ParagraphMode.TABULATION:
                                        nuevo_parrafo = coordenadas[0] < span["bbox"][0] < coordenadas[1]
                                    case ParagraphMode.VERTICAL_SEPARATION:
                                        nuevo_parrafo = (span["bbox"][1] -
                                                         ultima_coordenada >= coordenadas[1])
                                        ultima_coordenada = span["bbox"][1]

                                match _chapter_mode:
                                    case ChapterMode.BOLD:
                                        nuevo_capitulo = "BOLD" in span["font"].upper()
                                    case ChapterMode.CENTERED:
                                        nuevo_capitulo = (-0.5 < page.mediabox.x1 - span["bbox"][2] - span["bbox"][0]
                                                          < 0.5 and span["bbox"][0] > coordenadas[0])
                                    case ChapterMode.BOTH:
                                        nuevo_capitulo = ("BOLD" in span["font"].upper()
                                                          and -0.5 < page.mediabox.x1 - span["bbox"][2] -
                                                          span["bbox"][0] < 0.5 and span["bbox"][0] >
                                                          obtener_coordenadas(pdf, num_page,
                                                                              ParagraphMode.TABULATION)[0])

                                if nuevo_capitulo:
                                    titulo_bool = find_matches(pdf, num_page, span["text"], coordenadas, _chapter_mode)
                                    if titulo_bool:
                                        if last_was == "text" and completo != "":
                                            completo += "</p>"
                                            _capitulos.append(completo)
                                            completo = ""
                                        elif last_was == "image" and completo != "":
                                            completo = completo.removesuffix("<p>")
                                            _capitulos.append(completo)
                                            completo = ""
                                        completo = completo.removesuffix("<p>")
                                        completo += f"<h3>{span['text']}</h3><p>"
                                        last_was = "title"
                                    else:
                                        if not completo.endswith("</p>") and completo != "":
                                            completo += "</p>"
                                        completo += f"<p>{span['text']}"
                                        last_was = "text"
                                elif nuevo_parrafo:
                                    if not completo.endswith("</p>") and completo != "":
                                        completo += "</p>"
                                    completo += f"<p>{span['text']}"
                                    last_was = "text"
                                else:
                                    completo += f" {span['text']}"
                                    last_was = "text"

        _capitulos.append(completo.removesuffix("<p>"))
        return _capitulos


def find_matches(pdf: fitz.Document, inicio: int, string: str, coordenadas: list, _chapter_mode: ChapterMode):
    def iterar():
        _temp = ""
        bool1 = False
        empezado = False

        for page in pdf.pages(inicio, inicio + 1):
            for info in page.get_textpage().extractDICT()["blocks"]:
                if info["type"] == 0:
                    for line in info["lines"]:
                        for span in line["spans"]:
                            match _chapter_mode:
                                case ChapterMode.BOLD:
                                    bool1 = "BOLD" in span["font"].upper()
                                case ChapterMode.CENTERED:
                                    bool1 = (-0.5 < page.mediabox.x1 - span["bbox"][2] - span["bbox"][0] < 0.5
                                             and span["bbox"][0] > coordenadas[0])
                                case ChapterMode.BOTH:
                                    bool1 = ("BOLD" in span["font"].upper()
                                             and -0.5 < page.mediabox.x1 - span["bbox"][2] - span["bbox"][0] < 0.5
                                             and span["bbox"][0] >
                                             obtener_coordenadas(pdf, inicio, ParagraphMode.TABULATION)[0])
                            if bool1:
                                _temp += f' {span["text"]}'
                                empezado = True
                            elif not empezado:
                                continue
                            else:
                                return _temp
    temp = iterar()

    if match(r"\s?((CAP[IÍ]TULO)|(CHAPTER):?\s?[\dIVXLCDM]+)|(\b[\dIVXLCDM]+\b)", temp.upper()) is not None:
        return string in temp
    return False


def obtener_coordenadas(pdf: fitz.Document, inicio: int, _paragraph_mode: ParagraphMode):
    coordenadas = []
    ultima_coordenada = 0

    for page in pdf.pages(inicio + 1, inicio + 2):
        for num, info in enumerate(page.get_textpage().extractDICT()["blocks"]):
            if info["type"] == 0:
                for line in info["lines"]:
                    for span in line["spans"]:
                        match _paragraph_mode:
                            case ParagraphMode.TABULATION:
                                if ultima_coordenada != span["bbox"][1]:
                                    coordenadas.append(span["bbox"][0])
                            case ParagraphMode.VERTICAL_SEPARATION:
                                if span["text"] != "" and span["text"] != " ":
                                    coordenadas.append([round(span["bbox"][1]) - ultima_coordenada, span["text"]])
                        ultima_coordenada = round(span["bbox"][1])

    coordenadas_unicas = []
    for coordenada in coordenadas:
        if coordenada not in coordenadas_unicas:
            coordenadas_unicas.append(coordenada)
    coordenadas_unicas.sort()
    coordenadas_unicas = [floor(coordenadas_unicas[0]), ceil(coordenadas_unicas[1])]
    return coordenadas_unicas


@cambiar_ruta
def obtener_imagen(argumentos):
    if argumentos["num"] is None:
        with fitz.Document(argumentos["nombre_pdf"]) as pdf:
            pages = pdf.pages(0, 1)
            for page in pages:
                pix = pdf.extract_image(page.get_images()[0][0])
                return pix
    else:
        with fitz.Document(argumentos["nombre_pdf"]) as pdf:
            pix = pdf.extract_image(argumentos["num"])
            return pix


@cambiar_ruta
def guardar_imagen(argumentos):
    if argumentos["portada"]:
        with open("portada.jpg", "wb") as img:
            img.write(argumentos["pix"]["image"])
    else:
        with open(f"img{argumentos['num']}.jpg", "wb") as img:
            img.write(argumentos["pix"]["image"])


@cambiar_ruta
def pedir_libro():
    libros = os.listdir()
    opciones = "Seleccione el número de libro:\n"
    for i, libro in enumerate(libros):
        opciones += f"{i + 1}. {libro}\n"

    while True:
        try:
            resp = int(input(opciones))
            nombre = libros[resp - 1]
            _pagina_inicial = int(input("Ingrese el número de página de inicio: ")) - 1
            break
        except ValueError or IndexError:
            print("Ingrese una opción válida.")

    return nombre, _pagina_inicial


path_original = Path("C:/Users/USER/Documents/Libros/Original")
path_temp = Path("C:/Users/USER/Documents/Libros/temp")
path_convertido = Path("C:/Users/USER/Documents/Libros/Convertido")

nombre_archivo, pagina_inicial = pedir_libro(path_original, path_original)

path_libro = path_temp / nombre_archivo.strip(".pdf")
path_oebps = path_libro / "OEBPS"
path_meta_inf = path_libro / "META-INF"
path_images = path_oebps / "images"


def pedir_modos():
    paragraph_modes_options = """Ingrese el modo de párrafo:
    1. Tabulación
    2. Separación vertical desigual
    """
    chapter_modes_options = """Ingrese el modo de capítulo:
    1. Centrado
    2. Negrita
    3. Ambos
    """
    while True:
        try:
            _paragraph_mode = ParagraphMode(int(input(paragraph_modes_options)))
            _chapter_mode = ChapterMode(int(input(chapter_modes_options)))
            return _paragraph_mode, _chapter_mode
        except ValueError:
            print("Ingrese valores correctos.")


paragraph_mode, chapter_mode = pedir_modos()
capitulos = leer_pdf(nombre_archivo, pagina_inicial, input("¿Incluir imágenes? Y/N ").upper() == "Y",
                     paragraph_mode, chapter_mode)


def pedir_datos():
    _isbn = input('ISBN: ')
    _title = input('Título: ')
    _autor = input("Autor: ")
    _lenguaje = input("Lenguaje: ")

    return _isbn, _title, _autor, _lenguaje


isbn, titulo, autor, lenguaje = pedir_datos()


@cambiar_ruta
def create_mimetype():
    with open("mimetype", "w") as mimetype:
        mimetype.write("application/epub+zip")


@cambiar_ruta
def create_content():
    with open("content.opf", "w", encoding="utf-8") as content_opf:
        content_opf.write("<?xml version='1.0' encoding='UTF-8'?>")
        content_opf.write(f"<package xmlns='http://www.idpf.org/2007/opf' version='2.0' "
                          f"unique-identifier='{isbn}'>")
        content_opf.write(f"""  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{titulo}</dc:title>
        <dc:creator>{autor}</dc:creator>
        <dc:language>{lenguaje}</dc:language>
        <meta name="cover" content="portada.jpg"/>
    </metadata>""")

        manifest = """
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>"""

        types = {".jpg": "image/jpeg", ".xhtml": "application/xhtml+xml"}

        for base, dirs, archivos in os.walk(os.getcwd()):
            for archivo in archivos:
                nombre = archivo
                archivo = (base + "\\" + archivo).removeprefix(str(path_oebps) + "\\").replace("\\", "/")
                if archivo != "toc.ncx" and archivo != "cover.xhtml" and archivo != "content.opf":
                    manifest += f"""
        <item id="{nombre}" href="{archivo}" media-type="{types.get(os.path.splitext(nombre)[1])}"/>"""
                elif archivo == "cover.xhtml":
                    manifest += """
        <item id="cover.xhtml" href="cover.xhtml" media-type="application/xhtml+xml" properties="cover-image"/>"""

        spine = """
    <spine toc="ncx">
        <itemref idref="cover.xhtml"/>"""

        for i in range(len(capitulos)):
            spine += f"""
        <itemref idref="capitulo{i + 1}.xhtml"/>"""
        manifest += """
    </manifest>"""
        spine += """
    </spine>"""
        content_opf.write(manifest)
        content_opf.write(spine)
        content_opf.write('''
    <guide>
        <reference type="cover" title="Cover" href="cover.xhtml"/>
    </guide>
</package>''')


@cambiar_ruta
def create_ncx():
    with open("toc.ncx", "w", encoding="utf-8") as ncx:
        ncx.write('''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="{isbn}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{title}</text>
    </docTitle>''')

        contents = '    <navMap>'
        for i in range(len(capitulos)):
            contents += f'''
        <navPoint id="navPoint-{i + 1}" playOrder="{i + 1}">
            <navLabel>
                <text>Capítulo {i + 1}</text>
            </navLabel>
            <content src="capitulo{i + 1}.xhtml"/>
        </navPoint>'''
        ncx.write(contents)
        ncx.write("""
    </navMap>
</ncx>""")


@cambiar_ruta
def create_capitulos():
    for i, capitulo in enumerate(capitulos):
        with open(f"capitulo{i + 1}.xhtml", "w", encoding="utf-8") as text:
            text.write(f"<!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' "
                       f"'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>")
            text.write(f"""<html xmlns='http://www.w3.org/1999/xhtml' lang='en-US' xml:lang='en-US'>
        <head>
            <meta charset='utf-8'/>
            <title>{titulo}</title>
        </head>
        <body>
            {capitulo}
        </body>
</html>""")


@cambiar_ruta
def create_cover():
    pix = obtener_imagen(path_original, path_libro, nombre_pdf=nombre_archivo, num=None)
    guardar_imagen(path_images, path_oebps, pix=pix, portada=True)

    with open("cover.xhtml", "w", encoding="utf-8") as cover:
        cover.write('''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-US" xml:lang="en-US">
    <head>
        <title>Portada</title>
    </head>
    <body>
        <div epub:type="cover">
            <img src="images/portada.jpg" alt="Portada" />
        </div>
    </body>
</html>''')


@cambiar_ruta
def create_container():
    with open("container.xml", "w", encoding="utf-8") as container:
        container.write('''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>''')


@cambiar_ruta
def zip_book():
    nombre = f"{nombre_archivo.strip('.pdf')}.epub"
    with zipfile.ZipFile(nombre, "w", compression=zipfile.ZIP_STORED) as zipped:
        for base, dirs, archivos in os.walk(path_libro):
            for archivo in archivos:
                archivo = (base + "\\" + archivo).removeprefix(str(path_libro) + "\\")
                if archivo != nombre:
                    zipped.write(archivo)


def move_and_delete():
    shutil.move(path_libro / (nombre_archivo.strip(".pdf") + ".epub"), path_convertido /
                (nombre_archivo.strip(".pdf") + ".epub"))
    shutil.rmtree(nombre_archivo.strip(".pdf"))


create_mimetype(path_libro, path_libro)
create_capitulos(path_oebps, path_libro)
create_cover(path_oebps, path_libro)
create_content(path_oebps, path_libro)
create_container(path_meta_inf, path_libro)
create_ncx(path_oebps, path_libro)
zip_book(path_libro, path_temp)
move_and_delete()

print("Libro convertido.")
