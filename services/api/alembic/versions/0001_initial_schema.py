"""Initial PostgreSQL/PostGIS schema migration.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-29 02:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Enable PostGIS and UUID extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "postgis";')

    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('phone_normalized', sa.String(length=20), nullable=False),
        sa.Column('pin_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('account_state', sa.String(length=50), server_default='ACTIVE', nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_users_phone_normalized', 'users', ['phone_normalized'], unique=True)

    # 2. auth_sessions
    op.create_table(
        'auth_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_refresh_token_hash', 'auth_sessions', ['refresh_token_hash'], unique=True)

    # 3. regions
    op.create_table(
        'regions',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('state_code', sa.String(length=10), nullable=False),
        sa.Column('kind', sa.String(length=50), server_default='STATE', nullable=False),
        sa.Column('parent_id', sa.String(length=50), sa.ForeignKey('regions.id'), nullable=True),
        sa.Column('centroid', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('boundary', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326), nullable=True),
    )

    # 4. collectors
    op.create_table(
        'collectors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('display_alias', sa.String(length=100), nullable=True),
        sa.Column('preferred_language', sa.String(length=10), server_default='hi', nullable=False),
        sa.Column('region_id', sa.String(length=50), sa.ForeignKey('regions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('general_area', sa.String(length=200), nullable=True),
        sa.Column('consent_version', sa.String(length=50), server_default='v1.0', nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_collectors_user_id', 'collectors', ['user_id'], unique=True)
    op.create_index('ix_collectors_region_id', 'collectors', ['region_id'])
    op.create_index('ix_collectors_updated_at', 'collectors', ['id', 'updated_at'])

    # 5. facilities
    op.create_table(
        'facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('facility_name', sa.String(length=200), nullable=False),
        sa.Column('kind', sa.String(length=50), nullable=False),
        sa.Column('address_public', sa.Text(), nullable=False),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('region_id', sa.String(length=50), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('geo_point', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('geocode_accuracy', sa.String(length=50), server_default='UNKNOWN', nullable=True),
        sa.Column('contact_public', sa.String(length=100), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_facilities_region_id', 'facilities', ['region_id'])
    op.create_index('ix_facilities_updated_at', 'facilities', ['id', 'updated_at'])

    # 6. facility_users
    op.create_table(
        'facility_users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('membership_role', sa.String(length=50), server_default='OPERATOR', nullable=False),
        sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # 7. material_categories
    op.create_table(
        'material_categories',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('label_key', sa.String(length=100), nullable=False),
        sa.Column('display_order', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )
    op.create_index('ix_material_categories_code', 'material_categories', ['code'], unique=True)

    # 8. materials
    op.create_table(
        'materials',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('category_id', sa.String(length=50), sa.ForeignKey('material_categories.id'), nullable=False),
        sa.Column('subcategory_code', sa.String(length=50), nullable=False),
        sa.Column('description_key', sa.String(length=100), nullable=False),
        sa.Column('condition_options', sa.JSON(), nullable=True),
        sa.Column('allowed_units', sa.String(length=50), server_default='kg,g', nullable=False),
        sa.Column('default_route', sa.String(length=50), nullable=False),
        sa.Column('route_requires_context', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('safety_guide_ids', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_materials_category_id', 'materials', ['category_id'])
    op.create_index('ix_materials_subcategory_code', 'materials', ['subcategory_code'])

    # 9. material_aliases
    op.create_table(
        'material_aliases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('material_id', sa.String(length=50), sa.ForeignKey('materials.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('local_term', sa.String(length=100), nullable=False),
        sa.Column('normalized_term', sa.String(length=100), nullable=False),
        sa.UniqueConstraint('material_id', 'language', 'normalized_term', name='uq_material_alias_term'),
    )
    op.create_index('ix_material_aliases_material_id', 'material_aliases', ['material_id'])
    op.create_index('ix_material_aliases_normalized_term', 'material_aliases', ['normalized_term'])

    # 10. safety_guides
    op.create_table(
        'safety_guides',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('material_ids', sa.JSON(), nullable=False),
        sa.Column('route', sa.String(length=50), nullable=False),
        sa.Column('text_key', sa.String(length=100), nullable=False),
        sa.Column('icon_asset_ref', sa.String(length=200), nullable=False),
        sa.Column('image_asset_ref', sa.String(length=200), nullable=True),
        sa.Column('audio_keys', sa.JSON(), nullable=True),
        sa.Column('source_ids', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(length=20), server_default='v1.0', nullable=False),
        sa.Column('review_status', sa.String(length=50), server_default='APPROVED', nullable=False),
    )

    # 11. data_sources
    op.create_table(
        'data_sources',
        sa.Column('id', sa.String(length=100), primary_key=True),
        sa.Column('publisher', sa.String(length=200), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('publication_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('source_kind', sa.String(length=50), nullable=False),
        sa.Column('licence', sa.String(length=100), nullable=True),
        sa.Column('licence_url', sa.String(length=500), nullable=True),
        sa.Column('sha256', sa.String(length=64), nullable=True),
        sa.Column('local_snapshot', sa.String(length=255), nullable=True),
        sa.Column('locator', sa.String(length=200), nullable=True),
        sa.Column('review_status', sa.String(length=50), server_default='VERIFIED', nullable=False),
    )

    # 12. source_assertions
    op.create_table(
        'source_assertions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_path', sa.String(length=100), nullable=False),
        sa.Column('value_json', sa.JSON(), nullable=False),
        sa.Column('source_id', sa.String(length=100), sa.ForeignKey('data_sources.id'), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checked_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('supersedes_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_source_assertions_entity_type', 'source_assertions', ['entity_type'])
    op.create_index('ix_source_assertions_entity_id', 'source_assertions', ['entity_id'])
    op.create_index('ix_source_assertions_source_id', 'source_assertions', ['source_id'])

    # 13. facility_authorizations
    op.create_table(
        'facility_authorizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('route', sa.String(length=50), nullable=False),
        sa.Column('authority', sa.String(length=100), nullable=False),
        sa.Column('reference', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='VALID', nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
        sa.Column('source_document_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verification_level', sa.String(length=50), server_default='REGISTRY_MATCH', nullable=False),
        sa.Column('last_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('scope_notes', sa.Text(), nullable=True),
    )
    op.create_index('ix_facility_authorizations_facility_id', 'facility_authorizations', ['facility_id'])

    # 14. facility_materials
    op.create_table(
        'facility_materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.String(length=50), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('route', sa.String(length=50), nullable=False),
        sa.Column('accepted', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('min_weight_g', sa.BigInteger(), nullable=True),
        sa.Column('max_weight_g', sa.BigInteger(), nullable=True),
        sa.Column('evidence_source_id', sa.String(length=100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_facility_materials_facility_id', 'facility_materials', ['facility_id'])
    op.create_index('ix_facility_materials_material_id', 'facility_materials', ['material_id'])

    # 15. facility_operations
    op.create_table(
        'facility_operations',
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('pickup_status', sa.Boolean(), nullable=True),
        sa.Column('service_regions', sa.String(length=200), nullable=True),
        sa.Column('service_geometry', geoalchemy2.types.Geometry(geometry_type='POLYGON', srid=4326), nullable=True),
        sa.Column('accepting_status', sa.String(length=50), server_default='ACCEPTING', nullable=False),
        sa.Column('operational_updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('source_id', sa.String(length=100), nullable=True),
    )

    # 16. facility_rates
    op.create_table(
        'facility_rates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.String(length=50), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('region_id', sa.String(length=50), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('rate_paise_per_unit', sa.BigInteger(), nullable=False),
        sa.Column('unit', sa.String(length=20), server_default='kg', nullable=False),
        sa.Column('price_kind', sa.String(length=20), server_default='QUOTE', nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=False),
        sa.Column('review_status', sa.String(length=50), server_default='PENDING_REVIEW', nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    )
    op.create_index('ix_facility_rates_facility_id', 'facility_rates', ['facility_id'])
    op.create_index('ix_facility_rates_material_id', 'facility_rates', ['material_id'])
    op.create_index('ix_facility_rates_region_id', 'facility_rates', ['region_id'])

    # 17. price_observations
    op.create_table(
        'price_observations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('material_id', sa.String(length=50), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('subcategory_id', sa.String(length=50), nullable=True),
        sa.Column('region_id', sa.String(length=50), sa.ForeignKey('regions.id'), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('rate_paise_per_unit', sa.BigInteger(), nullable=False),
        sa.Column('unit', sa.String(length=20), server_default='kg', nullable=False),
        sa.Column('price_kind', sa.String(length=20), server_default='BUY', nullable=False),
        sa.Column('observed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=False),
        sa.Column('review_status', sa.String(length=50), server_default='PENDING_REVIEW', nullable=False),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('origin_class', sa.String(length=50), server_default='EXTERNAL_PUBLIC', nullable=False),
        sa.Column('source_kind', sa.String(length=50), server_default='PUBLIC_MARKET_QUOTE', nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_price_observations_material_id', 'price_observations', ['material_id'])
    op.create_index('ix_price_observations_region_id', 'price_observations', ['region_id'])
    op.create_index('ix_price_obs_cohort_date', 'price_observations', ['material_id', 'region_id', 'observed_at'])

    # 18. price_summaries
    op.create_table(
        'price_summaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('cohort_key', sa.String(length=100), nullable=False),
        sa.Column('policy_version', sa.String(length=50), server_default='PRICE_V1', nullable=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('source_cutoff_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('q1_rate', sa.BigInteger(), nullable=True),
        sa.Column('median_rate', sa.BigInteger(), nullable=True),
        sa.Column('q3_rate', sa.BigInteger(), nullable=True),
        sa.Column('count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('independent_sources', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('confidence', sa.String(length=50), server_default='INSUFFICIENT_DATA', nullable=False),
        sa.Column('reason_codes', sa.JSON(), nullable=False),
        sa.Column('observation_ids', sa.JSON(), nullable=False),
        sa.Column('input_hash', sa.String(length=64), nullable=False),
    )
    op.create_index('ix_price_summaries_cohort_key', 'price_summaries', ['cohort_key'])

    # 19. lots
    op.create_table(
        'lots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('collector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collectors.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.String(length=50), sa.ForeignKey('materials.id'), nullable=True),
        sa.Column('material_context', sa.String(length=100), nullable=True),
        sa.Column('regulatory_route', sa.String(length=50), nullable=True),
        sa.Column('estimated_weight_g', sa.BigInteger(), nullable=True),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('collection_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='DRAFT', nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('origin_class', sa.String(length=50), server_default='PLATFORM_GENERATED', nullable=False),
        sa.Column('source_kind', sa.String(length=50), server_default='PLATFORM_OBSERVATION', nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint('estimated_weight_g IS NULL OR estimated_weight_g > 0', name='chk_positive_estimated_weight'),
    )
    op.create_index('ix_lots_collector_id', 'lots', ['collector_id'])
    op.create_index('ix_lots_material_id', 'lots', ['material_id'])
    op.create_index('ix_lots_status', 'lots', ['status'])
    op.create_index('ix_lots_collector_updated', 'lots', ['collector_id', 'updated_at'])

    # 20. media_objects
    op.create_table(
        'media_objects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('owner_entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('storage_key', sa.String(length=255), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('byte_size', sa.BigInteger(), nullable=False),
        sa.Column('pixel_width', sa.Integer(), nullable=True),
        sa.Column('pixel_height', sa.Integer(), nullable=True),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('upload_state', sa.String(length=50), server_default='STAGED', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_media_objects_owner_user_id', 'media_objects', ['owner_user_id'])
    op.create_index('ix_media_objects_storage_key', 'media_objects', ['storage_key'], unique=True)
    op.create_index('ix_media_objects_sha256', 'media_objects', ['sha256'])

    # 21. lot_images
    op.create_table(
        'lot_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('media_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('media_objects.id'), nullable=False),
        sa.Column('purpose', sa.String(length=50), server_default='PHOTO', nullable=False),
        sa.Column('order_index', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('source_id', sa.String(length=100), nullable=True),
    )
    op.create_index('ix_lot_images_lot_id', 'lot_images', ['lot_id'])
    op.create_index('ix_lot_images_media_id', 'lot_images', ['media_id'])

    # 22. location_records
    op.create_table(
        'location_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('owner_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('point', geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('coarse_area', sa.String(length=100), nullable=True),
        sa.Column('accuracy_m', sa.Float(), nullable=True),
        sa.Column('source', sa.String(length=50), server_default='GPS', nullable=False),
        sa.Column('captured_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('age_ms', sa.BigInteger(), nullable=True),
        sa.Column('consent_version', sa.String(length=50), nullable=True),
    )
    op.create_index('ix_location_records_owner_entity_id', 'location_records', ['owner_entity_id'])

    # 23. classifications
    op.create_table(
        'classifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model_id', sa.String(length=100), nullable=False),
        sa.Column('model_sha256', sa.String(length=64), nullable=False),
        sa.Column('predicted_class', sa.String(length=100), nullable=True),
        sa.Column('scores', sa.JSON(), nullable=False),
        sa.Column('threshold_version', sa.String(length=50), server_default='v1.0', nullable=False),
        sa.Column('abstained', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('user_selected_material_id', sa.String(length=50), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_classifications_lot_id', 'classifications', ['lot_id'])

    # 24. valuation_snapshots
    op.create_table(
        'valuation_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price_summary_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('price_summaries.id'), nullable=True),
        sa.Column('input_weight_g', sa.BigInteger(), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('low_total_paise', sa.BigInteger(), nullable=True),
        sa.Column('median_total_paise', sa.BigInteger(), nullable=True),
        sa.Column('high_total_paise', sa.BigInteger(), nullable=True),
        sa.Column('policy_version', sa.String(length=50), server_default='PRICE_V1', nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_valuation_snapshots_lot_id', 'valuation_snapshots', ['lot_id'])

    # 25. lot_requests
    op.create_table(
        'lot_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('state', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_lot_requests_lot_id', 'lot_requests', ['lot_id'])
    op.create_index('ix_lot_requests_facility_id', 'lot_requests', ['facility_id'])

    # 26. offers
    op.create_table(
        'offers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lot_requests.id'), nullable=False),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id', ondelete='CASCADE'), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rate_paise_per_kg', sa.BigInteger(), nullable=True),
        sa.Column('fixed_total_paise', sa.BigInteger(), nullable=True),
        sa.Column('price_basis', sa.String(length=50), server_default='RATE_PER_KG', nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('weight_basis_g', sa.BigInteger(), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='OPEN', nullable=False),
        sa.Column('terms_hash', sa.String(length=64), nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_offers_request_id', 'offers', ['request_id'])
    op.create_index('ix_offers_lot_id', 'offers', ['lot_id'])
    op.create_index('ix_offers_facility_id', 'offers', ['facility_id'])

    # 27. transactions
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id'), nullable=False),
        sa.Column('collector_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('collectors.id'), nullable=False),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id'), nullable=False),
        sa.Column('accepted_offer_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('offers.id'), nullable=False),
        sa.Column('estimated_weight_g', sa.BigInteger(), nullable=False),
        sa.Column('agreed_weight_g', sa.BigInteger(), nullable=True),
        sa.Column('quoted_total_paise', sa.BigInteger(), nullable=False),
        sa.Column('agreed_total_paise', sa.BigInteger(), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
        sa.Column('lifecycle', sa.String(length=50), server_default='AGREED', nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('agreed_total_paise IS NULL OR agreed_total_paise >= 0', name='chk_tx_non_negative_agreed_paise'),
    )
    op.create_index('ix_transactions_lot_id', 'transactions', ['lot_id'], unique=True)
    op.create_index('ix_transactions_collector_id', 'transactions', ['collector_id'])
    op.create_index('ix_transactions_facility_id', 'transactions', ['facility_id'])

    # 28. terms_revisions
    op.create_table(
        'terms_revisions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('previous_revision_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('final_material_id', sa.String(length=50), sa.ForeignKey('materials.id'), nullable=False),
        sa.Column('measured_weight_g', sa.BigInteger(), nullable=False),
        sa.Column('final_total_paise', sa.BigInteger(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
        sa.Column('proposed_by', sa.String(length=50), nullable=False),
        sa.Column('proposed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('collector_ack_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recycler_ack_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('terms_hash', sa.String(length=64), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.CheckConstraint('measured_weight_g > 0', name='chk_terms_rev_positive_weight'),
        sa.CheckConstraint('final_total_paise >= 0', name='chk_terms_rev_non_negative_paise'),
    )
    op.create_index('ix_terms_revisions_transaction_id', 'terms_revisions', ['transaction_id'])

    # 29. handovers
    op.create_table(
        'handovers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id'), nullable=False),
        sa.Column('lot_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('lots.id'), nullable=False),
        sa.Column('proposal_payload_json', sa.JSON(), nullable=False),
        sa.Column('proposal_hash', sa.String(length=64), nullable=False),
        sa.Column('schema_version', sa.String(length=20), server_default='v1.0', nullable=False),
        sa.Column('proposed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('proposed_at_client', sa.DateTime(timezone=True), nullable=False),
        sa.Column('received_at_server', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('collection_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('handover_location_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('agreed_terms_revision_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='PENDING_CONFIRMATION', nullable=False),
        sa.Column('public_token_hash', sa.String(length=64), nullable=True),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_handovers_transaction_id', 'handovers', ['transaction_id'])
    op.create_index('ix_handovers_lot_id', 'handovers', ['lot_id'])
    op.create_index('ix_handovers_public_token_hash', 'handovers', ['public_token_hash'])

    # 30. handover_confirmations
    op.create_table(
        'handover_confirmations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('handover_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('handovers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('terms_revision_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recycler_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_handover_confirmations_handover_id', 'handover_confirmations', ['handover_id'], unique=True)

    # 31. payment_entries
    op.create_table(
        'payment_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('amount_paise', sa.BigInteger(), nullable=False),
        sa.Column('method', sa.String(length=50), server_default='CASH', nullable=False),
        sa.Column('private_reference', sa.String(length=100), nullable=True),
        sa.Column('asserted_by', sa.String(length=50), nullable=False),
        sa.Column('asserted_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('state', sa.String(length=50), server_default='ASSERTED', nullable=False),
        sa.Column('counterparty_ack_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ack_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reversal_of', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('is_demo', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('amount_paise > 0', name='chk_payment_positive_amount'),
    )
    op.create_index('ix_payment_entries_transaction_id', 'payment_entries', ['transaction_id'])

    # 32. domain_events
    op.create_table(
        'domain_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('aggregate_type', sa.String(length=50), nullable=False),
        sa.Column('aggregate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence', sa.BigInteger(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=True),
        sa.Column('occurred_at_client', sa.DateTime(timezone=True), nullable=True),
        sa.Column('received_at_server', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('previous_state', sa.String(length=50), nullable=True),
        sa.Column('next_state', sa.String(length=50), nullable=True),
        sa.Column('payload_json', sa.JSON(), nullable=False),
        sa.Column('prev_hash', sa.String(length=64), nullable=False),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.Column('schema_version', sa.String(length=20), server_default='v1.0', nullable=False),
        sa.Column('operation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.UniqueConstraint('aggregate_id', 'sequence', name='uq_domain_event_agg_seq'),
        sa.CheckConstraint('sequence >= 1', name='chk_event_sequence_positive'),
    )
    op.create_index('ix_domain_events_aggregate_type', 'domain_events', ['aggregate_type'])
    op.create_index('ix_domain_events_aggregate_id', 'domain_events', ['aggregate_id'])
    op.create_index('ix_domain_events_operation_id', 'domain_events', ['operation_id'])
    op.create_index('ix_events_agg_type_id', 'domain_events', ['aggregate_type', 'aggregate_id'])

    # 33. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('request_id', sa.String(length=100), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('redacted_change', sa.JSON(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
    )
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_entity_id', 'audit_logs', ['entity_id'])

    # 34. sync_operations
    op.create_table(
        'sync_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('operation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payload_hash', sa.String(length=64), nullable=False),
        sa.Column('state', sa.String(length=50), server_default='COMMITTED', nullable=False),
        sa.Column('response_json', sa.JSON(), nullable=False),
        sa.Column('committed_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_sync_operations_actor_id', 'sync_operations', ['actor_id'])
    op.create_index('ix_sync_operations_operation_id', 'sync_operations', ['operation_id'], unique=True)

    # 35. sync_changes
    op.create_table(
        'sync_changes',
        sa.Column('sequence', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_version', sa.BigInteger(), nullable=False),
        sa.Column('visibility_scope', sa.String(length=100), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_sync_changes_entity_type', 'sync_changes', ['entity_type'])
    op.create_index('ix_sync_changes_entity_id', 'sync_changes', ['entity_id'])
    op.create_index('ix_sync_changes_visibility_scope', 'sync_changes', ['visibility_scope'])

    # 36. quality_flags
    op.create_table(
        'quality_flags',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('policy_version', sa.String(length=50), server_default='v1.0', nullable=False),
        sa.Column('severity', sa.String(length=20), server_default='MEDIUM', nullable=False),
        sa.Column('evidence_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='OPEN', nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_quality_flags_entity_type', 'quality_flags', ['entity_type'])
    op.create_index('ix_quality_flags_entity_id', 'quality_flags', ['entity_id'])
    op.create_index('ix_quality_flags_status', 'quality_flags', ['status'])

    # 37. research_insights
    op.create_table(
        'research_insights',
        sa.Column('id', sa.String(length=50), primary_key=True),
        sa.Column('evidence_type', sa.String(length=50), server_default='SECONDARY', nullable=False),
        sa.Column('source_ids', sa.JSON(), nullable=False),
        sa.Column('paraphrase', sa.Text(), nullable=False),
        sa.Column('design_inference', sa.Text(), nullable=False),
        sa.Column('requirement_ids', sa.JSON(), nullable=False),
        sa.Column('limitations', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # 38. model_versions
    op.create_table(
        'model_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('model_sha256', sa.String(length=64), nullable=False),
        sa.Column('labels_sha256', sa.String(length=64), nullable=False),
        sa.Column('preprocess_version', sa.String(length=50), server_default='v1.0', nullable=False),
        sa.Column('licence_manifest_ref', sa.String(length=255), nullable=False),
        sa.Column('metrics_ref', sa.String(length=255), nullable=False),
        sa.Column('data_manifest_ref', sa.String(length=255), nullable=False),
        sa.Column('threshold', sa.Float(), server_default=sa.text('0.70'), nullable=False),
        sa.Column('supported_classes', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_model_versions_model_sha256', 'model_versions', ['model_sha256'], unique=True)

    # 39. training_images
    op.create_table(
        'training_images',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('path_or_object_key', sa.String(length=255), nullable=False),
        sa.Column('source_id', sa.String(length=100), sa.ForeignKey('data_sources.id'), nullable=False),
        sa.Column('licence_ref', sa.String(length=100), nullable=False),
        sa.Column('sha256', sa.String(length=64), nullable=False),
        sa.Column('object_group_id', sa.String(length=100), nullable=False),
        sa.Column('material_label', sa.String(length=100), nullable=False),
        sa.Column('labeler', sa.String(length=100), nullable=False),
        sa.Column('label_confidence', sa.Float(), server_default=sa.text('1.0'), nullable=False),
        sa.Column('split', sa.String(length=20), server_default='train', nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('weight_g', sa.BigInteger(), nullable=True),
        sa.Column('region_id', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index('ix_training_images_source_id', 'training_images', ['source_id'])
    op.create_index('ix_training_images_sha256', 'training_images', ['sha256'], unique=True)
    op.create_index('ix_training_images_object_group_id', 'training_images', ['object_group_id'])
    op.create_index('ix_training_images_material_label', 'training_images', ['material_label'])

    # 40. economics_scenarios
    op.create_table(
        'economics_scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('assumptions_json', sa.JSON(), nullable=False),
        sa.Column('source_ids', sa.JSON(), nullable=False),
        sa.Column('formula_version', sa.String(length=50), server_default='v1.0', nullable=False),
        sa.Column('is_illustrative', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.BigInteger(), server_default=sa.text('1'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # 41. dataset_versions
    op.create_table(
        'dataset_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('family', sa.String(length=50), nullable=False),
        sa.Column('schema_version', sa.String(length=20), server_default='v1.0', nullable=False),
        sa.Column('version', sa.String(length=50), nullable=False),
        sa.Column('manifest_storage_key', sa.String(length=255), nullable=False),
        sa.Column('manifest_sha256', sa.String(length=64), nullable=False),
        sa.Column('counts_by_origin_demo', sa.JSON(), nullable=False),
        sa.Column('source_ids', sa.JSON(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('validation_status', sa.String(length=50), server_default='VALID', nullable=False),
        sa.Column('data_card_ref', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_dataset_versions_family', 'dataset_versions', ['family'])


def downgrade() -> None:
    # Drop tables in reverse creation order
    op.drop_table('dataset_versions')
    op.drop_table('economics_scenarios')
    op.drop_table('training_images')
    op.drop_table('model_versions')
    op.drop_table('research_insights')
    op.drop_table('quality_flags')
    op.drop_table('sync_changes')
    op.drop_table('sync_operations')
    op.drop_table('audit_logs')
    op.drop_table('domain_events')
    op.drop_table('payment_entries')
    op.drop_table('handover_confirmations')
    op.drop_table('handovers')
    op.drop_table('terms_revisions')
    op.drop_table('transactions')
    op.drop_table('offers')
    op.drop_table('lot_requests')
    op.drop_table('valuation_snapshots')
    op.drop_table('classifications')
    op.drop_table('location_records')
    op.drop_table('lot_images')
    op.drop_table('media_objects')
    op.drop_table('lots')
    op.drop_table('price_summaries')
    op.drop_table('price_observations')
    op.drop_table('facility_rates')
    op.drop_table('facility_operations')
    op.drop_table('facility_materials')
    op.drop_table('facility_authorizations')
    op.drop_table('source_assertions')
    op.drop_table('data_sources')
    op.drop_table('safety_guides')
    op.drop_table('material_aliases')
    op.drop_table('materials')
    op.drop_table('material_categories')
    op.drop_table('facility_users')
    op.drop_table('facilities')
    op.drop_table('collectors')
    op.drop_table('regions')
    op.drop_table('auth_sessions')
    op.drop_table('users')
