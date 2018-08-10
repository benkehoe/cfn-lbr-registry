"""LBR Registry configuration classes.

Copyright 2018 iRobot Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from __future__ import absolute_import

import six
import os.path
import itertools
import sys

import yaml

import file_transformer

def _combine(base, overlay, path=None):
    """combine dicts like SAM"""
    if path is None:
        path = []
    result = {}
    for key in set(six.iterkeys(base)) | set(six.iterkeys(overlay)):
        if key in base and key not in overlay:
            result[key] = base[key]
        elif key in overlay and key not in base:
            result[key] = overlay[key]
        else:
            value1 = base[key]
            value2 = overlay[key]
            if value1 == value2:
                result[key] = value1
            elif isinstance(value1, dict) and isinstance(value2, dict):
                result[key] = _combine(value1, value2, path=path+[key])
            elif isinstance(value1, list) and isinstance(value2, list):
                result[key] = list(itertools.chain(value1, value2))
            else:
                raise TypeError("Cannot merge {} with {} at {}".format(type(value1), type(value2), '/'.join(path)))
    return result

class LBRRegistryConfig(object):
    DEFAULT_MEMORY_SIZE = 128
    DEFAULT_TIMEOUT = 300
    
    DEFAULT_POLICIES = 'AdministratorAccess'
    
    @classmethod
    def get_lbr_config_paths(cls, lbr_reg_obj):
        paths = []
        for resource_name, resource_config in six.iteritems(lbr_reg_obj['Resources']):
            paths.append(LBRRegistryResource.get_lbr_config_paths(resource_config))
        return paths

    @classmethod
    def parse(cls, lbr_reg_obj):
        options = lbr_reg_obj.get('Options', {})
        globals = lbr_reg_obj.get('Globals', {})
        resources = {}
        for resource_name, resource_config in six.iteritems(lbr_reg_obj['Resources']):
            resources[resource_name] = LBRRegistryResource.parse(resource_config)
        return cls(resources, globals, options)
    
    def __init__(self, resources, globals={}, options={}):
        self.resources = resources
        self.options = options
        
        globals_default = {
            'Function': {
                'MemorySize': self.DEFAULT_MEMORY_SIZE,
                'Timeout': self.DEFAULT_TIMEOUT,
            }
        }
        
        self.globals = _combine(globals_default, globals)
        
        self.default_policies = self.DEFAULT_POLICIES if self.options.get('EnableDefaultPolicies', False) else None
        
    def add_to_template(self, template):
        template['Transform'] = 'AWS::Serverless-2016-10-31'
        
        template['Globals'] = self.globals
        
        for name, resource in six.iteritems(self.resources):
            resource.add_to_template(name, template, default_policies=self.default_policies)
        
class LBRRegistryResource(object):
    @classmethod
    def get_lbr_config_paths(cls, lbr_resource_obj):
        return lbr_resource_obj['CodeUri']
    
    @classmethod
    def parse(cls, lbr_resource_obj):
        code_uri = lbr_resource_obj['CodeUri']
        if 'Config' in lbr_resource_obj:
            config_obj = lbr_resource_obj['Config']
        else:
            with open(os.path.join(code_uri, 'lbr.yaml'), 'r') as fp:
                config_obj = yaml.load(fp)
        config = LBRConfig.parse(config_obj)
        enable = lbr_resource_obj.get('Enable', True)
        return cls(code_uri, config, enable)
    
    def __init__(self, code_uri, config, enable=True):
        self.code_uri = code_uri
        self.config = config
        self.enable = enable
    
    def add_to_template(self, name, template, default_policies=None):
        if not self.enable:
            return
        self.config.add_to_template(name, template, self.code_uri, default_policies=default_policies)

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
    
    def add_to_template(self, name, template, code_uri,  default_policies=None):
        versions = self.versions or [self.default]
        for version_id, version in six.iteritems(versions):
            version.add_to_template(name, version_id, template, code_uri, default=self.default, default_policies=default_policies)

class LBRVersionConfig(object):
    @classmethod
    def parse(cls, lbr_version_config_obj):
        types = lbr_version_config_obj.get('Types') or lbr_version_config_obj.get('Type')
        properties = lbr_version_config_obj.get('Properties')
        metadata = lbr_version_config_obj.get('Metadata')
        enable = lbr_version_config_obj.get('Enable', True)
        beta = lbr_version_config_obj.get('Beta', False)
        return cls(properties, types=types, enable=enable, beta=beta, metadata=metadata)
    
    def __init__(self, properties, types=None, enable=True, beta=False, metadata=None):
        if isinstance(types, six.string_types):
            types = [types]
        self.types = types
        self.properties = properties
        self.metadata = metadata
        self.enable = enable
        self.beta = beta
    
    def add_to_template(self, name, version_id, template, code_uri, default=None, default_policies=None):
        if not self.enable:
            return
        
        suffix = 'beta' if self.beta else ''
        version_name = '{}{}{}'.format(name, version_id, suffix)
        
        version_resource_name = version_name + 'Function'
        
        properties = {}
        if default:
            properties.update(default.properties)
        properties.update(self.properties)
        properties['CodeUri'] = code_uri
        
        if 'Policies' not in properties and default_policies:
            properties['Policies'] = default_policies
        
        resource = {
            'Type': 'AWS::Serverless::Function',
            'Properties': properties,
        }
        
        metadata = {}
        if default and default.metadata:
            metadata.update(default.metadata)
        if self.metadata:
            metadata.update(self.metadata)    
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
    action = sys.argv[1]
    if action == 'template':
        loader, dumper = file_transformer.get_yaml_io()
        def processor(input, args):
            template = {}
            LBRRegistryConfig.parse(input).add_to_template(template)
            return template
        return file_transformer.main(
            processor,
            loader=loader,
            dumper=dumper,
            args=sys.argv[2:])
    elif action == 'paths':
        with open(sys.argv[2], 'r') as fp:
            reg_cfg = yaml.load(fp)
        print(' '.join(LBRRegistryConfig.get_lbr_config_paths(reg_cfg)))
    else:
        sys.exit("Invalid action {}".format(action))

if __name__ == '__main__':
    main()