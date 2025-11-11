# Repo Backup Launcher

This project provides a graphical tool to restore multiple git repositories from CSV lists, making it easy to clone and manage many repositories at once. It is especially useful for backup, migration, or onboarding scenarios where you need to restore a set of repositories to local folders.

## Features
- **Tkinter-based GUI**: Presents a table of repositories loaded from CSV files in the `repos` folder.
- **Checkbox Selection**: Select which repositories to restore using checkboxes.
- **Batch Actions**: Enable all, clear all, and restore selected repositories with one click.
- **Progress Display**: Shows progress bars and output logs for each clone operation.
- **Search/Filter**: Quickly filter repositories by name, path, or URL.
- **Restored Status**: Indicates which repositories have already been restored.

## Folder Structure
```
repo_backup/
    build.bat
    repo-launcher.py
    restore-repos-from-csv.py
    run-multi-repo-list.py
    repos/
        repo-list-github.csv
        repo-list-gitlab.csv
```

- **repo-launcher.py**: Main GUI application for restoring repositories.
- **repos/**: Folder containing CSV files with repository lists. Each CSV should have at least `remote_url` and `local_path` columns.
- **build.bat**: Batch script to build a standalone Windows executable using PyInstaller.


## How to Use
1. Place your CSV files in the `repos` folder. Each row should specify a `remote_url` and a `local_path`.
2. Run `repo-launcher.py` with Python 3.x, or use the built executable (see below).
3. Use the GUI to select and restore repositories as needed.

## Updating the CSV Files
To automatically update or generate the CSV files in the `repos` folder, use the `run-multi-repo-list.py` script. This script scans the specified local folders (by default `C:\gitlab` and `C:\github`) and generates or updates CSV files for each folder in the `repos` subfolder.

**To update the CSVs:**

```
python run-multi-repo-list.py
```

This will call `build-repo-list.py` for each folder and create or update the CSV files in the `repos` directory. Make sure to adjust the `folders` list in `run-multi-repo-list.py` if you want to scan different directories.

## Building the Executable
To create a standalone Windows executable, run:

```
build.bat
```

This will use PyInstaller to bundle the application and all required data into a single `.exe` file. The `--add-data repos;repos` option ensures the `repos` folder is included in the build.

## Requirements
- Python 3.x
- Tkinter (usually included with Python)
- PyInstaller (for building the executable)
- Git (must be available in your system PATH)

## Example CSV Format
```
remote_url,local_path
https://github.com/user/repo1.git,C:/repos/repo1
https://gitlab.com/group/repo2.git,C:/repos/repo2
```

## License
MIT License
