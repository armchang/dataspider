from abc import ABC, abstractmethod
from importlib import import_module


class DatabaseAdapter(ABC):
    """Contract implemented by every database backend."""

    def __init__(self, settings):
        self.settings = settings

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def insert_ohlcv(self, item):
        pass

    @abstractmethod
    def insert_ohlcv_batch(self, items):
        pass

    @abstractmethod
    def fetch_recent_ohlcv(self, limit=5):
        pass


def load_database(database_type, settings):
    """Dynamically load scripts.db.backends.<database_type>.Database."""
    normalized_type = database_type.strip().lower().replace("-", "_")
    module_name = f"scripts.db.backends.{normalized_type}"

    try:
        module = import_module(module_name)
    except ModuleNotFoundError as error:
        if error.name != module_name:
            raise
        raise ValueError(
            f"Unsupported database type '{database_type}'. "
            f"Add {module_name}.py with a Database adapter implementation."
        ) from error

    adapter_class = getattr(module, "Database", None)
    if adapter_class is None or not issubclass(adapter_class, DatabaseAdapter):
        raise TypeError(
            f"{module_name} must export a Database class derived from DatabaseAdapter"
        )

    return adapter_class(settings)
