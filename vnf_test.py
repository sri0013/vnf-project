#!/usr/bin/env python3
import subprocess, time

# Start VNFs
subprocess.run([
    'docker', 'run', '-d', '--name', 'firewall-vnf',
    'busybox', 'sh', '-c', 'echo firewall started; sleep 3600'
])
subprocess.run([
    'docker', 'run', '-d', '--name', 'ids-vnf',
    'busybox', 'sh', '-c', 'echo ids started; sleep 3600'
])

print("VNFs started successfully")
time.sleep(2)

# Stop and remove VNFs
subprocess.run(['docker', 'stop', 'firewall-vnf', 'ids-vnf'])
subprocess.run(['docker', 'rm',   'firewall-vnf', 'ids-vnf'])
print("VNF orchestration test complete")
