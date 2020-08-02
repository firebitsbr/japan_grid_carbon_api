#!/bin/bash
COMPANY=$1
FUNCTION=$2

echo "Deploying Function $FUNCTION for $COMPANY"
cd cloud_functions/api/utilities/$COMPANY/scraper/

gcloud functions deploy $FUNCTION --runtime python37 --trigger-http

echo "Done"