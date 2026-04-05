"""
Exercise 03 — Event Consumer

Implement a RabbitMQ consumer that:
- Connects to RabbitMQ at RABBITMQ_URL env var
- Consumes messages from the "node_events" queue
- Logs each event to stdout: "EVENT: {event} | node: {node_name} | time: {timestamp}"
- Acknowledges each message after processing
"""

# TODO: Implement the consumer
