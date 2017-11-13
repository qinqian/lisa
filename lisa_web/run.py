from flask_script import Manager
from lisa_web import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
