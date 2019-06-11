from datetime import datetime
from flask import Flask, jsonify, request
from allocation import (
    commands, email, exceptions, messagebus, orm, unit_of_work,
    views,
)

app = Flask(__name__)
orm.start_mappers()

def get_bus():
    from allocation import redis_pubsub  # avoid circular dependency
    return messagebus.MessageBus(
        uow=unit_of_work.SqlAlchemyUnitOfWork(),
        send_mail=email.send,
        publish=redis_pubsub.publish
    )



@app.route("/add_batch", methods=['POST'])
def add_batch():
    bus = get_bus()
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    command = commands.CreateBatch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
    )
    bus.handle([command])
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    bus = get_bus()
    try:
        command = commands.Allocate(
            request.json['orderid'], request.json['sku'], request.json['qty'],
        )
        bus.handle([command])
    except exceptions.InvalidSku as e:
        return jsonify({'message': str(e)}), 400

    return 'OK', 202


@app.route("/allocations/<orderid>", methods=['GET'])
def allocations_view_endpoint(orderid):
    bus = get_bus()
    result = views.allocations(orderid, bus.uow)
    if not result:
        return 'not found', 404
    return jsonify(result), 200
