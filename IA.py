from diagram_functions import diagram_builder, remove_plantuml, diagram_injector
from openai import OpenAI
from loaders import SpinningLoader
import json
import time
import re
import os

def ask_IA(prompt, thread_id = None):
    """
        Recibe an input parameter that consist on PLANTUML code 
        and return a binary that correspond a UML diagram builded 
        for the function to display the requestd diarma throught 
        the PLANTUML code
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ASSISTANT_ID= os.getenv("ASSISTANT_ID")
    print('OPENAI_API_KEY', OPENAI_API_KEY )
    print('ASSISTANT_ID', ASSISTANT_ID )
    loader = SpinningLoader()
    print("Inicializando Consulta... \n")
    loader.start()
    
    api_key = OPENAI_API_KEY

    client = OpenAI(
        api_key=api_key
    )

    thread = None
    if(thread_id is None):
        # Crea un nuevo thread
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role='user',
            content=prompt,
        )

    else:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role='user',
            content=prompt,
        )

    # Crea un run para generar la respuesta del asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )

    loader.stop()
    print("En espera de respuesta Asistente... \n")
    loader.start()
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == 'completed':
            loader.stop()
            print("Respuesta obtenida... \n")
            loader.start()

            messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
            while True:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status == 'completed':
                    break       
            return {
                        "thread_id": thread_id if thread_id is not None else thread.id,
                        "resp": response_formater(
                                    erase_source_labels(
                                        remove_plantuml(
                                            messages.data[0].content[0].text.value
                                        )
                                    )
                                )
                    }         
        
        elif run.status == 'failed':
            print('\n',run,'\n')
            return  {
                        "thread_id": thread_id if thread_id is not None else thread.id,
                        "resp": "¡Ocurrió un error!, por favor volver a consultar"
                    }   
        elif run.status == 'requires_action':
            

            function_to_be_called = run.required_action.submit_tool_outputs.tool_calls[0].function.name
            arguments =  run.required_action.submit_tool_outputs.tool_calls[0].function.arguments
            if function_to_be_called == "diagram_builder":
                loader.stop()
                print("Generando Diagrama... \n")
                loader.start()
                args = json.loads(arguments)
                PlantUML_code = args["prompt"]
                diagram_id = diagram_builder(PlantUML_code, run.id)

                call_id = run.required_action.submit_tool_outputs.tool_calls[0].id

                run = client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[
                        {
                            "tool_call_id": call_id,
                            "output": ""
                        }
                    ]
                )
                loader.stop()
                print("Solicitando explicación Diagrama... \n")
                loader.start()
                while True:
                    run = client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )

                    if run.status == 'completed':

                        # Instrucciones claras para evitar llamadas a funciones
                        client.beta.threads.messages.create(
                            thread_id=thread.id,
                            role='user',
                            content=f"{prompt}. Por favor, explica con palabras lo que se consulta, sin incluir código ni realizar llamadas a funciones.",
                        )

                        # Crea un nuevo run
                        run = client.beta.threads.runs.create(
                            thread_id=thread.id,
                            assistant_id=ASSISTANT_ID
                        )

                        # Espera a que el run se complete
                        while True:
                            run = client.beta.threads.runs.retrieve(
                                thread_id=thread.id,
                                run_id=run.id
                            )

                            if run.status == 'completed':
                                loader.stop()
                                print("Explicación Diagrama Obtenida... \n")
                                messages = client.beta.threads.messages.list(thread_id=thread.id)
                                loader.stop()
                                time.sleep(5)
                                return {
                                        "thread_id": thread_id if thread_id is not None else thread.id,
                                        "resp": diagram_injector(
                                                diagram_id,
                                                response_formater(
                                                    erase_source_labels(
                                                        messages.data[0].content[0].text.value
                                                    )
                                                )
                                            )
                                        }

def erase_source_labels(input_string):
    """
    Elimina todos los textos que están entre los corchetes 【】 de una cadena, 
    incluyendo los propios corchetes.
    
    Args:
        input_string (str): La cadena de entrada a limpiar.
    
    Returns:
        str: La cadena limpia sin los textos entre corchetes.
    """
    # Expresión regular para encontrar los textos entre 【 y 】
    pattern = r"【.*?】"
    # Reemplazar los textos que coincidan con la expresión regular por una cadena vacía
    cleaned_string = re.sub(pattern, "", input_string)
    return cleaned_string.strip()

def response_formater(resp):
   
    # Insertar un salto de línea antes de enumeraciones como "6. "
    enumeration_regex = r"(\D\d{1,2}\.\s)"
    resp = re.sub(enumeration_regex, r"<br/>\1", resp)
    
    # Insertar un salto de línea antes de un guion seguido de un espacio
    dash_regex = r"(- )"
    resp = re.sub(dash_regex, r"<br/>\1", resp)
    
    # Reemplazar las frases entre ** ** con <b>HTML</b>
    bold_markdown_regex = r"\*\*(.*?)\*\*"
    resp = re.sub(bold_markdown_regex, r"<b>\1</b>", resp)
    
    return resp