import subprocess
from datetime import datetime, timedelta
import os

# Obtém o commit mais recente
def get_most_recent_commit():
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Obtém a lista de todos os commits desde uma data especificada
def get_all_commits_since(since_date):
    result = subprocess.run(
        ["git", "rev-list", "--all", f"--since={since_date}"],
        capture_output=True,
        text=True
    )
    all_commits = result.stdout.strip().split('\n')
    return all_commits

# Obtém a diferença (diff) entre dois commits especificados
def get_diff_between_commits(commit1, commit2):
    result = subprocess.run(
        ["git", "diff", commit1, commit2],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Verifica se um commit é um revert de um commit anterior
def is_revert(commit, all_commits):
    for potential_original_commit in all_commits:
        if commit == potential_original_commit:
            continue
        
        # Obtém os diffs entre o commit atual e um commit anterior
        diff_current = get_diff_between_commits(commit, potential_original_commit)
        diff_reverse = get_diff_between_commits(potential_original_commit, commit)
        
        # Se os diffs forem iguais em ambos os sentidos, é um revert
        if diff_current == diff_reverse:
            return True
    return False

# Calcula a data de seis meses atrás
def get_date_six_months_ago():
    six_months_ago = datetime.now() - timedelta(days=6*30)
    return six_months_ago.strftime('%Y-%m-%d')

# Verifica se um commit está na branch `main`
def is_commit_in_main(commit_hash):
    result = subprocess.run(
        ["git", "branch", "--contains", commit_hash],
        capture_output=True,
        text=True
    )
    branches = result.stdout.strip().split('\n')
    return 'main' in [branch.strip() for branch in branches]

# Função principal que coordena a execução das outras funções
def main():
    # Obtém o commit mais recente
    recent_commit = get_most_recent_commit()

    # Calcular a data de 6 meses atrás
    since_date = get_date_six_months_ago()

    # Obter todos os commits desde a data calculada
    all_commits = get_all_commits_since(since_date)

    # Verificar se o commit recente é um revert
    if is_revert(recent_commit, all_commits):
        print(f"Revert commit detected: {recent_commit}")
        return recent_commit  # Retorna o hash do commit que é um revert

if __name__ == "__main__":
    main()
