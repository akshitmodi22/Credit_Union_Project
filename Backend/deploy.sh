#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# deploy.sh — Deploy Credit Union Skill to IBM Code Engine
# Run: chmod +x deploy.sh && ./deploy.sh
# ═══════════════════════════════════════════════════════════════

# ── Your credentials — fill these in ──────────────────────────
IBM_API_KEY="your_ibm_cloud_api_key"
REGION="us-south"
RESOURCE_GROUP="default"
CE_PROJECT="watsonx-skills"

COS_API_KEY="your_cos_api_key"
COS_INSTANCE_CRN="your_cos_instance_crn"
COS_ENDPOINT="https://s3.us-south.cloud-object-storage.appdomain.cloud"

WATSONX_URL="https://us-south.ml.cloud.ibm.com"
WATSONX_APIKEY="your_watsonx_apikey"
PROJECT_ID="754c80df-c361-4fef-b0a2-ff909ca368ad"

ATTRITION_PREDICT_JOB_ID="your_attrition_predict_job_id"
LOAN_PREDICT_JOB_ID="your_loan_predict_job_id"
PROPENSITY_PREDICT_JOB_ID="your_propensity_predict_job_id"
ATTRITION_TRAIN_JOB_ID="your_attrition_train_job_id"
LOAN_TRAIN_JOB_ID="your_loan_train_job_id"
PROPENSITY_TRAIN_JOB_ID="your_propensity_train_job_id"

APP_NAME="cu-credit-union-skill"

# ── Login to IBM Cloud ─────────────────────────────────────────
echo "Logging into IBM Cloud..."
ibmcloud login --apikey $IBM_API_KEY -r $REGION -g $RESOURCE_GROUP

# ── Install Code Engine plugin ─────────────────────────────────
ibmcloud plugin install code-engine -f

# ── Select Code Engine project ─────────────────────────────────
echo "Selecting Code Engine project..."
ibmcloud ce project select --name $CE_PROJECT 2>/dev/null || \
ibmcloud ce project create --name $CE_PROJECT

# ── Deploy app to Code Engine ──────────────────────────────────
echo "Deploying $APP_NAME to Code Engine..."
ibmcloud ce app create \
  --name $APP_NAME \
  --build-source . \
  --str buildpacks \
  --port 8080 \
  --min-scale 0 \
  --max-scale 5 \
  --cpu 1 \
  --memory 4G \
  --env COS_API_KEY=$COS_API_KEY \
  --env COS_INSTANCE_CRN=$COS_INSTANCE_CRN \
  --env COS_ENDPOINT=$COS_ENDPOINT \
  --env WATSONX_URL=$WATSONX_URL \
  --env WATSONX_APIKEY=$WATSONX_APIKEY \
  --env PROJECT_ID=$PROJECT_ID \
  --env ATTRITION_PREDICT_JOB_ID=$ATTRITION_PREDICT_JOB_ID \
  --env LOAN_PREDICT_JOB_ID=$LOAN_PREDICT_JOB_ID \
  --env PROPENSITY_PREDICT_JOB_ID=$PROPENSITY_PREDICT_JOB_ID \
  --env ATTRITION_TRAIN_JOB_ID=$ATTRITION_TRAIN_JOB_ID \
  --env LOAN_TRAIN_JOB_ID=$LOAN_TRAIN_JOB_ID \
  --env PROPENSITY_TRAIN_JOB_ID=$PROPENSITY_TRAIN_JOB_ID

# ── Get public URL ─────────────────────────────────────────────
echo ""
echo "Getting app URL..."
APP_URL=$(ibmcloud ce app get --name $APP_NAME --output url)
echo "═══════════════════════════════════════"
echo "Skill deployed!"
echo "URL: $APP_URL"
echo "Test: curl $APP_URL/health"
echo "═══════════════════════════════════════"
