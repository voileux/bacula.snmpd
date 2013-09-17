import sys
import ConfigParser
import os.path

#_dir, _f = os.path.split(os.path.abspath(__file__))
DEFAULT_ROOTDIR = "/usr/local/src/bacula-snmpd/"
DEFAULT_CONFIG_FILE = os.path.join('etc', 'defaults.cfg')

BOOLEANS = ['False', 'True', '1', '0']


def getdefaults(section, _rootDir=DEFAULT_ROOTDIR, _cfgFile=DEFAULT_CONFIG_FILE):
    """Get default values for template vars."""
    cfg = os.path.join(_rootDir , _cfgFile)
    Config = ConfigParser.ConfigParser()
    Config.read(cfg)
    options = Config.items(section)
    settings = dict(options)

    # sets real bool values in settings
    #for option in options:
    #    if option[1] in BOOLEANS:
    #        settings[option[0]] = Config.getboolean(section, option[0])
    return settings



