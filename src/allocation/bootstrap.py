from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from allocation import config, email, orm, messagebus, unit_of_work, redis_pubsub

DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_postgres_uri(),
    isolation_level="SERIALIZABLE"
))


def bootstrap(
        start_orm=orm.start_mappers,
        session_factory=DEFAULT_SESSION_FACTORY,
        send_mail=email.send,
        publish=redis_pubsub.publish,
):
    start_orm()
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory=session_factory)
    bus = messagebus.MessageBus(uow=uow, send_mail=send_mail, publish=publish)
    return bus

