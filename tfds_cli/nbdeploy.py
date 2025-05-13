#!/usr/bin/env python3
"""
Script to stamp Git revision information into Jupyter notebooks
and upload them to S3. Uses cell tags to identify the Git info cell.
"""

import os
import sys
from datetime import datetime, timezone
import nbformat
import boto3
import git
from common import get_config, find_dir

_deploy_config = None
def get_deploy_config():
    global _deploy_config
    if _deploy_config is None:
        _deploy_config = get_config("nbdeploy")['config']
    return _deploy_config

get_deploy_config()


_s3_config = None
def get_s3_config():
    global _s3_config
    if _s3_config is None:
        cfg = get_config("s3")
        if not cfg:
            raise FileNotFoundError ('could not find s3 config')
        _s3_config = cfg['config']
        _s3_config["bucket"] = 'notebooks'
    return _s3_config

get_s3_config()

def get_git_info():
    """Get Git information using GitPython."""
    try:
        repo = git.Repo('.')
        head = repo.head.commit
        url = repo.remotes.origin.url
        if url is None:
            url = "No remote URL found"
        else:
            url = f"{url.rstrip('.git')}/commit/{head.hexsha}"
        return {
            'repo': repo.working_tree_dir,
            'branch': repo.active_branch.name,
            'revision': head.hexsha[:7],  # Short hash
            'commit_date': head.committed_datetime.isoformat(),
            'author': f"{head.author.name}",
            'deployed': datetime.now(timezone.utc).isoformat(),
            'url': url
        }
    except git.InvalidGitRepositoryError:
        print("Error: Not a git repository")
        sys.exit(1)
    except Exception as e:
        print(f"Error getting git info: {e}")
        sys.exit(1)

def stamp_notebook(input_path, output_path):
    """
    Add Git revision information to notebook metadata and
    insert/update a markdown cell at the top with revision info.
    Uses cell tags to identify the Git info cell.
    """
    try:
        git_info = get_git_info()
        # Load the notebook
        with open(input_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        # Add git info to notebook metadata
        if 'metadata' not in notebook:
            notebook['metadata'] = {}
        notebook['metadata']['git_info'] = git_info
        url = git_info['url']
        # Create the revision markdown content
        revision_text = f"""
# Notebook: {os.path.basename(input_path)}

> **Git Revision**: `{git_info['revision']}` | **Branch**: `{git_info['branch']}`

> **Commit Date**: {git_info['commit_date']} | **Author**: {git_info['author']}

> **deployed**: {git_info['deployed']}

> [{url}]({url})
"""

        # Look for a cell with the 'gitinfo' tag
        gitinfo_cell_index = None
        for i, cell in enumerate(notebook.cells):
            cell_metadata = cell.get('metadata', {})
            tags = cell_metadata.get('tags', [])

            if 'gitinfo' in tags:
                gitinfo_cell_index = i
                break

        # If a gitinfo cell was found, update it
        if gitinfo_cell_index is not None:
            notebook.cells[gitinfo_cell_index]['source'] = revision_text
        # Otherwise, create a new cell with the gitinfo tag
        else:
            revision_cell = nbformat.v4.new_markdown_cell(revision_text)

            # Set the gitinfo tag on the cell
            if 'metadata' not in revision_cell:
                revision_cell['metadata'] = {}
            if 'tags' not in revision_cell['metadata']:
                revision_cell['metadata']['tags'] = []
            revision_cell['metadata']['tags'].append('gitinfo')

            # Add the cell at the top of the notebook
            notebook.cells.insert(0, revision_cell)
        containing_folder = os.path.dirname(output_path)
        os.makedirs(containing_folder, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(notebook, f)

        return notebook
    except Exception as e:
        print(f"Error processing notebook {input_path}: {e}")
        return None

def upload_to_s3(file_path, s3_key):
    """Upload a file to S3 bucket."""
    s3_config = get_s3_config()
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=s3_config["access_key"],
        aws_secret_access_key=s3_config["secret_key"],
        endpoint_url=s3_config["url"],
    )
    try:
        text = f"{file_path} to S3 bucket '{s3_config['bucket']}' as '{s3_key}'"
        print(f"Uploading {text}...")
        s3_client.upload_file(file_path, s3_config["bucket"], s3_key)
        print(f"Upload succeeded: {text}.")
        return True
    except Exception as e:
        print(f"Upload failed {text}: {e}")
        return False

def process_notebooks(notebooks_dir, temp_dir, s3_prefix):
    """
    Process each notebook in the specified directory, stamp it with Git info,
    and upload it to S3.
    """
    # Get git information
    git_info = get_git_info()
    print(f"Stamping notebooks with Git revision: {git_info}")

    stamped_notebooks = []
    for root, _, files in os.walk(notebooks_dir):
        for file in files:
            if file.endswith('.ipynb'):
                notebook_path = os.path.join(root, file)
                rel_path = os.path.relpath(notebook_path, notebooks_dir)
                print(f"Processing {rel_path}...")
                stamped_path = os.path.join(temp_dir, rel_path)
                nb = stamp_notebook(notebook_path, stamped_path)
                if nb:
                    stamped_notebooks.append((stamped_path, os.path.join(s3_prefix, rel_path)))
                else:
                    print(f"Failed to stamp notebook {notebook_path}")

    # Upload to S3
    if stamped_notebooks:
        print(f"Found {len(stamped_notebooks)} notebooks to upload")
        for local_path, s3_key in stamped_notebooks:
            upload_to_s3(file_path=local_path, s3_key=s3_key)
            if get_deploy_config().get('clean_up_temp',True):
                os.remove(local_path)  # Clean up local copy after upload

def process_repo(repo_name, notebook_dirs, temp_dir):
    """
    Process each notebook in the specified directory, stamp it with Git info,
    and upload it to S3.
    """
    # find repo
    repo_dir = find_dir(repo_name)
    if not repo_dir:
        print(f"Error: git repo '{repo_name}' not found")
        return 1
    os.chdir(repo_dir)

    git_info = get_git_info()
    print(f"Stamping notebooks with Git revision: {git_info}")
    for dir in notebook_dirs:
        notebooks_dir = os.path.join(repo_dir, dir)
        if os.path.exists(notebooks_dir):
            notebooks_dir = os.path.abspath(notebooks_dir)
            print(f"Found notebooks: {notebooks_dir}")
        else:
            print(f"Error: notebooks directory '{notebooks_dir}' not found in {repo_dir}")
            continue

        process_notebooks(
            notebooks_dir=notebooks_dir,
            temp_dir=temp_dir,
            s3_prefix=os.path.join(repo_name, dir)
        )



def main():
    start_dir = os.getcwd()
    temp_dir = get_deploy_config().get('temp_folder')

    # create temp dir
    temp_dir = os.path.abspath(temp_dir)
    pre_existing_temp_dir = os.path.exists(temp_dir)
    if not pre_existing_temp_dir:
        os.makedirs(temp_dir, exist_ok=True)

    for repo in get_deploy_config()['repositories']:
        repo_name = list(repo.keys())[0]
        process_repo(
            repo_name=repo_name,
            notebook_dirs=repo['folders'],
            temp_dir=temp_dir
        )

    os.chdir(start_dir)
    if not pre_existing_temp_dir and get_deploy_config().get('clean_up_temp',True):
        os.rmdir(temp_dir)
    print("Deployment complete!")

if __name__ == "__main__":
    main()
