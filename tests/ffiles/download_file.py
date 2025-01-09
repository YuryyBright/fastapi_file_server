import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
from main import app  # імпортуйте свій FastAPI додаток

client = TestClient(app)

@pytest.fixture
def setup_filesystem():
    """Створення тимчасових файлів для тестування"""
    test_dir = Path("./test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "test_file.txt"
    with open(test_file, "w") as f:
        f.write("Test content")
    yield test_file
    # Очистка після тестів
    test_file.unlink()
    test_dir.rmdir()

def test_download_file(setup_filesystem):
    """Тест для завантаження файлу"""
    url = f"/download/{setup_filesystem.name}"
    response = client.get(url)
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == f"attachment; filename={setup_filesystem.name}"
    assert response.content == b"Test content"

def test_download_file_not_found():
    """Тест для випадку, коли файл не знайдений"""
    response = client.get("/download/non_existent_file.txt")
    assert response.status_code == 404