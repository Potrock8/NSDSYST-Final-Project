import pika
import json
from PIL import Image, ImageEnhance
import base64

def callback(ch, method, properties, body):
    message = json.loads(body)
    image_name = message["image_name"]
    image_data = base64.decodebytes(str(message["image_data"]))
    brightness = message["brightness"]
    
    with open(image_name, "wb") as image:
        image.write(image_data)

    image = Image.open(image_name)
    enhanced_image = ImageEnhance.Brightness(image)
    enhanced_image = enhanced_image.enhance(brightness)

    #enhanced_image.save(f"./Enhanced Images/{image_name}")


def main():
    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.222.128", 5672, "/", credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange = "routing", exchange_type ="direct")
    queue = channel.queue_declare(queue = "", exclusive = True)
    channel.queue_bind(exchange = "routing", queue = queue.method.queue, routing_key = "brightness")

    channel.basic_consume(queue = queue.method.queue, auto_ack = True, on_message_callback = callback)

if __name__ == "__main__":
    main()