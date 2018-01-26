'''
Created on Dec 18, 2017

@author: bkehoe
'''

import argparse
import sys
import itertools

import yaml

import file_transformer

class LBRConfig(object):
    def __init__(self, cfg):
        self.common_properties = cfg.get('CommonProperties', {})
        
        self.globals = cfg.get('Globals', {})
        
        self.lbrs = {}
        for lbr_name, lbr_definition in cfg['Lambdas'].items():
            self.lbrs[lbr_name] = LBR(lbr_name, lbr_definition, self.common_properties)
    
    def add_to_template(self, template):
        template['Transform'] = 'AWS::Serverless-2016-10-31'
        
        for lbr in self.lbrs.values():
            lbr.add_to_template(template)
        
        if self.globals:
            template['Globals'] = self.globals
    
    def get_code_uris(self):
        return list(set(itertools.chain.from_iterable(lbr.get_code_uris() for lbr in self.lbrs.values())))
    
class LBR(object):
    def __init__(self, name, cfg, common_properties):
        self.name = name
        
        self.common_properties = {}
        self.common_properties.update(common_properties)
        self.common_properties.update(cfg.get('CommonProperties', {}))
        
        self.enable = cfg.get('Enable', True)
        
        self.versions = {}
        for version_id, version_definition in cfg.get('Versions').items():
            self.versions[version_id] = LBRVersion(self.name, version_id, version_definition, self.common_properties)
    
    def add_to_template(self, template):
        if not self.enable:
            return
        for version in self.versions.values():
            version.add_to_template(template)
    
    def get_code_uris(self):
        return list(set(v.get_code_uri() for v in self.versions.values()))

class LBRVersion(object):
    def __init__(self, lbr_name, version_id, cfg, common_properties):
        self.lbr_name = lbr_name
        
        self.version_id = version_id
        
        self.enable = cfg.get('Enable', True)
        
        self.beta = cfg.get('Beta', False)
        if self.beta:
            self.version_id = self.version_id + 'beta'
        
        self.properties = {}
        self.properties.update(common_properties)
        self.properties.update(cfg.get('Properties', {}))
        
        self.lbr_version_name = self.lbr_name + self.version_id
    
    def add_to_template(self, template):
        if not self.enable:
            return
        version_resource_name = self.lbr_version_name + 'Function'
        if 'Resources' not in template:
            template['Resources'] = {}
        template['Resources'][version_resource_name] = {
            'Type': 'AWS::Serverless::Function',
            'Properties': self.properties,
        }
        
        if 'Outputs' not in template:
            template['Outputs'] = {}
        template['Outputs'][self.lbr_version_name] = {
            'Value': {'Fn::GetAtt': [version_resource_name, 'Arn']},
            'Export': {'Name': 'LBR:{}:{}'.format(self.lbr_name, self.version_id)}
        }
    
    def get_code_uri(self):
        return self.properties['CodeUri']

def main():
    loader, dumper = file_transformer.get_yaml_io()
    def processor(input, args):
        template = {}
        LBRConfig(input).add_to_template(template)
        return template
    return file_transformer.main(
        processor,
        loader=loader,
        dumper=dumper)

if __name__ == '__main__':
    main()