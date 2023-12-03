import pika
import json
from PIL import Image, ImageEnhance
import base64

class BrightnessServer():
    def __init__(self, ip_addr):
        self.credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, "/", self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = "routing", exchange_type ="direct")
        self.queue = self.channel.queue_declare(queue = "", exclusive = True)
        self.channel.queue_bind(exchange = "routing", queue = self.queue.method.queue, routing_key = "brightness")
        self.channel.basic_qos(prefetch_count=1)
        print("Running Brightness Server\n");

def callback(ch, method, properties, body, ip_addr):
    message = json.loads(body)
    image_name = message["image_name"]
    image_data = base64.b64decode(message["image_data"])
    brightness = message["brightness"]
    
    with open("original_" + image_name, "wb") as image:
        image.write(image_data)

    image = Image.open(image_name)
    enhanced_image = ImageEnhance.Brightness(image)
    enhanced_image = enhanced_image.enhance(brightness)
    enhanced_image.save(image_name)

    print(f"Enhanced brightness factor of {image_name} by {brightness}.")

    with open(image_name, "rb") as image:
        image_data = image.read()

    image_data = base64.b64encode(image_data).decode()
    message = body
    message["image_data"] = image_data
    
    json_message = json.dumps(message)

    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, "/", credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange = "routing", exchange_type ="direct")
    channel.basic_publish(exchange = "routing", routing_key = "sharpness", body = json_message)
    connection.close()

    print(f"Sent {image_name} to Sharpness Enhancemet Server...")

def main():
    ip_addr = input("Input this server's computer address: ")
    server = BrightnessServer(ip_addr)

    server.channel.basic_consume(queue = server.queue.method.queue, auto_ack = True, on_message_callback = callback)

    server.channel.start_consuming()

if __name__ == "__main__":
    main()
