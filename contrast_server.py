import pika
import json
from PIL import Image, ImageEnhance
import base64

ip_addr = 0
class ContrastServer():
    def __init__(self, ip_addr):
        self.credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, "/", self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = "routing", exchange_type ="direct")
        self.queue = self.channel.queue_declare(queue = "", exclusive = True)
        self.channel.queue_bind(exchange = "routing", queue = self.queue.method.queue, routing_key = "contrast")
        self.channel.basic_qos(prefetch_count=1)
        print("Running Contrast Server\n")

def callback(ch, method, properties, body):
    message = json.loads(body)
    client_IP = message["client_IP"]
    image_name = "original_" + message["image_name"]
    image_data = base64.b64decode(message["image_data"])
    contrast = message["contrast"]
    
    with open(image_name, "wb") as image:
        image.write(image_data)

    image = Image.open(image_name)
    if(image_name[-3:] == "gif"):
        new = []
        for frame_num in range(image.n_frames):
            image.seek(frame_num)
            nhans_frame= Image.new('RGBA', image.size) 
            nhans_frame.paste(image)
            nhans_frame = ImageEnhance.Contrast(nhans_frame).enhance(contrast)
            new.append(nhans_frame)
        new[0].save(image_name, append_images=new[1:], save_all=True)
    else:
        enhanced_image = ImageEnhance.Contrast(image)
        enhanced_image = enhanced_image.enhance(contrast)
        enhanced_image.save(image_name)

    print(f"Enhanced contrast factor of {image_name} by {contrast}.")

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
    channel.basic_publish(exchange = "routing", routing_key = "client." + client_IP, body = json_message)
    connection.close()

    print(f"Sent enhanced {image_name} to {client_IP}...")

def main():
    global ip_addr
    ip_addr = input("Enter the rabbitmq server's IP address: ")
    server = ContrastServer(ip_addr)

    server.channel.basic_consume(queue = server.queue.method.queue, auto_ack = True, on_message_callback = callback)

    server.channel.start_consuming()

if __name__ == "__main__":
    main()
