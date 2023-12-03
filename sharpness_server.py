import pika
import json
from PIL import Image, ImageEnhance
import base64

ip_addr = 0
class SharpnessServer():
    def __init__(self, ip_addr):
        self.credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, "/", self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = "routing", exchange_type ="direct")
        self.queue = self.channel.queue_declare(queue = "", exclusive = True)
        self.channel.queue_bind(exchange = "routing", queue = self.queue.method.queue, routing_key = "sharpness")
        self.channel.basic_qos(prefetch_count=1)
        print("Running Sharpness Server\n");

def callback(ch, method, properties, body):
    message = json.loads(body)
    image_name = "original_" + message["image_name"]
    image_data = base64.b64decode(message["image_data"])
    sharpness = message["sharpness"]
    
    with open(image_name, "wb") as image:
        image.write(image_data)

    image = Image.open(image_name)
    if(image_name[-3:] == "gif"):
        new = []
        for frame_num in range(image.n_frames):
            image.seek(frame_num)
            nhans_frame= Image.new('RGBA', image.size) 
            nhans_frame.paste(image)
            nhans_frame = ImageEnhance.Sharpness(nhans_frame).enhance(sharpness)
            new.append(nhans_frame)
        new[0].save(image_name, append_images=new[1:], save_all=True)
    else:
        enhanced_image = ImageEnhance.Sharpness(image)
        enhanced_image = enhanced_image.enhance(sharpness)
        enhanced_image.save(image_name)

    print(f"Enhanced sharpness factor of {image_name} by {sharpness}.")

    with open(image_name, "rb") as image:
        image_data = image.read()

    image_data = base64.b64encode(image_data).decode()
    new_message = {"client_IP": message["client_IP"],
                           "image_name": message["image_name"],
                           "image_data": image_data,
                           "enhanced_folder": message["enhanced_folder"],
                           "brightness": message["brightness"],
                           "sharpness": message["sharpness"],
                           "contrast": message["contrast"]}
    
    json_message = json.dumps(new_message)
    
    global ip_addr
    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, "/", credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange = "routing", exchange_type = "direct")
    channel.basic_publish(exchange = "routing", routing_key = "contrast", body = json_message)
    connection.close()

    print(f"Sent {image_name} to Contrast Enhancemet Server...")

def main():
    global ip_addr
    ip_addr = input("Input this server's IP address: ");
    server = SharpnessServer(ip_addr);

    server.channel.basic_consume(queue = server.queue.method.queue, auto_ack = True, on_message_callback = callback)

    server.channel.start_consuming()

if __name__ == "__main__":
    main()
