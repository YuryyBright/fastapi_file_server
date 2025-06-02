import os
from pathlib import Path
from datetime import datetime
from pprint import pprint
from typing import List
from fastapi import HTTPException
from elasticsearch import AsyncElasticsearch
from app.api.utils.do_file import bucket_path
from app.config.settings import get_settings
from app.file_processors.main_file import SearchContext
from app.file_processors.archive_processor import ArchiveProcessor
from app.file_processors.audio_processor import AudioProcessor
from app.file_processors.code_processor import CodeProcessor
from app.file_processors.excel_processor import ExcelProcessor
from app.file_processors.image_processor import ImageProcessor
from app.file_processors.pdf_processor import PDFProcessor
from app.file_processors.presentation_processor import PresentationProcessor
from app.file_processors.text_processor import TextProcessor
from app.file_processors.word_processor import WordProcessor


class ElasticsearchService:
    """
    Service class for interacting with Elasticsearch, managing file indexing,
    and performing searches across various file types.

    This service handles indexing files, removing indexed files, and
    managing file processors for different file types.
    """

    def __init__(self):
        """
        Initializes the Elasticsearch service and registers file processors.
        """
        self.es = AsyncElasticsearch(
            hosts=[get_settings().elastic_host],
            basic_auth=(get_settings().elastic_user, get_settings().elastic_password),
            request_timeout=30,  # Default is 10
            max_retries=3,
            retry_on_timeout=True
        )

        self.context = SearchContext()
        self._register_processors()

    def _register_processors(self):
        """
        Registers file processors for various file types, allowing the
        system to handle different file formats like audio, code, PDF, images, etc.
        """
        self.context.register_processor("mp3", AudioProcessor)
        self.context.register_processor("py", CodeProcessor)
        self.context.register_processor("pdf", PDFProcessor)
        self.context.register_processor("xlsx", ExcelProcessor)
        self.context.register_processor("pptx", PresentationProcessor)
        self.context.register_processor("txt", TextProcessor)
        self.context.register_processor("docx", WordProcessor)
        self.context.register_processor("doc", WordProcessor)
        self.context.register_processor("jpg", ImageProcessor)
        self.context.register_processor("png", ImageProcessor)
        self.context.register_processor("jpeg", ImageProcessor)
        self.context.register_processor("zip", lambda path: ArchiveProcessor(path, self.context.processors))
        self.context.register_processor("7z", lambda path: ArchiveProcessor(path, self.context.processors))

    async def index_file(self, file_path: str):
        """
        Indexes a single file into Elasticsearch after processing its content.

        Args:
            file_path (str): The file path to be indexed.

        Raises:
            HTTPException: If there's an error while indexing the file.
        """
        content = self.context.read_file(file_path)
        if content == '':
            content = 'empty'
        if not content:
            print(f"[WARN] No processor found for {file_path}")
            return

        ext = file_path.split('.')[-1].lower()
        doc = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": ext,
            "content": content,
            "indexed_at": datetime.utcnow(),
        }
        try:
            await self.es.index(index="files_index", document=doc)
            print(f"[SUCCESS] File {file_path} indexed")
        except Exception as e:
            print(f"[ERROR] Error indexing file {file_path}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error indexing file {file_path}: {str(e)}")
        finally:
            await self.close()

    async def index_all_unindexed_files(self):
        """
        Indexes all unindexed files in the directory specified by `bucket_path`.

        The method first identifies all the physical files in the directory,
        then checks Elasticsearch for already indexed files, and indexes those
        that haven't been indexed yet.

        Raises:
            HTTPException: If there's an error retrieving or indexing the files.
        """
        try:
            # Fetch all physical files from the bucket path
            directory = Path(bucket_path)
            physical_files = {str(file) for file in directory.rglob('*') if file.is_file()}

            # Fetch already indexed files from Elasticsearch
            es_query = {"query": {"match_all": {}}}
            es_response = await self.es.search(index="files_index", body=es_query)

            indexed_files = {hit["_source"].get("file_path", "") for hit in es_response["hits"]["hits"]}
            # Identify unindexed files
            unindexed_files = list(physical_files - indexed_files)

            if not unindexed_files:
                print("[INFO] No unindexed files found.")
                return

            print(f"[INFO] Found {len(unindexed_files)} unindexed files. Starting indexing process...")

            # Index all unindexed files
            for file in unindexed_files:
                print(f"[INFO] Indexing file {file}")
                await self.index_file(file)

        except Exception as e:
            print(f"[ERROR] Error during indexing unindexed files: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error indexing unindexed files: {str(e)}")
        finally:
            await self.close()

    async def delete_file_index(self, file_path: str):
        """
        Deletes the index of a file from Elasticsearch.

        Args:
            file_path (str): The path of the file to delete from the index.
        """
        try:
            search_result = await self.es.search(index="files_index", body={
                "query": {"match": {"file_path": file_path}}
            })
            if search_result['hits']['total']['value'] > 0:
                doc_id = search_result['hits']['hits'][0]['_id']
                await self.es.delete(index="files_index", id=doc_id)
                print(f"[SUCCESS] Index for file {file_path} deleted")
            else:
                print(f"[WARN] No index found for file {file_path}")
        except Exception as e:
            print(f"[ERROR] Error deleting index for file {file_path}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting index for file {file_path}: {str(e)}")
        finally:
            await self.close()
    async def get_unindexed_files(self) -> List[str]:
        """Отримати список файлів, які ще не проіндексовані в Elasticsearch"""
        try:

            directory = Path(bucket_path)
            physical_files = {file.name for file in directory.rglob('*') if file.is_file()}

            # Отримати всі індексовані файли
            es_query = {"query": {"match_all": {}}}
            es_response = await self.es.search(index="files_index", body=es_query)
            indexed_files = {hit["_source"].get("file_name", "") for hit in es_response["hits"]["hits"]}
            # Визначити непроіндексовані файли
            unindexed_files = list(physical_files - indexed_files)
            return unindexed_files

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Помилка отримання даних: {str(e)}")
        finally:
            await self.close()
    async def close(self):
        """
        Closes the connection to Elasticsearch.
        """
        await self.es.close()
