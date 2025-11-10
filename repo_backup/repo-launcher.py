import os
import csv
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)
REPOS_DIR = os.path.join(BASE_DIR, 'repos')

class RepoLauncher(tk.Tk):
    def _filter_repos(self, *args):
        search = self.search_var.get().lower()
        # Save current selection state
        # Rebuild the tree with only matching repos, but keep check_vars for all
        self.tree.delete(*self.tree.get_children())
        for i, repo in enumerate(self.repos):
            # Show if any field matches search
            if (
                search in repo.get('repo_name', '').lower()
                or search in repo.get('local_path', '').lower()
                or search in repo.get('remote_url', '').lower()
            ):
                restored = 'Yes' if os.path.exists(repo['local_path']) else 'No'
                tags = ('restored_gray',) if restored == 'Yes' else ()
                text = '[x]' if self.check_vars[i] else '[ ]'
                self.tree.insert('', 'end', iid=str(i), text=text, values=(i+1, restored, repo['repo_name'], repo['local_path'], repo['remote_url']), tags=tags)
        self._update_checkbox_text(only_visible=True)

    def __init__(self):
        super().__init__()
        self.title('Repo Launcher')
        self.geometry('900x600')
        self.repos = []
        self.check_vars = []
        self.progress_bars = []
        self._load_repos()
        self._build_ui()

    def _load_repos(self):
        self.repos = []
        for fname in os.listdir(REPOS_DIR):
            if fname.endswith('.csv'):
                with open(os.path.join(REPOS_DIR, fname), newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Expecting at least 'remote' and 'local' columns
                        if 'remote_url' in row and 'local_path' in row:
                            row['source_csv'] = fname
                            self.repos.append(row)




    def _build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search field
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=2, column=0, columnspan=6, sticky='ew', pady=(12, 8))
        search_label = ttk.Label(search_frame, text='Search:')
        search_label.grid(row=0, column=0, sticky='w')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.grid(row=0, column=1, sticky='ew', padx=(5, 0))
        search_frame.columnconfigure(0, weight=0)
        search_frame.columnconfigure(1, weight=1)
        self.search_var.trace_add('write', self._filter_repos)

        # Table with vertical scrollbar
        columns = ('index', 'restored', 'repo_name', 'local', 'remote')
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=0, column=0, columnspan=6, sticky='nsew')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=20)
        self.tree.heading('#0', text='Select')
        self.tree.heading('index', text='Index')
        self.tree.heading('restored', text='Restored')
        self.tree.heading('repo_name', text='Repo Name')
        self.tree.heading('local', text='Local Folder')
        self.tree.heading('remote', text='Remote URL')
        self.tree.column('#0', width=50, minwidth=20, stretch=False, anchor='center')
        self.tree.column('index', width=50, minwidth=20, stretch=False, anchor='center')
        self.tree.column('restored', width=80, minwidth=50, stretch=False, anchor='center')
        self.tree.column('repo_name', width=220, minwidth=120, stretch=True, anchor='w')
        self.tree.column('local', width=180, minwidth=80, stretch=True, anchor='w')
        self.tree.column('remote', width=220, minwidth=120, stretch=True, anchor='w')

        # Add vertical scrollbar
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        tree_scrollbar.grid(row=0, column=1, sticky='ns')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Add checkboxes and progress bars
        self.check_vars = []
        self.progress_bars = []
        self.tree.tag_configure('restored_gray', background='#e0e0e0')
        for i, repo in enumerate(self.repos):
            self.check_vars.append(False)
            restored = 'Yes' if os.path.exists(repo['local_path']) else 'No'
            tags = ('restored_gray',) if restored == 'Yes' else ()
            self.tree.insert('', 'end', iid=str(i), text='[ ]', values=(i+1, restored, repo['repo_name'], repo['local_path'], repo['remote_url']), tags=tags)
        self._update_checkbox_text()
        self.tree.bind('<ButtonRelease-1>', self._on_tree_click)

        # Enable All and Clear All buttons side by side on the left
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        ttk.Button(button_frame, text='Enable All', command=self._enable_all).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text='Clear All', command=self._clear_all).pack(side='left')

        # Restore button on the right
        ttk.Button(frame, text='Restore Selected', command=self._restore_selected).grid(row=3, column=2, pady=10, sticky='e')

        # Progress frame
        self.progress_frame = ttk.Frame(frame)
        self.progress_frame.grid(row=4, column=0, columnspan=4, sticky='ew')
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Output text box for clone process
        self.output_text = tk.Text(frame, height=10, wrap='word', state='disabled', bg='white')
        self.output_text.grid(row=5, column=0, columnspan=5, sticky='nsew', pady=(10,0))
        frame.rowconfigure(5, weight=1)


    def _update_checkbox_text(self, only_visible=False):
        # If only_visible is True, only update checkboxes for visible items (filtered)
        if only_visible:
            for iid in self.tree.get_children():
                idx = int(iid)
                text = '[x]' if self.check_vars[idx] else '[ ]'
                self.tree.item(iid, text=text)
        else:
            for i, checked in enumerate(self.check_vars):
                text = '[x]' if checked else '[ ]'
                self.tree.item(str(i), text=text)

    def _on_tree_click(self, event):
        # Detect if click is on the tree (checkbox) column
        region = self.tree.identify('region', event.x, event.y)
        if region == 'tree':
            row = self.tree.identify_row(event.y)
            if row:
                idx = int(row)
                self.check_vars[idx] = not self.check_vars[idx]
                self._update_checkbox_text(only_visible=True)

    def _enable_all(self):
        for i in range(len(self.check_vars)):
            self.check_vars[i] = True
        self._update_checkbox_text()

    def _clear_all(self):
        for i in range(len(self.check_vars)):
            self.check_vars[i] = False
        self._update_checkbox_text()

    def _restore_selected(self):
        selected = [i for i, checked in enumerate(self.check_vars) if checked]
        # Filter out already restored repos and those without remote_url
        to_restore = [i for i in selected if not os.path.exists(self.repos[i]['local_path']) and self.repos[i].get('remote_url')]
        if not to_restore:
            messagebox.showinfo('No Selection', 'No selected repositories need to be restored or are missing a remote URL.')
            return
        # Clear previous progress bars
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        self.progress_bars = []
        for idx in to_restore:
            pb = ttk.Progressbar(self.progress_frame, length=300, mode='determinate')
            pb.grid(row=idx, column=0, sticky='w', pady=2)
            label = ttk.Label(self.progress_frame, text=f"Cloning {self.repos[idx]['local_path']}" if self.repos[idx].get('remote_url') else f"No remote_url for {self.repos[idx]['local_path']}")
            label.grid(row=idx, column=1, sticky='w')
            self.progress_bars.append(pb)
        threading.Thread(target=self._run_clone, args=(to_restore,), daemon=True).start()
        # After starting restore, update the 'Restored' column for all rows
        self.after(1000, self._refresh_restored_column)

    def _refresh_restored_column(self):
        for i, repo in enumerate(self.repos):
            restored = 'Yes' if os.path.exists(repo['local_path']) else 'No'
            values = list(self.tree.item(str(i), 'values'))
            if len(values) == 5:
                values[1] = restored  # 'restored' is now at index 1
                tags = ('restored_gray',) if restored == 'Yes' else ()
                self.tree.item(str(i), values=values, tags=tags)

    def _run_clone(self, selected):
        for i, idx in enumerate(selected):
            repo = self.repos[idx]
            remote = repo['remote_url']
            local = repo['local_path']
            pb = self.progress_bars[i]
            self._clone_repo(remote, local, pb)

    def _clone_repo(self, remote, local, pb):
        def update_progress(val):
            pb['value'] = val
            self.update_idletasks()
        def append_output(text):
            self.output_text.configure(state='normal')
            self.output_text.insert('end', text)
            self.output_text.see('end')
            self.output_text.configure(state='disabled')
        update_progress(10)
        try:
            append_output(f'Cloning {remote} to {local}...\n')
            if os.path.exists(local):
                append_output(f'  Skipped: {local} already exists.\n')
                update_progress(100)
                return
            update_progress(20)
            proc = subprocess.Popen(['git', 'clone', remote, local], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                append_output(line)
                update_progress(min(pb['value']+10, 90))
            proc.wait()
            if proc.returncode == 0:
                append_output(f'  Success: {local} cloned.\n')
            else:
                append_output(f'  Error: Failed to clone {remote} (exit code {proc.returncode})\n')
            update_progress(100 if proc.returncode == 0 else 0)
        except Exception as e:
            append_output(f'  Exception: {e}\n')
            update_progress(0)

if __name__ == '__main__':
    app = RepoLauncher()
    app.mainloop()
