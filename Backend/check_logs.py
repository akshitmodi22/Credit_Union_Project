import requests
from config import WATSONX_KEY, PROJECT_ID, JOB_IDS

token_resp = requests.post(
    'https://iam.cloud.ibm.com/identity/token',
    data={
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': WATSONX_KEY
    },
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
token  = token_resp.json()['access_token']
job_id = JOB_IDS['attrition_predict']
run_id = '019dd4e3-41be-7773-b901-beac12e43eb0'

log_url = (
    f'https://api.dataplatform.cloud.ibm.com/v2/jobs/{job_id}'
    f'/runs/{run_id}/logs?project_id={PROJECT_ID}&version=2023-07-07'
)
logs = requests.get(log_url, headers={'Authorization': f'Bearer {token}'}).json().get('results', [])
print('Last 15 lines:')
for line in logs[-15:]:
    print(line)
