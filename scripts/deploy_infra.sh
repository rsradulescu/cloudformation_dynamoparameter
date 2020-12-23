#!/bin/bash
if ! [ -x "$(command -v sam)" ]; then
    date '+%Y-%m-%d %H:%M:%S'
    echo "sam not found"
    exit 1
fi

if ! [ -x "$(command -v aws)" ]; then
    date '+%Y-%m-%d %H:%M:%S'
    echo "aws not found"
    exit 1
fi

#######################################################
# DESCOMENTAR, CAMBIAR LOS VALORES Y EJECUTAR LOCALMENTE:

export AWS_PROFILE="default"
export ENV="rocio"
export PROJECT="acciona-s3dynamoparameter"
export LOG_RETENTION=30 ## IN DAYS
export STACK=$PROJECT-$ENV-deployinfra
export BUCKET=$PROJECT-$ENV-deployinfra
#######################################################

ENV=${ENV}
AWS_PROFILE=${AWS_PROFILE}
BUCKET=${BUCKET}
STACK=${STACK}
PROJECT=${PROJECT}

ROOT_PATH="$(pwd)"
ROOTSTACK="101_deployinfra"
SOURCE="$ROOT_PATH/cloudformations/$ROOTSTACK"
FUNCTIONS="$ROOT_PATH/functions/*"
FUNCTIONS_PATH="$ROOT_PATH/functions/"
BUILD_PATH="$ROOT_PATH/.aws-sam/build/"
UUID=$$

LOG_RETENTION=${LOG_RETENTION}

#######################################################

#aws s3 cp $SOURCE/nestedstacks/parameters01.yaml s3://arqdatos-$ENV-$MULTISTACK/$ROOTSTACK/nestedstacks/parameters01$UUID.yaml

#######################################################
# PROCESO DE DESPLIEGUE DEL STACK:



date=$(date '+%Y-%m-%d %H:%M:%S')
echo "$date [ INFO ] :: VALIDATING TEMPLATE ~/cloudformations/template.yaml"
sam validate \
 --template "$SOURCE/template.yaml" \
 --profile ${AWS_PROFILE}

date=$(date '+%Y-%m-%d %H:%M:%S')
echo "$date [ INFO ] :: BUILDING SAM $SOURCE/template.yaml"
sam build -t "$SOURCE/template.yaml" -s $FUNCTIONS_PATH

date=$(date '+%Y-%m-%d %H:%M:%S')
echo "$date [ INFO ] :: PACKAGING SAM PROJECT"
sam package \
    --profile $AWS_PROFILE  \
    --template-file "$BUILD_PATH/template.yaml" \
    --output-template-file "$BUILD_PATH/template_$UUID.yaml" \
    --s3-bucket $BUCKET

date=$(date '+%Y-%m-%d %H:%M:%S')
echo "$date [ INFO ] :: DEPLOYING SAM PROJECT"
sam deploy \
    --profile $AWS_PROFILE \
    --template-file "$BUILD_PATH/template_$UUID.yaml" \
    --stack-name $STACK \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
    --region us-east-1 \
    --tags Project=$PROJECT \
    --parameter-overrides \
        UUID=$UUID \
        Project=$PROJECT \
        Environment=$ENV \
        LogLevel=debug \
        RetentionInDays=$LOG_RETENTION

rm -rf "$(pwd)/.aws-sam"
