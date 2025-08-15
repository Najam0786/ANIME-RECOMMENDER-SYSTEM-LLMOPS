import time
from pathlib import Path
from typing import Any  # Add this import at the top
from src.data_loader import AnimeDataLoader
from src.vector_store import VectorStoreBuilder
from utils.logger import get_logger
from utils.custom_exception import CustomException, ConfigError
from config.config import Config

logger = get_logger(__name__)

class PipelineBuilder:
    def __init__(
        self,
        raw_data_path: str = "data/anime_with_synopsis.csv",
        processed_data_path: str = "data/anime_processed.csv",
        persist_dir: str = "chroma_db",
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        max_retries: int = 2
    ):
        if not Config.validate():
            raise ConfigError("Invalid API configuration")

        self.raw_data_path = raw_data_path
        self.processed_data_path = processed_data_path
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_retries = max_retries
        self._setup_workspace()

    def _setup_workspace(self):
        """Ensure directories exist"""
        Path("data").mkdir(exist_ok=True)
        Path(self.persist_dir).mkdir(exist_ok=True)

    def run_pipeline(self) -> None:
        """Execute complete pipeline with retry logic"""
        try:
            # Process data
            processed_path = self._process_data()

            # Build vector store
            self._build_vector_store(processed_path)

            logger.info("✅ Pipeline completed successfully")
        except Exception as e:
            logger.error("❌ Pipeline failed - cleaning up...")
            self._cleanup()
            raise CustomException("Pipeline execution failed", e)

    def _process_data(self) -> str:
        """Process raw data with retries"""
        return self._run_with_retry(
            operation=lambda: AnimeDataLoader(
                self.raw_data_path,
                self.processed_data_path
            ).load_and_process(),
            operation_name="data processing"
        )

    def _build_vector_store(self, processed_path: str) -> None:
        """Build vector store with retries"""
        self._run_with_retry(
            operation=lambda: VectorStoreBuilder(
                csv_path=processed_path,
                persist_dir=self.persist_dir,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            ).build_and_save_vectorstore(),
            operation_name="vector store creation"
        )

    def _run_with_retry(self, operation: callable, operation_name: str) -> Any:
        """Execute operation with retry logic"""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.warning(f"Retrying {operation_name} (attempt {attempt + 1})...")
                    time.sleep(wait)
        raise last_exception

    def _cleanup(self):
        """Clean up partial outputs"""
        try:
            if Path(self.processed_data_path).exists():
                Path(self.processed_data_path).unlink()
            if Path(self.persist_dir).exists():
                import shutil
                shutil.rmtree(self.persist_dir)
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

def main():
    try:
        logger.info("🚀 Starting pipeline build")
        PipelineBuilder().run_pipeline()
    except ConfigError as e:
        logger.error(f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()