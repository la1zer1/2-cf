import os
import json
import shutil
from datetime import datetime
from dependency_graph import load_config, read_commit, parse_commit_data, get_commits_after_date, get_commit_hash_from_ref, generate_graph, save_graph_as_png  # замените на правильный путь

# Утверждения для упрощения работы с тестами
def setup_test_repo():
    """Создание минимального тестового репозитория с нужной структурой .git."""
    repo_path = 'C:/Users/redmi/Documents/Config/Config--Max/Config--2'  # Заменен путь на корректный

    # Создаем структуру каталогов
    os.makedirs(os.path.join(repo_path, '.git', 'objects', 'f6'), exist_ok=True)

    # Имитация HEAD файла с ссылкой на тестовый коммит
    with open(os.path.join(repo_path, '.git', 'HEAD'), 'w') as f:
        f.write('ref: refs/heads/main\n')

    # Создаем объект коммита в формате Git
    commit_hash = 'f62a81bbf6a5adf672d06c1d9a580f4fb6ed7268'
    commit_data = b"commit hash\nparent abc123\ncommitter John Doe <john@example.com> 1623654400 +0000\n"

    # Сохраняем сжатый объект коммита
    commit_path = os.path.join(repo_path, '.git', 'objects', 'f6', commit_hash[2:])
    with open(commit_path, 'wb') as f:
        f.write(commit_data)

    # Создание тестового конфигурационного файла
    config_data = {
        'repo_path': repo_path,
        'output_image_path': 'test_output_graph.png',
        'commit_date': '2022-01-01'
    }

    # Путь к конфигурационному файлу
    config_path = 'config.json'
    with open(config_path, 'w') as f:
        json.dump(config_data, f)

    print(f"Test repository set up at {repo_path}")
    return repo_path  # Возвращаем путь к репозиторию

# Тест для load_config
def test_load_config():
    setup_test_repo()  # Создаем тестовый репозиторий
    config = load_config('config.json')  # Загружаем конфигурацию по пути config.json
    
    assert isinstance(config, dict), "Config should be a dictionary"
    assert 'repo_path' in config, "'repo_path' key should be in the config"
    assert 'output_image_path' in config, "'output_image_path' key should be in the config"
    assert 'commit_date' in config, "'commit_date' key should be in the config"
    
    print("test_load_config passed.")

# Тест для read_commit
def test_read_commit():
    repo_path = setup_test_repo()  # Создаем тестовый репозиторий
    commit_hash = 'f62a81bbf6a5adf672d06c1d9a580f4fb6ed7268'  # Реальный хеш коммита
    
    try:
        commit_data = read_commit(commit_hash, repo_path)
        assert isinstance(commit_data, dict), "Commit data should be a dictionary"
        assert 'commit_hash' in commit_data, "'commit_hash' should be in commit data"
        assert 'committer_timestamp' in commit_data, "'committer_timestamp' should be in commit data"
        print("test_read_commit passed.")
    except Exception as e:
        print(f"test_read_commit failed: {e}")

# Тест для parse_commit_data
def test_parse_commit_data():
    test_data = b"commit hash\nparent abc123\ncommitter John Doe <john@example.com> 1623654400 +0000\n"
    commit_hash = 'abc123'
    
    commit_data = parse_commit_data(test_data, commit_hash)
    
    assert commit_data['commit_hash'] == commit_hash, f"Expected commit hash {commit_hash}, got {commit_data['commit_hash']}"
    assert 'parent' in commit_data, "'parent' should be in the commit data"
    assert 'committer_timestamp' in commit_data, "'committer_timestamp' should be in the commit data"
    
    print("test_parse_commit_data passed.")

# Тест для get_commits_after_date
def test_get_commits_after_date():
    repo_path = setup_test_repo()  # Создаем тестовый репозиторий
    start_date = datetime(2022, 1, 1)
    
    commits = get_commits_after_date(repo_path, start_date)
    
    assert isinstance(commits, list), "Commits should be a list"
    assert all(isinstance(commit, dict) for commit in commits), "All commits should be dictionaries"
    
    # Проверим, что все коммиты имеют временную метку после указанной даты
    for commit in commits:
        assert commit['committer_timestamp'] >= start_date.timestamp(), "Commit timestamp should be after the start date"
    
    print("test_get_commits_after_date passed.")

# Тест для get_commit_hash_from_ref
def test_get_commit_hash_from_ref():
    repo_path = setup_test_repo()  # Создаем тестовый репозиторий
    branch_ref = 'refs/heads/main'  # Замените на имя тестовой ветки
    
    commit_hash = get_commit_hash_from_ref(branch_ref, repo_path)
    
    assert isinstance(commit_hash, str), "Commit hash should be a string"
    assert len(commit_hash) == 40, "Commit hash should have a length of 40 characters"
    
    print("test_get_commit_hash_from_ref passed.")

# Тест для generate_graph
def test_generate_graph():
    commits = [
        {'commit_hash': 'abc123', 'parent': None, 'committer_timestamp': 1623654400},
        {'commit_hash': 'def456', 'parent': 'abc123', 'committer_timestamp': 1623654600},
    ]
    
    graph = generate_graph(commits)
    
    assert graph is not None, "Graph should be generated"
    assert 'Commit 1' in graph.source, "Graph should contain Commit 1"
    assert 'Commit 2' in graph.source, "Graph should contain Commit 2"
    
    print("test_generate_graph passed.")

# Тест для save_graph_as_png
def test_save_graph_as_png():
    commits = [
        {'commit_hash': 'abc123', 'parent': None, 'committer_timestamp': 1623654400},
        {'commit_hash': 'def456', 'parent': 'abc123', 'committer_timestamp': 1623654600},
    ]
    
    graph = generate_graph(commits)
    output_path = 'test_output_graph.png'
    
    save_graph_as_png(graph, output_path)
    
    assert os.path.exists(output_path), f"Graph image should be saved at {output_path}"
    
    # Очистим файл после теста
    os.remove(output_path)
    
    print("test_save_graph_as_png passed.")

if __name__ == "__main__":
    try:
        test_load_config()
        test_read_commit()
        test_parse_commit_data()
        test_get_commits_after_date()
        test_get_commit_hash_from_ref()
        test_generate_graph()
        test_save_graph_as_png()
    except Exception as e:
        print(f"Test failed: {e}")
