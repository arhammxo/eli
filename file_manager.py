import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class FileOperationResult:
    """Represents the result of a file operation"""
    success: bool
    data: Optional[str] = None
    error: Optional[str] = None
    was_created: bool = False

class FileManager:
    """Handles file operations with improved error handling and auto-creation"""
    
    def __init__(self, 
                 logger: Optional[logging.Logger] = None,
                 auto_create: bool = True,
                 default_content: str = ""):
        self.logger = logger or self._setup_default_logger()
        self.auto_create = auto_create
        self.default_content = default_content

    @staticmethod
    def _setup_default_logger() -> logging.Logger:
        logger = logging.getLogger('FileManager')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def ensure_file_exists(self, file_path: Path) -> FileOperationResult:
        try:
            if not file_path.exists():
                if not self.auto_create:
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.default_content)
                
                self.logger.info(f"Created new file: {file_path}")
                return FileOperationResult(success=True, was_created=True)
                
            return FileOperationResult(success=True, was_created=False)
            
        except Exception as e:
            self.logger.error(f"Error ensuring file exists {file_path}: {e}")
            return FileOperationResult(success=False, error=str(e))

    def read_file(self, file_path: str | Path) -> FileOperationResult:
        file_path = Path(file_path)
        
        try:
            ensure_result = self.ensure_file_exists(file_path)
            if not ensure_result.success:
                return ensure_result
            
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                data = file.read()
                
            self.logger.info(
                f"Successfully read file: {file_path}" + 
                (" (newly created)" if ensure_result.was_created else "")
            )
            return FileOperationResult(
                success=True, 
                data=data,
                was_created=ensure_result.was_created
            )
            
        except UnicodeDecodeError as e:
            self.logger.error(f"Unicode decode error for file: {file_path}")
            return FileOperationResult(
                success=False, 
                error=f"Error decoding the file. Please check the file encoding: {e}"
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error reading file {file_path}: {e}")
            return FileOperationResult(success=False, error=str(e))

    def write_file(self, file_path: str | Path, content: str) -> FileOperationResult:
        file_path = Path(file_path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
                
            self.logger.info(f"Successfully wrote to file: {file_path}")
            return FileOperationResult(success=True)
            
        except PermissionError as e:
            self.logger.error(f"Permission denied writing to file: {file_path}")
            return FileOperationResult(
                success=False, 
                error=f"Permission denied. Check file permissions: {e}"
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error writing to file {file_path}: {e}")
            return FileOperationResult(success=False, error=str(e))