from plantuml import PlantUML
import re
import os

def diagram_builder(PlantUML_str, diagram_name):
    # Configurar el servidor PlantUML para generar SVG
    servidor = PlantUML(url='http://www.plantuml.com/plantuml/svg/')

    # Procesar el código PlantUML y obtener el contenido generado
    respuesta = servidor.processes(PlantUML_str)

    # Guardar el contenido generado en un archivo local con extensión .svg
    nombre_archivo = f'{diagram_name}.svg'
    with open(nombre_archivo, 'wb') as archivo:
        archivo.write(respuesta)

    # Modificar el SVG para establecer width="100%" y height="auto"
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        contenido_svg = archivo.read()

    # Actualizar los atributos width y height en la etiqueta <svg>
    contenido_svg = re.sub(
        r'(<svg[^>]*?)\s(width|height)="[^"]*"',  # Encontrar atributos width y height existentes
        r'\1',  # Eliminar los atributos encontrados
        contenido_svg  # Aplicar el cambio al contenido
    )
    contenido_svg = re.sub(
        r'(<svg[^>]*?)>',  # Encontrar el inicio de la etiqueta <svg>
        r'\1 width="100%" height="auto">',  # Añadir los nuevos atributos
        contenido_svg
    )

    # Guardar el archivo SVG modificado
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write(contenido_svg)

    return nombre_archivo

def contains_plantuml(prompt):
    """
    Verifica si el prompt contiene código PlantUML.

    Args:
        prompt (str): El texto del prompt.

    Returns:
        bool: True si contiene PlantUML, False de lo contrario.
    """
    # Busca bloques de código delimitados por ```puml o etiquetas @startuml
    plantuml_pattern = re.compile(r'```puml|@startuml', re.IGNORECASE)
    return bool(plantuml_pattern.search(prompt))

def extract_plantuml(prompt):
    """
    Extrae el código PlantUML del prompt.

    Args:
        prompt (str): El texto del prompt.

    Returns:
        str: El código PlantUML extraído.
    """
    # Busca bloques de código delimitados por ```puml ... ```
    code_block_pattern = re.compile(r'```puml\n(.*?)\n```', re.DOTALL | re.IGNORECASE)
    match = code_block_pattern.search(prompt)
    if match:
        return match.group(1).strip()
    
    # Si no hay bloques de código, busca etiquetas @startuml y @enduml
    uml_pattern = re.compile(r'@startuml(.*?)@enduml', re.DOTALL | re.IGNORECASE)
    match = uml_pattern.search(prompt)
    if match:
        return match.group(1).strip()
    
    return ""

def remove_plantuml(prompt):
    """
    Elimina el código PlantUML del prompt, dejando únicamente la explicación.

    Args:
        prompt (str): El texto del prompt que incluye el código PlantUML.

    Returns:
        str: El texto del prompt sin el código PlantUML.
    """
    # Elimina bloques de código delimitados por ```puml ... ```
    prompt = re.sub(r'```puml\n.*?\n```', '', prompt, flags=re.DOTALL | re.IGNORECASE)
    
    # Elimina bloques de código entre @startuml y @enduml
    prompt = re.sub(r'@startuml.*?@enduml', '', prompt, flags=re.DOTALL | re.IGNORECASE)
    
    # Limpia espacios innecesarios y retorna el texto restante
    return prompt.strip()

def diagram_injector(svg_file, explanation):
    """
    Busca un archivo .svg en el directorio raíz con el nombre basado en el id,
    extrae su contenido, lo inyecta en un HTML stringificado y elimina el archivo SVG.
    
    Args:
        svg_file (str): El nombre del archivo SVG.
        explanation (str): Explicación que se añadirá al HTML.
    
    Returns:
        str: HTML stringificado con el contenido del archivo SVG.
    """
    # Verificar si el archivo SVG existe
    if not os.path.isfile(svg_file):
        raise FileNotFoundError(f"El archivo {svg_file} no existe en el directorio raíz.")

    # Leer el contenido del archivo SVG
    with open(svg_file, "r", encoding="utf-8") as file:
        svg_content = file.read()

    # Eliminar el archivo después de leerlo
    try:
        os.remove(svg_file)
    except Exception as e:
        raise RuntimeError(f"No se pudo eliminar el archivo {svg_file}. Error: {e}")

    # Plantilla HTML básica con el contenido del SVG inyectado
    html_template = f"""
    <body>
        <div class="svg-container">
            {svg_content}
        </div>
        <p class="message" style="max-width: 100%!important">
            {explanation}
        </p>
    </body>
    """
    
    return html_template

def save_html_to_root(html_content, filename="output.html"):
    """
    Guarda un HTML stringificado como un archivo en el directorio raíz.
    
    Args:
        html_content (str): Contenido HTML en formato string.
        filename (str): Nombre del archivo HTML a crear. Por defecto es 'output.html'.
    
    Returns:
        str: Ruta completa del archivo HTML creado.
    """
    # Construir la ruta del archivo en el directorio actual (raíz)
    file_path = os.path.join(os.getcwd(), filename)

    try:
        # Escribir el contenido HTML en el archivo
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(html_content)
    except Exception as e:
        raise RuntimeError(f"Error al guardar el archivo HTML: {e}")

    return file_path
