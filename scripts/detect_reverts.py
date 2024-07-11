import subprocess
from datetime import datetime, timedelta
import os

def get_commit_diffs(oldrev, newrev):
    result = subprocess.run(
        ["git", "rev-list", f"{oldrev}..{newrev}"],
        capture_output=True,
        text=True
    )
    commits = result.stdout.strip().split('\n')
    return commits

def get_main_or_master_branch():
    branches = subprocess.run(
        ["git", "branch", "-r", "--list", "origin/main", "origin/master"],
        capture_output=True,
        text=True
    )
    branches = branches.stdout.strip().split('\n')
    if "origin/main" in branches:
        return "main"
    elif "origin/master" in branches:
        return "master"
    else:
        raise ValueError("Neither 'main' nor 'master' branch found in the repository")

def get_merges_in_branch_since(branch, since_date):
    result = subprocess.run(
        ["git", "rev-list", branch, "--merges", f"--since={since_date}", "--reverse"],
        capture_output=True,
        text=True
    )
    merges = result.stdout.strip().split('\n')
    return merges

def get_diff_between_commits(commit1, commit2):
    result = subprocess.run(
        ["git", "diff", commit1, commit2],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def is_revert(commit, merges):
    for potential_original_commit in merges:
        if commit == potential_original_commit:
            continue
        
        diff_current = get_diff_between_commits(commit, potential_original_commit)
        diff_reverse = get_diff_between_commits(potential_original_commit, commit)
        
        if diff_current == diff_reverse:
            return True
    return False

def get_date_six_months_ago():
    six_months_ago = datetime.now() - timedelta(days=6*30)
    return six_months_ago.strftime('%Y-%m-%d')

def main():
    oldrev = os.getenv('OLD_COMMIT_HASH')
    newrev = os.getenv('NEW_COMMIT_HASH')

    # Calcular a data de 6 meses atrás
    since_date = get_date_six_months_ago()

    # Determinar a branch principal (main ou master)
    branch = get_main_or_master_branch()

    # Obter todos os commits de merge na branch principal desde a data calculada, em ordem cronológica reversa (mais recentes primeiro)
    merges = get_merges_in_branch_since(branch, since_date)

    # Obter os commits entre as revisões especificadas
    commits = get_commit_diffs(oldrev, newrev)

    # Verificar se algum commit recente é um revert
    for commit in commits:
        if is_revert(commit, merges):
            print(commit)
            return commit  # Retorna o hash do commit que é um revert

if __name__ == "__main__":
    main()
