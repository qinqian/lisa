"""update local data directory for .ini configuration file
"""
import fire

def update(folder):
    """ update the config given a folder
    """
    import os
    import configparser
    folder = os.path.abspath(folder)
    conf = configparser.ConfigParser()
    conf.read('lisa/lisa.ini')

    for key in conf.sections():
        for i in conf[key].keys():
            conf.set(key, i, os.path.join(folder, os.path.basename(conf.get(key, i))))

    with open('lisa/lisa.ini.updated', 'w') as configfile:
        conf.write(configfile)

if __name__ == '__main__':
    fire.Fire(update)
