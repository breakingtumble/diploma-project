import sys
import os
import copy
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime
from sqlalchemy.ext.mutable import MutableDict

Base = declarative_base()

class MarketplaceConfiguration(Base):
    __tablename__ = 'marketplace_configurations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    config_json = Column(MutableDict.as_mutable(JSON), nullable=False)
    required_fields_json = Column(MutableDict.as_mutable(JSON), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)

    def __init__(self, name, config_json, required_fields_json):
        self.name = name
        self.config_json = config_json
        self.required_fields_json = required_fields_json

class ConfigurationLoader:
    __configurations = None

    def __init__(self, db_url, conf_file_path=None, required_fields_path=None):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.conf_file_path = conf_file_path
        self.required_fields_path = required_fields_path
        
        try:
            configurations = self.__load_configurations_from_db()
        except Exception as e:
            if not conf_file_path or not required_fields_path:
                raise Exception("Database loading failed and no fallback files provided")
            configurations = self.__load_configurations_from_file(conf_file_path, required_fields_path)
            
        self.__generate_configurations_object(configurations)
    
    def __load_configurations_from_db(self):
        session = self.Session()
        try:
            print("Loading configurations from database...")
            config = session.query(MarketplaceConfiguration).all()[0]
            if not config:
                raise Exception("No configurations found in the database.")
            
            config_data = config.config_json.get('marketplace_configurations', [])
            required_fields = config.required_fields_json.get('required_fields', [])
            
            for config in config_data:
                self.__validate_configuration_fields_and_params(config['fields'], required_fields)
            
            return config_data
        finally:
            session.close()

    def __load_configurations_from_file(self, conf_file_path, required_fields_path):
        if (os.path.getsize(conf_file_path) == 0):
            raise Exception("Can't read configuration file, there is no content inside. Aborting application.")
        if (os.path.getsize(required_fields_path) == 0):
            raise Exception("Can't read required fields configuration file, there is no content inside. Aborting application.")
        
        config_data = self.__read_json(conf_file_path).get('marketplace_configurations', [])
        required_fields = self.__read_json(required_fields_path).get('required_fields', [])

        for config in config_data:
            self.__validate_configuration_fields_and_params(config['fields'], required_fields)
        
        return config_data

    def __validate_configuration_fields(self, fields_to_validate, required_fields):
        missing_fields = set()

        for required_field in required_fields:
            value = fields_to_validate[required_field]
            if value is None or str(value).strip() == '':
                missing_fields.add(required_field)
        
        if len(missing_fields) != 0:
            raise Exception(f"Missing or empty required fields: {', '.join(missing_fields)}. Check configuration file.")
        
        extra_fields = set(fields_to_validate) - set(required_fields)
        if extra_fields:
            raise Exception(f"Invalid fields found: {', '.join(extra_fields)}. Check configuration file.")
        
    def __validate_configuration_fields_and_params(self, fields_to_validate, required_fields):
        missing_fields = set()
        fields_to_validate = self.__generate_configurations_dict(fields_to_validate, 'name')
        required_fields = self.__generate_configurations_dict(required_fields, 'field_name')
        
        fields_to_validate_namings = fields_to_validate.keys()
        required_fields_namings = required_fields.keys()

        extra_fields = set(fields_to_validate_namings) - set(required_fields_namings)
        if extra_fields:
            raise Exception(f"Invalid fields found: {', '.join(extra_fields)}. Check configuration file.")

        for required_field_name in required_fields_namings:
            try:
                value = fields_to_validate[required_field_name]
                if str(value).strip == '':
                    missing_fields.add(required_field_name)
            except:
                missing_fields.add(required_field_name)
            required_field_params = required_fields[required_field_name]['field_params']
            missing_params = set()
            for required_field_param in required_field_params:
                try:
                    param = value[required_field_param]
                    if str(value).strip() == '':
                        missing_params.add(required_field_param)
                except:
                    missing_params.add(required_field_param)
            if len(missing_params) != 0:
                raise Exception(f"Missing or empty required parameter(s): {', '.join(missing_params)} for '{required_field_name}' field. Check configuration file.")
            extra_params = set(value.keys()) - set(required_field_params)
            if extra_params:
                raise Exception(f"Extra parameter(s) found: {', '.join(extra_fields)}. Check configuration file.")
    
        if len(missing_fields) != 0:
            raise Exception(f"Missing or empty required field(s): {', '.join(missing_fields)}. Check configuration file.")
        
    def __generate_configurations_dict(self, configurations, key_field):
        config_dict = dict()
        for configuration in configurations:
            key = configuration[key_field]
            copied_configuration = copy.copy(configuration)
            copied_configuration.pop(key_field)
            config_dict[key] = copied_configuration
        
        return config_dict
    
    def __generate_configurations_object(self, configurations):
        configurations = self.__generate_configurations_dict(configurations, 'name')
        for key in configurations:
            for field in configurations[key]:
                if type(configurations[key][field]) is list and field == 'fields':
                    configurations[key][field] = self.__generate_configurations_dict(configurations[key][field], 'name')
        self.__configurations = configurations

    def __read_json(self, file_path):
        with open(file_path) as f:
            json_object = json.load(f)
            return json_object

    def get_configuration_object(self):
        """Get the configuration object from the database"""
        with self.Session() as db:
            config = db.query(MarketplaceConfiguration).first()
            if not config:
                raise Exception("No marketplace configuration found in database")
            configs_list = config.config_json.get('marketplace_configurations', [])
            # Convert list to dict mapping name -> config dict
            configs_dict = {c['name']: c for c in configs_list}
            return configs_dict