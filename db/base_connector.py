import os
import yaml

def load_db_config(path='config/databases.yaml'):
    with open(path, 'r') as f:
        config_yaml = yaml.safe_load(f)
    env = config_yaml.get('environment', 'DEV').upper()
    connections = config_yaml['connections']
    return env, connections

