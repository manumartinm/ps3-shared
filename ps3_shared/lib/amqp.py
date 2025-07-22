import pika
from typing import Callable, Optional


class AMQPManager:
    def __init__(
        self,
        host: str,
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
    ) -> None:
        credentials = pika.PlainCredentials(username, password)
        self.connection_params: pika.ConnectionParameters = pika.ConnectionParameters(
            host=host, port=port, virtual_host=virtual_host, credentials=credentials
        )
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def connect(self) -> None:
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        if not self.channel:
            self.connect()
        self.channel.queue_declare(queue=queue_name, durable=durable)

    def publish(self, queue_name: str, message: str) -> None:
        if not self.channel:
            self.connect()
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message.encode() if isinstance(message, str) else message,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        print(f"Mensaje publicado en la cola '{queue_name}'.")

    def consume(
        self, queue_name: str, callback: Callable, auto_ack: bool = False
    ) -> None:
        if not self.channel:
            self.connect()
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=auto_ack
        )
        print(
            f"Esperando mensajes en la cola '{queue_name}'. Para salir presiona CTRL+C."
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.close()

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            print("Conexión AMQP cerrada.")
