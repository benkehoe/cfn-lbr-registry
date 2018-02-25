# cfn-lbr-registry
## Set up a stack of Lambda functions for Lambda-backed custom resources (LBRs)

cfn-lbr-registry creates CloudFormation stacks containing Lambda functions for custom resources.
The ARNs of these functions are exported into CloudFormation, allowing you to import them in other stacks to use these custom resources.

To get started, it's assumed you've got directories containing your custom resource Lambdas. Inside the directory for each Lambda, you need an `lbr.yaml` file. Then, you need an `lbr-registry.yaml` file that links to the directories. Then you run `cfn-lbr-registry deploy`, and you'll get a stack named LBR-Registry. 

## LBR definitions (the lbr.yaml file)
Each LBR needs an LBR definition. This definition mostly specifies the properties for the Lambda resource in the generated stack. It contains three sections:
* **Versions**:
  * This section contains version definitions. Each version will get its own Lambda function, allowing for backwards-incompatible changes. Paying attention to versions is important, because CloudFormation stacks can be long-lived, and the version of the LBR that deletes the resource must be compatible with the version that created it.
  * The Versions section is an object mapping version name (an arbitrary string) to a version definition.
  * A version definition contains a Properties section that, when overlaid on the top-level Properties section and the Defaults section from the `lbr-registry.yaml`, comprises the required properties for an AWS::Serverless::Function resource.
* **Types**: this is an optional section. It should be a list of the CloudFormation resource types supported by the LBR. This is primarily for documentation purposes. It is put in the metadata for the Lambda resource, allowing for programmatic interaction, if desired.
* **Properties**: this is an optional section that defines default properties for all versions.
  * The properties `MemorySize` and `Timeout` default to 128 and 300, respectively, if they are not provided.

You can put this definition in a file called `lbr.yaml` in your LBR's code directory, or you can inline it in the `lbr-registry.yaml` file (see below).

### Example
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


## The lbr-registry.yaml file
The `lbr-registry.yaml` file defines the set of LBRs to deploy as a stack. It contains three sections:
* **Resources**: This is an object mapping LBR name (what you'll use to reference the LBR in other stacks) to a resource definition: this is simply an object containing the `CodeUri` for the LBR. If that CodeUri is a directory containing the LBR definition in an `lbr.yaml` file, you're done. Otherwise, the LBR definition can provided under the `Config` key.
* **Globals**: An optional section corresponding to the Globals in an AWS SAM template. Use this for defining default values for properties across your LBRs.
* **Options**: Configure the LBR registry. Currently, the options are:
  * `EnableDefaultPolicies`: a bool (false by default) that will attach the AdministratorAccess policy to your LBRs. This is useful for development, but it's a good idea to define least-privilege policies per LBR (or even per LBR version, if they differ).

### Example

```
Options:
  EnableDefaultPolicies: True

Globals:
  Function:
    Properties:
      MemorySize: 128
      Timeout: 300

Resources:
  S3Object:
    CodeUri: ./S3Object
    [Config: <LBR definition>]
```

## Deployment

Deployment happens through the `cfn-lbr-registry` executable, which is a wrapper around a makefile. In general, you'll likely only use `cfn-lbr-registry deploy [--stack-name NAME]`. The steps are, in order:

* `template`: create the AWS SAM template from the `lbr-registry.yaml` file. This appears as `lbr-registry-artifact-template.yaml` in the current directory.
* `package`: package and upload the LBR sources and insert their ARNs into the template. This is just calls `aws cloudformation package`, and outputs to `lbr-registry-artifact-packaged-template.yaml.
* `deploy`: Deploy the stack using the given stack name, or "LBR-Registry" by default. This just calls `aws cloudformation deploy`.

The process generates templates in the current directory; if this is version-controlled, it's a good idea to add `lbr-registry-artifact*` to your ignore file.

## Referencing in other stacks

The deployed stack exports the ARNs of each of the functions as "LBR:<LBR name>:<version id>". Note that the LBR name is defined by the `lbr-registry.yaml` file, not in the LBR source.

To use an LBR, you just set `ServiceToken` using `Fn::ImportValue`:
```
MyS3Object:
  Type: Custom::S3Object
  ServiceToken: {"Fn::ImportValue": "LBR:S3Object:v1"}
  Properties:
    Bucket: MyBucket
    Key: MyKey
    Text: Hello world!
```

## Selecting resources

Individual LBRs and LBR versions can be disabled. In the `lbr-registry.yaml` file, set `Enabled=False` in the resource definition. In an `lbr.yaml` file, `Enabled=False` can be set either at the top level, or on a version definition.