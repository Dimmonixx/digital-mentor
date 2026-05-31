import subprocess
import sys
import os

# Указываем путь к папке проекта
project_dir = r'C:\Projects\digital-mentor'
bridge_path = os.path.join(project_dir, 'api_bridge.py')
print(f"Starting API Bridge from: {bridge_path}")
subprocess.run([sys.executable, bridge_path])
