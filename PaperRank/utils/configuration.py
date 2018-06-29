import json
import logging
import os
import pprint


BASE_CONFIGURATION = 'config/base.json'


def setup(override: str=''):
    """Initializes the static configuration variables used in the
    PaperRank system. Provides a method to override base configuration.
    
    Keyword Arguments:
        override {str} -- File name in the `config/` directory
            that may be used to override the `base.json` configuration.
            (default: {''})
    
    Raises:
        RuntimeError -- Raised when configuration files cannot be found.
    """

    try:
        base_config_data = open(BASE_CONFIGURATION).read()
        base_config = json.loads(base_config_data)
    except FileNotFoundError:
        logging.error('Base configuration file in config/base.json not found.')
        raise RuntimeError('Base configuration file not found.')
    
    # Check if override is required
    if override is not '':
        try:
            override_config_data = open('config/{0}'.format(override)).read()
            override_config = json.loads(override_config_data)
        except FileNotFoundError:
            logging.error('Override configuration file config/{0} not found.')
            raise RuntimeError('Invalid configuraiton override file.')
        
        # Removing override parameters from base config
        all(map(base_config.pop, override_config))
        base_config.update(override_config)

    # Add to parameters
    global Parameters
    Parameters.__dict__.update(base_config)


@staticmethod
def Parameters():
    """Static function to store configuration variables. This function
    is not designed to be called, but rather serves as a placeholder.
    
    Raises:
        NotImplementedError -- Raised when the function is called directly.
    """

    raise NotImplementedError()
