from celery import Celery
from flask import Flask
from pymongo import MongoClient

import celery_config


def create_app(settings):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = settings['secret']
    app.db = MongoClient(settings['mongo_connection_string']).get_database(settings['default_database'])

    app.config.update(
        CELERY_BROKER_URL=settings['mongo_connection_string']
    )

    from src.views.auth import init_view
    init_view(app, settings)

    from src.views.index import init_view
    init_view(app, settings)

    from src.views.configs import init_view
    init_view(app, settings)
    return app


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    celery.config_from_object(celery_config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery
