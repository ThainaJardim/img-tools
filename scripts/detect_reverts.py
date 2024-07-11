import subprocess
from datetime import datetime, timedelta
import os
from typing import List, Tuple, Set

def run_git_command(command: List[str]) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error executing command {' '.join(command)}: {e.stderr}")
        raise

def get_commit_diff(commit: str) -> List[str]:
    result = run_git_command(["git", "show", commit, "--pretty=format:", "--name-only"])
    files_changed = result.stdout.strip().split('\n')
    return files_changed

def get_main_or_master_branch() -> str:
    result = run_git_command(["git", "branch", "-r", "--list", "origin/main", "origin/master"])
    branches = result.stdout.strip().split('\n')
    if "origin/main" in branches:
        return "main"
    elif "origin/master" in branches:
        return "master"
    else:
        raise ValueError("Neither 'main' nor 'master' branch found in the repository")

def get_merges_in_branch_since(branch: str, since_date: str) -> List[str]:
    result = run_git_command(["git", "rev-list", branch, "--merges", f"--since={since_date}", "--reverse"])
    merges = result.stdout.strip().split('\n')
    return merges

def get_diff_between_commits(commit1: str, commit2: str) -> str:
    result = run_git_command(["git", "diff", commit1, commit2])
    return result.stdout.strip()

def get_second_parent_commit(commit: str) -> str:
    print(f"Obtaining second parent for commit {commit}")
    result = run_git_command(["git", "rev-parse", f"{commit}^2"])
    second_parent_commit = result.stdout.strip()
    print(f"Second parent of commit {commit}: {second_parent_commit}")
    return second_parent_commit

def parse_diff(diff: str) -> Tuple[Set[str], Set[str]]:
    added_lines = set()
    removed_lines = set()
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added_lines.add(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removed_lines.add(line[1:])
    return added_lines, removed_lines

def is_revert(commit: str, merges: List[str]) -> bool:
    commit_files = get_commit_diff(commit)
    for m in merges:
        try:
            potential_original_commit = get_second_parent_commit(m)
        except subprocess.CalledProcessError:
            continue

        if commit == potential_original_commit:
            continue

        original_files = get_commit_diff(potential_original_commit)

        if set(commit_files) == set(original_files):
            diff_current = get_diff_between_commits(commit, potential_original_commit)
            diff_reverse = get_diff_between_commits(potential_original_commit, commit)

            added_current, removed_current = parse_diff(diff_current)
            added_reverse, removed_reverse = parse_diff(diff_reverse)

            if added_current == removed_reverse and removed_current == added_reverse:
                print(f"Commit {commit} is a revert of commit {potential_original_commit}")
                return True
    return False

def get_date_six_months_ago() -> str:
    six_months_ago = datetime.now() - timedelta(days=180)
    return six_months_ago.strftime('%Y-%m-%d')

def main():
    newrev = os.getenv('NEW_COMMIT_HASH')
    if not newrev:
        raise EnvironmentError("Environment variable 'NEW_COMMIT_HASH' not set")

    since_date = get_date_six_months_ago()
    branch = get_main_or_master_branch()
    merges = get_merges_in_branch_since(branch, since_date)

    if is_revert(newrev, merges):
        print(newrev)
        return newrev

if __name__ == "__main__":
    main()
