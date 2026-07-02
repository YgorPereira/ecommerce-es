from src.modules.inventories.entity import Inventory
from src.modules.inventories.models import InventoryModel


class InventoryMapper:

    @staticmethod
    def to_model(entity: Inventory) -> InventoryModel:
        return InventoryModel(
            id=entity.id,
            product_id=entity.product_id,
            quantity=entity.quantity,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(model: InventoryModel) -> Inventory:
        return Inventory(
            id=model.id,
            product_id=model.product_id,
            quantity=model.quantity,
            updated_at=model.updated_at,
        )
