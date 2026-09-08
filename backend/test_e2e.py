import requests
import json
from datetime import datetime, timedelta

base_url = 'http://localhost:8000/api'

# 1. Verify a challenge
challs = requests.get(f'{base_url}/challenges/').json()
pending = [c for c in challs if c['status'] == 'pending_verification']
if not pending:
    print('No pending challenges found. Cannot proceed.')
    exit(1)
c = pending[0]
cid = c['id']
print(f'Verifying challenge: {cid}')

res = requests.patch(f'{base_url}/challenges/{cid}/verify', json={'verified': True})
if res.status_code != 200:
    print(res.text)
    exit(1)

# 2. Get some active universities
unis = requests.get(f'{base_url}/universities/?status=ACTIVE').json()
org_ids = [u['id'] for u in unis[:2]]
print(f'Routing to orgs: {org_ids}')

# 3. Route challenge
deadline = (datetime.utcnow() + timedelta(days=7)).isoformat()
payload = {'org_ids': org_ids, 'deadline': deadline, 'note': 'Test routing'}
res = requests.post(f'{base_url}/challenges/{cid}/route', json=payload)
if res.status_code != 200:
    print(res.text)
    exit(1)
batch = res.json()
print(f"Routed successfully. Batch ID: {batch['id']}")

# 4. Accept invitation
inv_id = batch['invitations'][0]['id']
print(f'Accepting invitation: {inv_id}')
res = requests.post(f'{base_url}/challenges/invitations/{inv_id}/accept')
if res.status_code != 200:
    print(res.text)
    exit(1)
print('Accepted successfully')
print(res.json())

# 5. Check challenge status
c_after = requests.get(f'{base_url}/challenges/{cid}').json()
print(f"Final challenge status: {c_after['status']}")
