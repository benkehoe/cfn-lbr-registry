import six
import os.path

import yaml

import file_transformer

class LBRRegistryConfig(object):
    DEFAULT_MEMORY_SIZE = 128
    DEFAULT_POLICIES = 'AdministratorAccess'
    DEFAULT_TIMEOUT = 300

    @classmethod
    def parse(cls, lbr_reg_obj):
        options = lbr_reg_obj.get('Options', {})
        defaults = lbr_reg_obj.get('Defaults', {})
        resources = {}
        for resource_name, resource_config in six.iteritems(lbr_reg_obj['Resources']):
            resources[resource_name] = LBRRegistryResource.parse(resource_config)
        return cls(resources, defaults, options)
    
    def __init__(self, resources, defaults={}, options={}):
        self.resources = resources
        self.options = options
        
        self.defaults = {
            'MemorySize': self.DEFAULT_MEMORY_SIZE,
            'Timeout': self.DEFAULT_TIMEOUT,
        }
        if self.options.get('EnableDefaultPolicies', False):
            self.defaults['Policies'] = self.DEFAULT_POLICIES
        
        self.defaults.update(defaults)
    
    def add_to_template(self, template):
        template['Transform'] = 'AWS::Serverless-2016-10-31'
        
        for name, resource in six.iteritems(self.resources):
            resource.add_to_template(name, template)
        
class LBRRegistryResource(object):
    @classmethod
    def parse(cls, lbr_resource_obj):
        code_uri = lbr_resource_obj['CodeUri']
        if 'Config' in lbr_resource_obj:
            config_obj = lbr_resource_obj['Config']
        else:
            try:
                with open(os.path.join(code_uri, 'lbr.yaml'), 'r') as fp:
                    config_obj = yaml.load(fp)
            except Exception as e:
                raise
        config = LBRConfig.parse(config_obj)
        enable = lbr_resource_obj.get('Enable', True)
        return cls(code_uri, config, enable)
    
    def __init__(self, code_uri, config, enable=True):
        self.code_uri = code_uri
        self.config = config
        self.enable = enable
    
    def add_to_template(self, name, template):
        if not self.enable:
            return
        self.config.add_to_template(name, template)

class LBRConfig(object):
    @classmethod
    def parse(cls, lbr_config_obj):
        version_objs = lbr_config_obj.pop('Versions', {})
        default = LBRVersionConfig.parse(lbr_config_obj)
        versions = {version_id: LBRVersionConfig.parse(v) for version_id, v in six.iteritems(version_objs)}
        enable = lbr_config_obj.get('Enable', True)
        return cls(default, versions, enable)
    
    def __init__(self, default, versions, enable=True):
        self.default = default
        self.versions = versions
        self.enable = enable
    
    def add_to_template(self, name, template):
        versions = self.versions or [self.default]
        for version_id, version in six.iteritems(versions):
            version.add_to_template(name, version_id, template, self.default)

class LBRVersionConfig(object):
    @classmethod
    def parse(cls, lbr_version_config_obj):
        types = lbr_version_config_obj.get('Types') or lbr_version_config_obj.get('Type')
        properties = lbr_version_config_obj.get('Properties')
        enable = lbr_version_config_obj.get('Enable', True)
        beta = lbr_version_config_obj.get('Beta', False)
        return cls(properties, types, enable, beta)
    
    def __init__(self, properties, types=None, enable=True, beta=False):
        if isinstance(types, six.string_types):
            types = [types]
        self.types = types
        self.properties =properties
        self.enable = enable
        self.beta = beta
    
    def add_to_template(self, name, version_id, template, default=None):
        if not self.enable:
            return
        
        suffix = 'beta' if self.beta else ''
        version_name = '{}{}{}'.format(name, version_id, suffix)
        
        version_resource_name = version_name + 'Function'
        
        properties = {}
        if default:
            properties.update(default.properties)
        properties.update(self.properties)
        
        resource = {
            'Type': 'AWS::Serverless::Function',
            'Properties': properties,
        }
        
        metadata = {}
        if self.types:
            metadata['LBR::Types'] = self.types
        if metadata:
            resource['Metadata'] = metadata
        
        output = {
            'Value': {'Fn::GetAtt': [version_resource_name, 'Arn']},
            'Export': {'Name': 'LBR:{}:{}'.format(name, version_id)}
        }
        
        if 'Resources' not in template:
            template['Resources'] = {}
        if 'Outputs' not in template:
            template['Outputs'] = {}
        
        template['Resources'][version_resource_name] = resource
        template['Outputs'][version_name] = output

def main():
    loader, dumper = file_transformer.get_yaml_io()
    def processor(input, args):
        template = {}
        LBRRegistryConfig.parse(input).add_to_template(template)
        return template
    return file_transformer.main(
        processor,
        loader=loader,
        dumper=dumper)

if __name__ == '__main__':
    main()