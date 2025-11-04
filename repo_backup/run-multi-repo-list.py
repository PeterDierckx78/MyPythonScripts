import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / 'build-repo-list.py'
PYTHON_EXE = sys.executable

folders = [r'C:\gitlab', r'C:\github']
repos_subfolder = Path(__file__).parent / 'repos'
repos_subfolder.mkdir(exist_ok=True)

for folder in folders:
    print(f'Processing {folder}...')
    subprocess.run([
        PYTHON_EXE,
        str(SCRIPT_PATH),
        folder,
        '3',
        str(repos_subfolder)
    ], check=True)
print('CSV files created for all folders in repos subfolder.')
