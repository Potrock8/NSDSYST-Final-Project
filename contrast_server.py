import pika
import json
from PIL import Image, ImageEnhance
import base64

class ContrastServer():
    def __init__(self):
        self.credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.222.128", 5672, "/", self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = "routing", exchange_type ="direct")
        self.queue = self.channel.queue_declare(queue = "", exclusive = True)
        self.channel.queue_bind(exchange = "routing", queue = self.queue.method.queue, routing_key = "contrast")
        self.channel.basic_qos(prefetch_count=1)

def callback(ch, method, properties, body):
    message = json.loads(body)
    client_IP = message["client_IP"]
    image_name = message["image_name"]
    image_data = base64.b64decode(message["image_data"])
    contrast = message["contrast"]
    
    with open("original_" + image_name, "wb") as image:
        image.write(image_data)

    image = Image.open(image_name)
    enhanced_image = ImageEnhance.Contrast(image)
    enhanced_image = enhanced_image.enhance(contrast)
    enhanced_image.save(image_name)

    print(f"Enhanced contrast factor of {image_name} by {contrast}.")

    with open(image_name, "rb") as image:
        image_data = image.read()

    image_data = base64.b64encode(image_data).decode()
    message = body
    message["image_data"] = image_data
    
    json_message = json.dumps(message)

    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.222.128", 5672, "/", credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange = "routing", exchange_type = "direct")
    channel.basic_publish(exchange = "routing", routing_key = "client." + client_IP, body = json_message)
    connection.close()

    print(f"Sent enhanced {image_name} to {client_IP}...")

def main():
    server = ContrastServer

    server.channel.basic_consume(queue = server.queue.method.queue, auto_ack = True, on_message_callback = callback)

    server.channel.start_consuming()

if __name__ == "__main__":
    main()