"""Transformer to insert LBR references into a template.

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

import argparse
import json

import boto3
import cfn_transform

class ReferenceInserter(cfn_transform.CloudFormationTemplateTransform):
    def __init__(self, *args, **kwargs):
        super(ReferenceInserter, self).__init__(*args, **kwargs)
        
        parser = argparse.ArgumentParser()
        
        parser.add_argument('--stack-name', default='LBR-Registry', action='append')
        
        args = parser.parse_args(args=self._remaining_args)
        
        self.stack_names = args.stack_name
        
        self._resource = boto3.resource('cloudformation')
        
        self._map = {}
        for stack_name in self.stack_names:
            self._map.update(self._get_stack_map(stack_name))
    
    def _get_stack_map(self, stack_name):
        stack = self._resource.Stack(stack_name)
        
        map = {}
        for output in stack.outputs:
            name = output['ExportName']
            resource = stack.Resource(output['Value']['Ref'])
            
            types = json.loads(resource.metadata).get('LBR::Types', [])
            
            for type in types:
                map[type] = name
        return map
    
    def process_resource(self, resource_name, resource):
        resource_type = resource['Type']
        if resource_type in self._map:
            if 'Properties' not in resource:
                resource['Properties'] = {}
            resource['Properties']['ServiceToken'] = {'Fn::ImportValue': self._map[resource_type]}