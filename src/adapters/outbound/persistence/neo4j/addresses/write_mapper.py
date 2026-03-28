"""Write-side mappers for Neo4j address persistence."""

from src.adapters.outbound.persistence.neo4j.addresses.write_model import CreateAddressWriteModel
from src.domain.addresses.model.address import Address


class AddressToCreateAddressWriteModelMapper:
    """Maps the pure address domain object to the Neo4j write model."""

    def map(self, address: Address) -> CreateAddressWriteModel:
        """Create the write model required by the address create statement."""
        return CreateAddressWriteModel(
            address_id=address.id.value,
            house_number=address.house_number,
            latitude=None if address.geo_location is None else address.geo_location.latitude,
            longitude=None if address.geo_location is None else address.geo_location.longitude,
        )
