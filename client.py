import os
import socket
import json
import pika
import base64

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

def main():
    orig_folder = ""
    enhanced_folder = ""
    stats_file = ""
    brightness = 0.0
    sharpness = 0.0
    contrast = 0.0

    clientIP = socket.gethostbyname(socket.gethostname())

    orig_folder, enhanced_folder, brightness, sharpness, contrast = inputPrompt()
    stats_file = enhanced_folder + "/statistics.txt"


    #print(brightness, sharpness, contrast)
    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters("192.168.222.128", 5672, "/", credentials))
    channel = connection.channel() 

    channel.exchange_declare(exchange = "routing", exchange_type ="direct")

    for image_name in os.listdir(orig_folder):
        with open(os.path.join(orig_folder, image_name), "rb") as image:
            image_data = image.read()

        image_data = base64.b64encode(image_data)
        image_data = image_data.decode()

        message = {"clientIP": clientIP,
                   "image_name": image_name,
                   "image_data": image_data,
                   "brightness": brightness,
                   "sharpness": sharpness,
                   "contrast": contrast}
        
        json_message = json.dumps(message)
        channel.basic_publish(exchange = "routing", routing_key = "brightness", body = json_message)

        print(f"Sent {image_name} for processing...")

    connection.close()

if __name__ == "__main__":
    main()