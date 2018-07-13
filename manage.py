from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import *

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # To run this app, hit following commands on terminal-
    # export DATABASE_URL='postgresql://postgres:postgres@localhost:5432/crowd_funding'
    manager.run()
