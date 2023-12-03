import os
import json
import pika
import base64
from PIL import Image
import time

file_count = 0
stats_file = ""
files_enhanced = 0
start_time = 0.0
client = None

class Client():
    def __init__(self, client_IP, server_ip):
        self.client_IP = client_IP
        self.credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(server_ip, 5672, "/", self.credentials))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange = "routing", exchange_type ="direct")
        self.queue = self.channel.queue_declare(queue = "", exclusive = True)
        self.channel.queue_bind(exchange = "routing", queue = self.queue.method.queue, routing_key = "client." + self.client_IP)
        self.channel.basic_qos(prefetch_count=1)
        print("Launching Client")

def inputPrompt():
    folder_exists = False
    valid_input = False
    orig_folder = ""
    enhanced_folder = ""
    brightness = ""
    sharpness = ""
    contrast = ""

    while not folder_exists:
        print("Please enter the folder location of the images you would like to enhance.")
        orig_folder = input(">> ")

        if os.path.isdir(orig_folder):
            folder_exists = True

    print("\nPlease enter the folder location where you would like to store the enhanced images.")
    enhanced_folder = input(">> ")

    if not os.path.isdir(enhanced_folder):
        os.mkdir(enhanced_folder)

    while not valid_input:
        print("\nPlease enter the desired image BRIGHTNESS enhancement factor (float)")
        brightness = input(">> ")

        try:
            brightness = float(brightness)
            valid_input = True
        except ValueError:
            print("Entered value is not a float. Please enter a float type value. (Ex: 4.0)")

    valid_input = False

    while not valid_input:
        print("\nPlease enter the desired image SHARPNESS enhancement factor (float)")
        sharpness = input(">> ")

        try:
            sharpness = float(sharpness)
            valid_input = True
        except ValueError:
            print("Entered value is not a float. Please enter a float type value. (Ex: 4.0)")

    valid_input = False

    while not valid_input:
        print("\nPlease enter the desired image CONTRAST enhancement factor (float)")
        contrast = input(">> ")

        try:
            contrast = float(contrast)
            valid_input = True
        except ValueError:
            print("Entered value is not a float. Please enter a float type value. (Ex: 4.0)")

    return orig_folder, enhanced_folder, brightness, sharpness, contrast

def callback(ch, method, properties, body):
    global file_count, stats_file, files_enhanced, start_time, client
    files_enhanced += 1
    print("received a message")
    message = json.loads(body)
    image_name = message["image_name"]
    image_data = base64.b64decode(message["image_data"])
    enhanced_folder = message["enhanced_folder"]

    with open(os.path.join(enhanced_folder, image_name), "wb") as image:
        image.write(image_data)

    print(f"Enhanced {image_name} saved in {enhanced_folder}")

    if files_enhanced == file_count:
        end_time = time.time()
        elapsed_time = end_time - start_time
        with open(stats_file, "w+") as file:
            lines = ["Number of images enhanced: ", str(files_enhanced),
                     "\nTime elapsed: ", str(elapsed_time),
                     "\nNumber of machines used: 3"]
            file.writelines(lines)
            file.close()

        print("All images have been processed.")
        print(f"Statistics of the processed files can be found in {stats_file}.")
        print("Client program shutting down...")
        client.connection.close()


def main():
    global file_count, stats_file, start_time, client
    orig_folder = ""
    enhanced_folder = ""
    brightness = 0.0
    sharpness = 0.0
    contrast = 0.0

    client_IP = input("Get client's IP address: ")
    server_ip = input("Input the server IP: ")
    client = Client(client_IP, server_ip)

    client.channel.basic_consume(queue = client.queue.method.queue, auto_ack = True, on_message_callback = callback)

    orig_folder, enhanced_folder, brightness, sharpness, contrast = inputPrompt()
    stats_file = os.path.join(enhanced_folder, "statistics.txt")


    #print(brightness, sharpness, contrast)
    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters(server_ip, 5672, "/", credentials))
    channel = connection.channel() 

    channel.exchange_declare(exchange = "routing", exchange_type = "direct")

    start_time = time.time()
    for image_name in os.listdir(orig_folder):
        file_count += 1
        with open(os.path.join(orig_folder, image_name), "rb") as image:
            print(orig_folder)
            print(image_name)
            image_data = image.read()

        image_data = base64.b64encode(image_data)
        image_data = image_data.decode()

        message = {"client_IP": client_IP,
                   "image_name": image_name,
                   "image_data": image_data,
                   "enhanced_folder": enhanced_folder,
                   "brightness": brightness,
                   "sharpness": sharpness,
                   "contrast": contrast}
        
        json_message = json.dumps(message)
        channel.basic_publish(exchange = "routing", routing_key = "brightness", body = json_message)

        print(f"Sent {image_name} for processing...")

    client.channel.start_consuming()
    connection.close()

if __name__ == "__main__":
    main()
