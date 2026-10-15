"""Storage backends."""
import json
import os
from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def save(self, key, value):
        ...

    @abstractmethod
    def load(self, key):
        ...


class StorageFactory:
    @staticmethod
    def create(kind, path):
        if kind == "json":
            return JsonFileStorage(path)
        raise ValueError(kind)


class JsonFileStorage(StorageBackend):
    def __init__(self, path):
        self.path = path

    def _read(self):
        if not os.path.exists(self.path):
            return {}
        with open(self.path) as f:
            return json.load(f)

    def save(self, key, value):
        data = self._read()
        data[key] = value
        with open(self.path, "w") as f:
            json.dump(data, f)

    def load(self, key):
        return self._read().get(key)
