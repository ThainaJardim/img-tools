import subprocess
import os
from datetime import datetime, timedelta

def get_commit_diffs(oldrev, newrev):
    result = subprocess.run(
        ["git", "rev-list", f"{oldrev}..{newrev}"],
        capture_output=True,
        text=True
    )
    commits = result.stdout.strip().split('\n')
    return commits

def get_all_commits_since(since_date):
    result = subprocess.run(
        ["git", "rev-list", "--all", f"--since={since_date}"],
        capture_output=True,
        text=True
    )
    all_commits = result.stdout.strip().split('\n')
    return all_commits

def get_diff_between_commits(commit1, commit2):
    result = subprocess.run(
        ["git", "diff", commit1, commit2],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def is_revert(commit, all_commits):
    for potential_original_commit in all_commits:
        if commit == potential_original_commit:
            continue
        
        diff_current = get_diff_between_commits(commit, potential_original_commit)
        diff_reverse = get_diff_between_commits(potential_original_commit, commit)
        
        if diff_current == diff_reverse:
            print("é revert")
            return True
    return False

def get_date_six_months_ago():
    six_months_ago = datetime.now() - timedelta(days=6*30)
    return six_months_ago.strftime('%Y-%m-%d')

def is_commit_in_main(commit_hash):
    result = subprocess.run(
        ["git", "branch", "--contains", commit_hash],
        capture_output=True,
        text=True
    )
    branches = result.stdout.strip().split('\n')
    return 'main' in [branch.strip() for branch in branches]

def main():
    oldrev = os.getenv('OLD_COMMIT_HASH')
    newrev = os.getenv('NEW_COMMIT_HASH')

    # Calcular a data de 6 meses atrás
    since_date = get_date_six_months_ago()

    # Obter todos os commits desde a data calculada
    all_commits = get_all_commits_since(since_date)

    # Obter os commits entre as revisões especificadas
    commits = get_commit_diffs(oldrev, newrev)

    # Verificar se algum commit recente é um revert
    for commit in commits:
        if is_revert(commit, all_commits) and is_commit_in_main(commit):
            print(f"Revert detected: {commit}")
            return commit  # Retorna o hash do commit que é um revert

if __name__ == "__main__":
    main()
