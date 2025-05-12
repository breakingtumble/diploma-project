class MarketplaceConfiguration:
    __configs = {}

    def __init__(self, marketplace_json_configs_array):
        self.marketplace_configs = marketplace_json_configs_array
        self.__init_marketplace_dict(marketplace_json_configs_array)

    def __init_marketplace_dict(self, marketplace_configs):
        for marketplace_config in marketplace_configs:
            for key in marketplace_config:
                if len(str(marketplace_config[key])) == 0:
                    raise Exception("Some of the requiered fields in the marketplaces' config are empty, please fill it")
            marketplace_key = marketplace_config['name']
            marketplace_config.pop('name')
            self.__configs[marketplace_key] = marketplace_config
