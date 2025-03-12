import os
from datetime import datetime

from elasticsearch import AsyncElasticsearch

from config.settings import get_settings
from file_processors.archive_processor import ArchiveProcessor
from file_processors.audio_processor import AudioProcessor
from file_processors.code_processor import CodeProcessor
from file_processors.excel_processor import ExcelProcessor
from file_processors.image_processor import ImageProcessor
from file_processors.main_file import SearchContext
from file_processors.pdf_processor import PDFProcessor
from file_processors.presentation_processor import PresentationProcessor
from file_processors.text_processor import TextProcessor
from file_processors.word_processor import WordProcessor


async def index_file(file_path: str):
    """Фоновий процес: читає файл і додає його в Elasticsearch"""

    # Підключення до Elasticsearch
    es = AsyncElasticsearch(
        hosts=[get_settings().elastic_host],
        basic_auth=(get_settings().elastic_user, get_settings().elastic_password)
    )
    context = SearchContext()

    # Register file processors
    context.register_processor("mp3", AudioProcessor)
    # context.register_processor("mp4", VideoProcessor)
    context.register_processor("py", CodeProcessor)
    context.register_processor("pdf", PDFProcessor)
    context.register_processor("xlsx", ExcelProcessor)
    context.register_processor("pptx", PresentationProcessor)

    context.register_processor("txt", TextProcessor)
    context.register_processor("docx", WordProcessor)
    context.register_processor("doc", WordProcessor)

    context.register_processor("jpg", ImageProcessor)
    context.register_processor("png", ImageProcessor)
    context.register_processor("jpg", ImageProcessor)
    context.register_processor("jpeg", ImageProcessor)

    context.register_processor("zip", lambda path: ArchiveProcessor(path, context.processors))
    content = context.read_file(file_path)

    if not content:
        print(f"[WARN] Немає обробника для {file_path}")
        await es.close()  # Закрити з'єднання
        return

    ext = file_path.split('.')[-1].lower()
    try:
        doc = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": ext,
            "content": content,  # Весь текст файлу
            "indexed_at": datetime.utcnow(),
        }

        await es.index(index="files_index", document=doc)
        print(f"[SUCCESS] Файл {file_path} проіндексований")

    except Exception as e:
        print(f"[ERROR] Помилка індексації {file_path}: {str(e)}")
    finally:
        await es.close()  # Закрити з'єднання


async def delete_file_index(file_path: str):
    """Фоновий процес: видалення індексу файлу з Elasticsearch"""
    es = AsyncElasticsearch(
        hosts=[get_settings().elastic_host],
        basic_auth=(get_settings().elastic_user, get_settings().elastic_password)
    )

    try:
        search_result = await es.search(index="files_index", body={
            "query": {
                "match": {
                    "file_path": file_path
                }
            }
        })

        if search_result['hits']['total']['value'] > 0:
            # Якщо знайдено відповідний документ, видаляємо його
            doc_id = search_result['hits']['hits'][0]['_id']
            await es.delete(index="files_index", id=doc_id)
            print(f"[SUCCESS] Видалено індекс для файлу {file_path}")
        else:
            print(f"[WARN] Не знайдено індексу для файлу {file_path}")
    except Exception as e:
        print(f"[ERROR] Помилка при видаленні індексу файлу {file_path}: {e}")
    finally:
        await es.close()  # Закрити з'єднання
