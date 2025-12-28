from typing import TypeVar, Protocol

EntityType = TypeVar("EntityType")
ModelType = TypeVar("ModelType")
SchemaType = TypeVar("SchemaType")


class ModelToEntityMapper(Protocol[ModelType, EntityType]):
    def from_model_to_entity(self, model: ModelType) -> EntityType: ...


class EntityToSchemaMapper(Protocol[EntityType, SchemaType]):
    def from_entity_to_schema(self, entity: EntityType) -> SchemaType: ...