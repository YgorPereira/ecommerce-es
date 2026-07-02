import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import CouponNotFoundException
from src.modules.coupons.schemas import CreateCouponSchema, UpdateCouponSchema
from src.modules.coupons.services import CouponService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def coupon_service(mock_repository):
    return CouponService(repository=mock_repository)


@pytest.fixture
def coupon():
    return Coupon(
        discount_percentage=10.0,
        discount_amount=5.0,
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        usage_limit=100,
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(coupon):
    return CreateCouponSchema(
        discount_percentage=coupon.discount_percentage,
        discount_amount=coupon.discount_amount,
        expires_at=coupon.expires_at,
        usage_limit=coupon.usage_limit,
    )


@pytest.fixture
def update_schema(coupon):
    return UpdateCouponSchema(
        id=coupon.id,
        discount_percentage=20.0,
        discount_amount=10.0,
        expires_at=coupon.expires_at,
        usage_limit=50,
    )


@pytest.mark.unit()
async def test_create_coupon(coupon_service, mock_repository, create_schema, coupon):
    mock_repository.create.return_value = coupon

    created = await coupon_service.create_coupon(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Coupon)
    assert created.discount_percentage == coupon.discount_percentage


@pytest.mark.unit()
async def test_get_all_coupons(coupon_service, mock_repository, coupon):
    mock_repository.get_all.return_value = [coupon, coupon]

    coupons = await coupon_service.get_all_coupons()

    mock_repository.get_all.assert_called_once()
    assert isinstance(coupons, list)
    assert len(coupons) == 2


@pytest.mark.unit()
async def test_get_all_coupons_empty(coupon_service, mock_repository):
    mock_repository.get_all.return_value = []

    coupons = await coupon_service.get_all_coupons()

    mock_repository.get_all.assert_called_once()
    assert coupons == []


@pytest.mark.unit()
async def test_get_coupon_by_id(coupon_service, mock_repository, coupon):
    mock_repository.get_by_id.return_value = coupon

    found = await coupon_service.get_coupon_by_id(coupon.id)

    mock_repository.get_by_id.assert_called_once_with(coupon.id)
    assert isinstance(found, Coupon)
    assert found.id == coupon.id


@pytest.mark.unit()
async def test_get_coupon_by_id_not_found(coupon_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(CouponNotFoundException):
        await coupon_service.get_coupon_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_update_coupon(coupon_service, mock_repository, coupon, update_schema):
    updated = Coupon(
        discount_percentage=update_schema.discount_percentage,
        discount_amount=update_schema.discount_amount,
        expires_at=update_schema.expires_at,
        usage_limit=update_schema.usage_limit,
        id=coupon.id,
    )
    mock_repository.get_by_id.return_value = coupon
    mock_repository.update_by_id.return_value = updated

    result = await coupon_service.update_coupon(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert isinstance(result, Coupon)
    assert result.discount_percentage == update_schema.discount_percentage


@pytest.mark.unit()
async def test_update_coupon_not_found(coupon_service, mock_repository, update_schema):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CouponNotFoundException):
        await coupon_service.update_coupon(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_coupon_by_id(coupon_service, mock_repository, coupon):
    mock_repository.get_by_id.return_value = coupon
    mock_repository.delete_by_id.return_value = True

    is_deleted = await coupon_service.delete_coupon_by_id(coupon.id)

    mock_repository.get_by_id.assert_called_once_with(coupon.id)
    mock_repository.delete_by_id.assert_called_once_with(coupon.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_coupon_by_id_not_found(coupon_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CouponNotFoundException):
        await coupon_service.delete_coupon_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
