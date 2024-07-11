import subprocess
from datetime import datetime, timedelta
import os

def get_commit_diff(commit):
    result = subprocess.run(
        ["git", "show", commit, "--pretty=format:", "--name-only"],
        capture_output=True,
        text=True
    )
    files_changed = result.stdout.strip().split('\n')
    return files_changed

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
        ["git", "rev-list", branch, "--merges", f"--since={since_date}"],
        capture_output=True,
        text=True
    )
    merges = result.stdout.strip().split('\n')
    return merges

def run_git_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar comando {' '.join(command)}: {result.stderr}")
    return result

def get_second_parent_commit(commit):
    if not commit:
        print("")
        return ""
    result = run_git_command(["git", "rev-parse", f"{commit}^2"])
    if result.returncode != 0:
        print(f"Erro ao obter segundo pai do commit {commit}: {result.stderr}")
    second_parent_commit = result.stdout.strip()
    print(f"Segundo pai do commit {commit}: {second_parent_commit}")
    return second_parent_commit


def get_diff_between_commits(commit1, commit2):
    result = subprocess.run(
        ["git", "diff", commit1, commit2],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def extract_changes(diff_text):
    additions = []
    deletions = []
    for line in diff_text.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            additions.append(line[1:].strip())
        elif line.startswith('-') and not line.startswith('---'):
            deletions.append(line[1:].strip())
    return additions, deletions

def is_revert(commit, merges):
    commit_files = get_commit_diff(commit)
    for m in merges:
        potential_original_commit = get_second_parent_commit(m)
        if commit == potential_original_commit:
            continue
        
        original_files = get_commit_diff(potential_original_commit)
        
        if set(commit_files) == set(original_files):
            diff_current = get_diff_between_commits(commit, potential_original_commit)
            diff_reverse = get_diff_between_commits(potential_original_commit, commit)

            add1, del1 = extract_changes(diff_current)
            add2, del2 = extract_changes(diff_reverse)
        
            print(f"Diff do commit {commit} para o commit {potential_original_commit}: {diff_current}")
            print(f"Diff do commit {potential_original_commit} para o commit {commit}: {diff_reverse}")
            
            if sorted(add1) == sorted(del2) and sorted(del1) == sorted(add2):
                print(f"O commit {commit} é um revert do commit {potential_original_commit}")
                return True
            else:
                print(f"O commit {commit} não é um revert do commit {potential_original_commit}")
 
            return
    return False

def get_date_six_months_ago():
    six_months_ago = datetime.now() - timedelta(days=6*30)
    return six_months_ago.strftime('%Y-%m-%d')

def main():
  #  newrev = os.getenv('NEW_COMMIT_HASH')
    newrev = "0fbc0a85c4ed4d218fe3789a72fcae8e5988c552"

    # Calcular a data de 6 meses atrás
    since_date = get_date_six_months_ago()

    # Determinar a branch principal (main ou master)
    branch = get_main_or_master_branch()

    # Obter todos os commits de merge na branch principal desde a data calculada, em ordem cronológica reversa (mais recentes primeiro)
    merges = get_merges_in_branch_since(branch, since_date)

    # # Verificar se o commit recente é um revert
    # if is_revert(newrev, merges):
    #     print(newrev)
    #     print("O commit é um revert")
    #     return newrev  # Retorna o hash do commit que é um revert
    # else:
    #     print(newrev)
    #     print("O commit não é um revert")
    #     return "6c5f2ae650dac47262714c5850ea52591d92e4a1"

    print(merges)
    return merges

if __name__ == "__main__":
    main()


def is_revert(commit, merges):
    commit_files = get_commit_diff(commit)
    for m in merges:
        potential_original_commit = get_second_parent_commit(m)
        if commit == potential_original_commit:
            continue
        
        original_files = get_commit_diff(potential_original_commit)
        
        if set(commit_files) == set(original_files):
            diff_current = get_diff_between_commits(commit, potential_original_commit)
            diff_reverse = get_diff_between_commits(potential_original_commit, commit)

            add1, del1 = extract_changes(diff_current)
            add2, del2 = extract_changes(diff_reverse)
        
            print(f"Diff do commit {commit} para o commit {potential_original_commit}: {diff_current}")
            print(f"Diff do commit {potential_original_commit} para o commit {commit}: {diff_reverse}")
            
           
    return False