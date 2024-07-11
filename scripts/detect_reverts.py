import subprocess
from datetime import datetime, timedelta
import os


def run_git_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erro ao executar comando {' '.join(command)}: {result.stderr}")
    return result

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

def get_second_parent_commit(commit):
    print(f"Obtendo segundo pai para o commit {commit}")
    result = run_git_command(["git", "rev-parse", f"{commit}^2"])
    second_parent_commit = result.stdout.strip()
    print(f"Segundo pai do commit {commit}: {second_parent_commit}")
    return second_parent_commit


def parse_diff(diff):
    added_lines = set()
    removed_lines = set()
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            added_lines.add(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removed_lines.add(line[1:])
    return added_lines, removed_lines

def is_revert(commit, merges):
    commit_files = get_commit_diff(commit)
    for m in merges:
        potential_original_commit = get_second_parent_commit(m)
        if commit == potential_original_commit:
            continue
        
        original_files = get_commit_diff(potential_original_commit)
        print(f"Comparando commit {commit} com commit {potential_original_commit}")
        print(f"Arquivos alterados no commit {commit}: {commit_files}")
        print(f"Arquivos alterados no commit {potential_original_commit}: {original_files}")
        
        if set(commit_files) == set(original_files):
            print("Entra aqui")
            diff_current = get_diff_between_commits(commit, potential_original_commit)
            diff_reverse = get_diff_between_commits(potential_original_commit, commit)
            print(f"Diff do commit {commit} para o commit {potential_original_commit}: {diff_current}")
            print(f"Diff do commit {potential_original_commit} para o commit {commit}: {diff_reverse}")

            added_current, removed_current = parse_diff(diff_current)
            added_reverse, removed_reverse = parse_diff(diff_reverse)

            # Verificar se as linhas adicionadas/removidas são inversas entre os diffs
            if added_current == removed_reverse and removed_current == added_reverse:
                print(f"O commit {commit} é um revert do commit {potential_original_commit}")
                return True
    return False

def get_date_six_months_ago():
    six_months_ago = datetime.now() - timedelta(days=6*30)
    return six_months_ago.strftime('%Y-%m-%d')

def main():
    newrev = os.getenv('NEW_COMMIT_HASH')

    # Calcular a data de 6 meses atrás
    since_date = get_date_six_months_ago()

    # Determinar a branch principal (main ou master)
    branch = get_main_or_master_branch()

    # Obter todos os commits de merge na branch principal desde a data calculada, em ordem cronológica reversa (mais recentes primeiro)
    merges = get_merges_in_branch_since(branch, since_date)

    # Verificar se o commit recente é um revert
    if is_revert(newrev, merges):
        print(newrev)
        return newrev  # Retorna o hash do commit que é um revert

if __name__ == "__main__":
    main()
