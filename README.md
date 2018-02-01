# cfn-lbr-registry
## Set up a stack of Lambda functions for Lambda-backed custom resources (LBRs)


## The lbr-registry.yaml file
```
Options:
  EnableDefaultPolicies: True

Defaults:
  MemorySize: 128
  Timeout: 300

Resources:
  S3Object:
    CodeUri: ./S3Object
    [Config: <lbr.yaml contents>]
```

## The lbr.yaml file
```
Types:
- Custom::S3Object
Properties:
  Runtime: python3.6

Versions:
  v1:
    Properties:
      Handler: S3Object.handler
```

