from pymongo import MongoClient, errors
from typing import Any, Dict, List, Optional


class MongoManager:
    def __init__(self, uri: str, db_name: str) -> None:
        self.client: MongoClient = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Optional[Any]:
        try:
            result = self.db[collection].insert_one(document)
            print(f"Documento insertado con _id: {result.inserted_id}")
            return result.inserted_id
        except errors.PyMongoError as err:
            print(f"Error al insertar documento: {err}")
            return None

    def find_one(
        self, collection: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            return self.db[collection].find_one(query)
        except errors.PyMongoError as err:
            print(f"Error al buscar documento: {err}")
            return None

    def find_many(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            return list(self.db[collection].find(query))
        except errors.PyMongoError as err:
            print(f"Error al buscar documentos: {err}")
            return []

    def update_one(
        self,
        collection: str,
        query: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False,
    ) -> int:
        try:
            result = self.db[collection].update_one(
                query, {"$set": update}, upsert=upsert
            )
            print(f"Documentos actualizados: {result.modified_count}")
            return result.modified_count
        except errors.PyMongoError as err:
            print(f"Error al actualizar documento: {err}")
            return 0

    def delete_one(self, collection: str, query: Dict[str, Any]) -> int:
        try:
            result = self.db[collection].delete_one(query)
            print(f"Documentos eliminados: {result.deleted_count}")
            return result.deleted_count
        except errors.PyMongoError as err:
            print(f"Error al eliminar documento: {err}")
            return 0

    def close(self) -> None:
        self.client.close()
        print("Conexión a MongoDB cerrada.")
