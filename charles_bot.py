import requests
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
TOKEN_TELEGRAM = os.environ.get("TOKEN")

print(os.environ.get("DOMAIN"))


def get_updates(offset):
    """
    Obtiene las actualizaciones de mensajes desde la API de Telegram.

    Args:
        offset (int): Especifica el ID de actualización a partir del cual se
                      deben recibir nuevas actualizaciones.

    Returns:
        list: Una lista de diccionarios con los datos de los mensajes recibidos.

    La función realiza una solicitud a la API de Telegram para obtener los
    mensajes recibidos que aún no han sido procesados. El parámetro 'timeout'
    establece un tiempo de espera para recibir las actualizaciones, y 'offset'
    evita que se repitan mensajes procesados previamente.
    """
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/getUpdates"
    params = {"timeout": 100, "offset": offset}
    response = requests.get(url, params=params)
    return response.json()["result"]


def send_messages(chat_id, text):
    """
    Envía un mensaje a un usuario específico en Telegram.

    Args:
        chat_id (int): El ID del chat de Telegram al que se enviará el mensaje.
        text (str): El contenido del mensaje que se enviará.

    Returns:
        Response: El objeto de respuesta de la solicitud POST.

    La función construye la URL de la API de Telegram utilizando el token del bot,
    y envía un mensaje al usuario especificado mediante una solicitud POST.
    """
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    response = requests.post(url, params=params)
    return response


def get_openai_response(prompt):
    """
    Genera una respuesta a partir de un 'prompt' utilizando el modelo de OpenAI.

    Args:
        prompt (str): Texto de entrada para el modelo de OpenAI, que representa
                      la pregunta o mensaje del usuario.

    Returns:
        str: El texto de la respuesta generada por el modelo de OpenAI.

    Esta función interactúa con la API de OpenAI para generar respuestas contextuales
    usando un asistente configurado como sistema. El mensaje 'prompt' del usuario es
    procesado con el modelo especificado en el método `openai.chat.completions.create`.
    """
    system = """
        Eres un asistente de atención a clientes 
        para una empresa de asesorias contables y financieras llamada 1-2-Trust.
        Cuando te pregunten por la empresa 1-2 Trust debes responder con lo siguiente:
        '1-2-Trust es una empresa que cree en la importancia de que las Micro y Pequeñas 
        empresas sean sostenibles, se vuelvan competitivas y crezcan, por lo cual 1-2-Trust 
        está en constante innovación para prestar servicios de calidad a sus clientes, que les 
        permitan tener procesos de apoyo eficientes y conocimiento oportuno y relevante para la 
        toma de decisiones.' Su página web es https://12trust.co/
    """
    response = openai.chat.completions.create(
        model="ft:gpt-3.5-turbo-0613:personal::9x0UQTDV",
        messages=[
            {"role": "system", "content": f"{system}"},
            {"role": "user", "content": f"{prompt}"},
        ],
        max_tokens=150,
        n=1,
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def main():
    """
    Función principal del bot de Telegram.

    Inicializa el bot e inicia un bucle continuo para recibir y procesar
    mensajes de los usuarios. Para cada mensaje recibido, obtiene la
    respuesta desde OpenAI y la envía de vuelta al usuario en Telegram.

    La función utiliza un 'offset' para evitar procesar mensajes duplicados,
    y un tiempo de espera cuando no hay mensajes nuevos.
    """
    print("Starting bot...")
    offset = 0
    while True:
        updates = get_updates(offset)
        if updates:
            for update in updates:
                offset = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                user_message = update["message"]["text"]
                print(f"Received message: {user_message}")
                GPT = get_openai_response(user_message)
                send_messages(chat_id, GPT)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
