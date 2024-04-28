import configparser
import os
import logging

class ConfigWrapper:
    def create_instance(base_ini_file, environment_specific_ini_file)->configparser.ConfigParser:
        config_parser = configparser.ConfigParser(os.environ,interpolation=configparser.ExtendedInterpolation())
        dir_name = os.path.dirname( __file__)

        # base_ini_file = os.path.join(dir_name,"settings.ini")
        if not os.path.exists(base_ini_file):
            raise Exception(f"The base INI file '{base_ini_file}' was not found")
        logging.info(f"The base INI file '{base_ini_file}' was found")

        # env = os.environ.get("environment", None)
        # logging.info(f"The environemnt variable 'environment' has the value '{env}'")
        # if env is None:
        #     raise ValueError(f"The envrionment variable: 'environment' has not been set") 
        # logging.info(f"The current environment is '{env}'")
        config_parser.read(base_ini_file)
        # environment_specific_ini_file = os.path.join(dir_name,f"settings.{env}.ini")
        if not os.path.exists(environment_specific_ini_file):
            logging.warning(f"The environment specific INI file '{environment_specific_ini_file}' was not found")
            return config_parser
        logging.info(f"The environment specific INI file '{environment_specific_ini_file}' was found")
        config_parser.read(environment_specific_ini_file)

        return config_parser

    
    