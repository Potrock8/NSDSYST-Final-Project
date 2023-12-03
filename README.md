# BSC Command Line Program -- Distributed System Version

A simple program created for DLSU NSDSYST demonstrating the concepts behind distributed systems.

# How to Run

## Prerequesites
1. Docker
2. Pip
3. Python 3 and above.

## Instructions
1. Run the following program: `sudo docker run -d --hostname rabbit-svr --name nsdsyst-rmq -p 15672:15672 -p 5672:5672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management`
2. Open the RabbitMQ interface using the same IP address you launched the Docker container in.
2. Add user 'rabbituser' with password 'rabbit1234' and 'admin' tag in the 'Admin' tab
3. Install pika using `pip install pika`
4. Run the programs using `python3 <file-name>`

