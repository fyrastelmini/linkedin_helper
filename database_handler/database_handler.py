import database as database
from flask import Flask
import os
import time
import json
from sqlalchemy.exc import IntegrityError
from kafka.errors import NoBrokersAvailable
from kafka import KafkaConsumer, KafkaProducer
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
database.db.init_app(app)
database.ma.init_app(app)

def create_producer():
    while True:
        try:
            producer = KafkaProducer(bootstrap_servers='kafka:9092',
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'))
            return producer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)
def create_consumer():
    while True:
        try:
            consumer = KafkaConsumer(bootstrap_servers='kafka:9092',
                                     auto_offset_reset='earliest',
                                     enable_auto_commit=True,
                                     group_id='my-group',
                                     value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            consumer.subscribe(['extracted_data', 'summerized_data', 'csv_data','get_view'])
            return consumer
        except NoBrokersAvailable:
            print("Broker not available, retrying...")
            time.sleep(3)


def consume_messages():
    consumer = create_consumer()

    for message in consumer:
        print(f"Received message")
        topic = message.topic
        with app.app_context():
            if topic == 'extracted_data':
                new_job = database.Job(message.value["job_title"], message.value["company_name"], message.value["location"], message.value["url"])
                try:
                    database.db.session.add(new_job)
                    database.db.session.commit()
                except IntegrityError:
                    database.db.session.rollback()
                
                consumer.commit()
            elif topic == 'summerized_data':
                new_SummarizedData = database.SummarizedData(message.value["url"],message.value["data"])
                try:
                    database.db.session.add(new_SummarizedData)
                    database.db.session.commit()
                except IntegrityError:
                    database.db.session.rollback()
                consumer.commit()
            elif topic == 'new_raw_data':
                new_raw_data = database.RawData(message.value["url"], message.value["raw_data"])
                try:
                    database.db.session.add(new_raw_data)
                    database.db.session.commit()
                except IntegrityError:
                    database.db.session.rollback()
                consumer.commit()
            elif topic == 'get_view':
                
                data = database.db.session.query(database.Job).all()
                
                formatted_data = database.multiple_Job_data_schema.dump(data)
                summarized_data = database.db.session.query(database.SummarizedData).all()
                formatted_summarized_data = database.multiple_SummarizedData_data_schema.dump(summarized_data)
                producer = create_producer()
                combined_data = {
                'formatted_data': formatted_data,
                'formatted_summarized_data': formatted_summarized_data
                }
                producer.send('database_view', value=combined_data)
                producer.flush()
                producer.close()
                consumer.commit()
if __name__ == "__main__":
    with app.app_context():
        database.db.create_all()
    consume_messages()
    app.run(debug=True, host='0.0.0.0',port=4444)