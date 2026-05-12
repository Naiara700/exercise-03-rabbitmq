"""
Exercise 03 — Event Consumer

Connects to RabbitMQ and consumes messages from the "node_events" queue.
Logs each event to stdout and acknowledges after processing.
Retries connection with exponential backoff if RabbitMQ is not ready.
"""

import json
import os
import time

import pika

RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
QUEUE        = "node_events"
MAX_RETRIES  = 10
RETRY_DELAY  = 3


def connect():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            conn = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            print(f"Conectado a RabbitMQ.", flush=True)
            return conn
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ no disponible, reintento {attempt}/{MAX_RETRIES}...", flush=True)
            time.sleep(RETRY_DELAY)
    return None


def on_message(ch, method, properties, body):
    try:
        data      = json.loads(body)
        event     = data.get("event", "unknown")
        node_name = data.get("node_name", "unknown")
        timestamp = data.get("timestamp", "unknown")
        print(f"[EVENT] {event} — {node_name} @ {timestamp}", flush=True)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except json.JSONDecodeError:
        print(f"[WARN] mensaje no válido: {body}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
    connection = connect()
    if connection is None:
        print("No se pudo conectar a RabbitMQ. Abortando.", flush=True)
        return

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)

    print(f"Consumidor listo. Escuchando '{QUEUE}'...", flush=True)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except pika.exceptions.ConnectionClosedByBroker:
        print("[WARN] Conexión cerrada por RabbitMQ.", flush=True)
    except pika.exceptions.AMQPConnectionError:
        print("[ERROR] Conexión perdida.", flush=True)
    finally:
        if not connection.is_closed:
            connection.close()


if __name__ == "__main__":
    main()