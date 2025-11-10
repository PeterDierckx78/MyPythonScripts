import os
import csv
from pathlib import Path
import configparser

def find_git_repos(root_dir, max_depth=3):
	git_repos = []
	root_dir = Path(root_dir)
	for dirpath, dirnames, filenames in os.walk(root_dir):
		rel_path = Path(dirpath).relative_to(root_dir)
		if len(rel_path.parts) > max_depth:
			# Don't go deeper than max_depth
			dirnames[:] = []
			continue
		if '.git' in dirnames:
			git_repos.append(Path(dirpath))
			dirnames.remove('.git')  # Don't descend into .git
	return git_repos

def get_remote_url(git_dir):
	config_path = git_dir / '.git' / 'config'
	if not config_path.exists():
		return ''
	config = configparser.ConfigParser(strict=False)
	try:
		#print(f"Reading {config_path}...")
		config.read(config_path)
		if 'remote "origin"' in config:
			return config['remote "origin"'].get('url', '')
		else:
			print(f"No remote 'origin' found in {config_path}")
	except Exception as e:
		print(f"Failed to read remote 'origin' for {config_path} - reason: {e}")
	return ''

def main():
	import sys
	# Parse arguments
	# Usage: python build-repo-list.py <path-to-root-folder> [max-levels] [output-folder]
	if len(sys.argv) > 1:
		root_folder = Path(sys.argv[1]).resolve()
	else:
		print("Usage: python build-repo-list.py <path-to-root-folder> [max-levels] [output-folder]")
		print("No path provided. Defaulting to current folder.")
		print("This script finds all git repos up to N levels deep (default 3), reads their remote URLs, and writes repo-list.csv with local path, remote URL, and repo name.")
		print("You can optionally specify max-levels and an output folder for the CSV file.")
		root_folder = Path(__file__).parent.resolve()

	if len(sys.argv) > 2:
		try:
			max_levels = int(sys.argv[2])
		except ValueError:
			print(f"Invalid max-levels argument '{sys.argv[2]}', using default 3.")
			max_levels = 3
	else:
		max_levels = 3

	if len(sys.argv) > 3:
		output_folder = Path(sys.argv[3]).resolve()
	else:
		output_folder = root_folder

	output_folder.mkdir(parents=True, exist_ok=True)
	folder_name = root_folder.name.lower()
	output_file = output_folder / f'repo-list-{folder_name}.csv'

	# Read existing repos if CSV exists
	existing = {}
	if output_file.exists():
		with open(output_file, newline='', encoding='utf-8') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				existing[row['local_path']] = row

	# Find new repos and update/add them
	repos = find_git_repos(root_folder, max_depth=max_levels)
	newly_added = []
	for repo_path in repos:
		remote_url = get_remote_url(repo_path)
		repo_name = repo_path.name
		key = str(repo_path)
		if key not in existing:
			newly_added.append({'local_path': key, 'remote_url': remote_url, 'repo_name': repo_name})
		existing[key] = {
			'local_path': key,
			'remote_url': remote_url,
			'repo_name': repo_name
		}

	# Write merged result
	with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=['local_path', 'remote_url', 'repo_name'])
		writer.writeheader()
		for row in existing.values():
			writer.writerow(row)
   
	print(f"CSV file written: {output_file.resolve()}")
 
	if newly_added:
		print("Newly added repos:")
		for repo in newly_added:
			print(f"  {repo['local_path']} | {repo['remote_url']} | {repo['repo_name']}")
	else:
		print("No new repos added.")

if __name__ == '__main__':
	main()
