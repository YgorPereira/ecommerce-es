from src.modules.addresses.entity import Address
from src.modules.addresses.models import AddressModel
from src.modules.addresses.schemas import CreateAddressSchema


class AddressMapper:

    @staticmethod
    def to_model(entity: Address) -> AddressModel:
        return AddressModel(
            id=entity.id,
            user_id=entity.user_id,
            address_line=entity.address_line,
            city=entity.city,
            state=entity.state,
            number=entity.number,
            district=entity.district,
            complement=entity.complement,
        )

    @staticmethod
    def to_entity(model: AddressModel) -> Address:
        return Address(
            id=model.id,
            user_id=model.user_id,
            address_line=model.address_line,
            city=model.city,
            state=model.state,
            number=model.number,
            district=model.district,
            complement=model.complement,
        )

    @staticmethod
    def from_create_schema(schema: CreateAddressSchema) -> Address:
        return Address(
            user_id=schema.user_id,
            address_line=schema.address_line,
            city=schema.city,
            state=schema.state,
            number=schema.number,
            district=schema.district,
            complement=schema.complement,
        )
