import requests
import time
import os
import sys

# Configuration
AEGIS_URL = "http://129.213.117.130.nip.io"
API_BASE = f"{AEGIS_URL}/api/protect/queue"
AUTH = None # Add Basic Auth Tuple ("admin", "pass") if Gateway requires it for API, 
            # BUT: Gateway config usually protects /api with Basic Auth? 
            # We confirmed Gateway protects EVERYTHING.
            # So Worker needs credentials.
            
USERNAME = "admin"
PASSWORD = "AegisSec2026!" # Default, user should update if changed.

def log(msg):
    print(f"[Worker] {msg}")

def check_queue():
    try:
        res = requests.get(f"{API_BASE}/pending", auth=(USERNAME, PASSWORD))
        if res.status_code == 200:
            return res.json()
        return None
    except Exception as e:
        log(f"Error checking queue: {e}")
        return None

def process_job(job):
    job_id = job['id']
    job_type = job['type']
    log(f"Processing Job {job_id} ({job_type})")
    
    # 1. Download Input
    img_res = requests.get(f"{API_BASE}/image/{job_id}", auth=(USERNAME, PASSWORD))
    if img_res.status_code != 200:
        log("Failed to download image")
        return

    input_path = f"input_{job_id}.png"
    with open(input_path, 'wb') as f:
        f.write(img_res.content)
        
    # 2. Process (Mocking GPU work for now)
    log("Running GPU Protection...")
    time.sleep(5) # Simulate work
    
    # ACTUAL MIST/PHOTOGUARD LOGIC WOULD GO HERE
    # subprocess.call(["python", "mist.py", ...])
    
    output_path = f"output_{job_id}.png"
    # For now, just copy input to output (simulate success)
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
            
    # 3. Upload Result
    with open(output_path, 'rb') as f:
        files = {'file': f}
        res = requests.post(
            f"{API_BASE}/complete/{job_id}", 
            files=files, 
            auth=(USERNAME, PASSWORD)
        )
        
    if res.status_code == 200:
        log(f"Job {job_id} Complete!")
    else:
        log(f"Failed to upload result: {res.text}")

    # Cleanup
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)

def main():
    log(f"Starting Aegis AI Worker connecting to {AEGIS_URL}")
    while True:
        job = check_queue()
        if job:
            process_job(job)
        else:
            time.sleep(5) # Idle poll

if __name__ == "__main__":
    main()
