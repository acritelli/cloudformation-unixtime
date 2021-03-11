# Overview

This repository presents a simple example of developing a Python Lambda function to implement a CloudFormation Custom Resource.

# Usage

## Uploading the Lambda code to S3

The CloudFormation template deploys a Lambda function to implement a Custom Resource (`UnixTime`). The code for this function must be located in S3. To deploy to S3 from a terminal:

```
# Obtain the current ZIP file. If you are interested in building the .zip manually, instructions are included in the "Build" section of the README

# Create an S3 bucket
aws s3 mb s3://acritelli-unixtime-function

# Place the zip file into the bucket
aws s3 cp function.zip s3://acritelli-unixtime-function/function.zip
```

## Deploying a new stack from the Cloud Formation Template

The CloudFormation template can be used to deploy a complete stack with the Lambda function and a Custom Resource that interacts with the function. The example below demonstrates this process from the CLI, but the UI works just as well.

First, clone the repository and change into the repo directory:

```
git clone acritelli/cloudformation-unixtime.git
cd cloudformation-unixtime
```

Then, create the stack. Notice that the parameters passed specifies the previously created  S3 Bucket and Key, along with a state (`Rome`) to obtain the `unixtime` for.

```
aws cloudformation create-stack --stack-name unixtime-test --template-body file://cloudformation/cloudformation.yaml --capabilities CAPABILITY_IAM --parameters ParameterKey=UnixTimeLambdaS3Bucket,ParameterValue=acritelli-unixtime-function ParameterKey=UnixTimeLambdaS3Key,ParameterValue=function.zip ParameterKey=State,ParameterValue=Rome
```

Confirm that the `UnixTime` output was populated by the Custom Resource (omit the `jq` command if you don't have it installed):

```
aws cloudformation describe-stacks --stack-name unixtime-test | jq .Stacks[0].Outputs
[
  {
    "OutputKey": "UnixTime",
    "OutputValue": "1615411187",
    "Description": "The time retrieved from the UnixTime lookup service"
  }
]
```

Finally, test an update of the stack (and optionally repeat the previous `describe-stacks` to see the updated Output):

```
aws cloudformation update-stack --stack-name unixtime-test --template-body file://cloudformation/cloudformation.yaml --capabilities CAPABILITY_IAM --parameters ParameterKey=State,ParameterValue=Zurich
```

# Explanation

There are two components to making this custom resource work, each described in further detail below.

1. The Lambda function
2. The CloudFormation template

## Lambda function

The Lambda Function receives requests per the [CloudFormation Custom Resource request definition](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/crpg-ref-requests.html). It looks for a `State` key in the `ResourceProperties` part of the request. It then reaches out to the [WorldTimeAPI](https://worldtimeapi.org/) to obtain a time object for the given European state. Assuming that a time is returned from the API, this is then returned to the custom resource for further use inside the stack.

The function makes use of the [CloudFormation Helper Python library](https://github.com/aws-cloudformation/custom-resource-helper) to manage some of the specifics of dealing with CloudFormation requests, such as sending the response to the Presigned S3 URL. The helper library also handles bubbling up exceptions to CloudFormation, as can be seen in the custom exception messages that are listed throughout the code.

The function is designed to run in a Lambda Python 3.8 runtime.

## CloudFormation Template

The `unixtime.yaml` CloudFormation template provides an example of deploying and using the `UnixTime` Custom Resource. The template manages three resources:

|        Resource Name        |                                                              Description                                                              |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| UnixTimeLambdaExecutionRole | A basic IAM policy for the UnixTime Lambda Function, modeled after the default IAM policy created when deploying new Lambda resources |
| UnixTimeLambdaFunction      | An instantiation of the lambda function necessary to service requests for the UnixTime Custom Resource                                |
| UnixTime                    | The UnixTime custom resource, implemented by the Lambda function                                                                      |

The template also takes three parameters:

|     Parameter Name     |                             Description                             |
| ---------------------- | ------------------------------------------------------------------- |
| UnixTimeLambdaS3Bucket | The S3 bucket location for the UnixTime Lambda code, as a .zip file |
| UnixTimeLambdaS3Key    | The S3 key location for the UnixTime Lambda code, as a .zip file    |
| State                  | A European state to query the WorldTimeAPI for                      |

The template provides a single output:

| Output Name |                            Description                            |
| ----------- | ----------------------------------------------------------------- |
| UnixTime    | The `unixtime` from the WorldTimeAPI for the given European State |


# Build Instructions

The usage instructions assume that you use the prebuilt zip archive for the Lambda function's code. If you want to build the zip manually, follow the process below.

```
# Clone the repository and change into the directory
git clone acritelli/cloudformation-unixtime.git
cd cloudformation-unixtime

# Ensure that you have Python 3.8 installed
python --version

# Change into the lambda directory and install the needed libraries
pip3 install --target ./package requests crhelper

# Change into the package directory and create the zip
cd package
zip -r ../function.zip .

# Change back to the lambda directory and add the function itself to the zip
cd ../
zip -g function.zip lambda_function.py
```

# Useful Resources

The links below outline some useful resources that I used while determining the best way to implement this.

* [Official CloudFormation User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html)
* [CloudFormation Custom Resource Walkthrough](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/walkthrough-custom-resources-lambda-lookup-amiids.html)
* [AWS CloudFormation Python Helper Library](https://github.com/aws-cloudformation/custom-resource-helper)
* [CloudFormation Custom Resources in Python AWS Blog Article](https://aws.amazon.com/blogs/infrastructure-and-automation/aws-cloudformation-custom-resource-creation-with-python-aws-lambda-and-crhelper/)


# Potential Areas of Improvement
