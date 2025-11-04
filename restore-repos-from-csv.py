import csv
import subprocess
from pathlib import Path
import sys

# Suffix to add to all root paths when restoring repos (for testing)
#SUFFIX = "-testrestore"
SUFFIX = ""

# Folder containing CSV files
data_folder = Path(__file__).parent / 'repos'

# Find all repo-list-*.csv files
csv_files = list(data_folder.glob('repo-list-*.csv'))

for csv_file in csv_files:
    print(f'Restoring repos from {csv_file}...')
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            local_path = row.get('local_path', '').strip()
            remote_url = row.get('remote_url', '').strip()
            repo_name = row.get('repo_name', '').strip()
            if not local_path or not remote_url:
                continue
            # Determine root path and repo folder, add suffix for testing
            repo_root = Path(local_path).parent
            repo_root_with_suffix = Path(str(repo_root) + SUFFIX)
            repo_folder = repo_root_with_suffix / repo_name
            repo_folder.parent.mkdir(parents=True, exist_ok=True)
            if repo_folder.exists():
                print(f'Skipping existing repo: {repo_folder}')
                continue
            print(f'Cloning {remote_url} to {repo_folder}...')
            subprocess.run([
                'git', 'clone', remote_url, str(repo_folder)
            ], check=True)
print('Restore complete.')
