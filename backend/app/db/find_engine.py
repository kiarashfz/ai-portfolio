from typing import Optional, Tuple, Type
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, or_
from sqlalchemy.orm.relationships import RelationshipProperty
from sqlalchemy.orm import joinedload, selectinload

from db.models import *


class FindEngine:
    """
    Dynamic find engine that can work with any SQLAlchemy model.
    Based on BaseStageService's find method logic.
    """

    def get_model_class(self, model_name: str) -> Type:
        if model_name not in self.model_registry:
            raise ValueError(f"Model '{model_name}' is not registered")
        return self.model_registry[model_name]

    def _resolve_field_path(self, model_class: Type, field_path: str):
        """
        Resolve a dot-separated field path to the appropriate column and joins.
        Handles JSON field lookups and relationship traversal.
        Returns (column_to_filter, relation_attrs_to_join)
        """
        parts = field_path.split('.')

        if len(parts) == 1:
            # Simple field case
            if not hasattr(model_class, parts[0]):
                raise ValueError(f"'{parts[0]}' field is not valid for {model_class.__name__}")
            return getattr(model_class, parts[0]), None

        # Two-part field path: could be JSON field lookup or relationship
        root_field = parts[0]
        json_key_or_target = parts[1]

        if not hasattr(model_class, root_field):
            raise ValueError(f"'{root_field}' field is not valid for {model_class.__name__}")

        root_attr = getattr(model_class, root_field)

        # Check if it's a relationship
        if hasattr(root_attr, 'property') and isinstance(root_attr.property, RelationshipProperty):
            # This is a relationship case
            related_model = root_attr.property.entity.class_

            # Check if target field exists on related model
            if not hasattr(related_model, json_key_or_target):
                raise ValueError(f"'{json_key_or_target}' field is not valid for {related_model.__name__}")

            target_column = getattr(related_model, json_key_or_target)
            return target_column, root_attr

        else:
            # This is a JSON field lookup case
            # Use SQLAlchemy's JSON field access with .astext for text comparison
            json_column = root_attr[json_key_or_target].astext
            return json_column, None

    def _create_filter_clause(self, col, match_mode: str, value: Any):
        """Create a filter clause based on match mode and value. Supports both single values and arrays."""

        # Handle custom match mode first
        if match_mode == "custom":
            if not isinstance(value, list):
                raise ValueError("Custom filters must pass a list of SQLAlchemy expressions")
            return value

        # Handle array values for all match modes
        if isinstance(value, list):
            # Handle empty array case - return a condition that matches everything
            if len(value) == 0:
                return [col.is_(None) | col.isnot(None)]  # Always true condition

            # Special handling for 'in' and 'not_in' match modes with arrays
            if match_mode == "in":
                return [col.in_(value)]
            elif match_mode == "not_in":
                return [~col.in_(value)]
            elif match_mode == "between":
                if len(value) == 2:
                    return [col.between(value[0], value[1])]
                else:
                    raise ValueError("Between match mode with array requires exactly 2 values")

            # For other match modes, apply the condition to each value and combine with OR
            clauses = []
            for single_value in value:
                clause = self._create_single_value_clause(col, match_mode, single_value)
                if clause is not None:
                    clauses.append(clause)

            # Combine multiple clauses with OR
            return [or_(*clauses)] if clauses else [col.is_(None) | col.isnot(None)]

        else:
            # Handle single values
            clause = self._create_single_value_clause(col, match_mode, value)
            if clause is None:
                raise ValueError(f"Type mismatch for match mode '{match_mode}' and value type")
            return [clause]

    def _create_single_value_clause(self, col, match_mode: str, value: Any):
        """Create a filter clause for a single value based on match mode."""
        filter_handlers = {
            "starts_with": lambda: col.ilike(f"{value}%") if isinstance(value, str) else None,
            "contains": lambda: col.ilike(f"%{value}%") if isinstance(value, str) else None,
            "not_contains": lambda: ~col.ilike(f"%{value}%") if isinstance(value, str) else None,
            "ends_with": lambda: col.ilike(f"%{value}") if isinstance(value, str) else None,
            "equals": lambda: col == value,
            "not_equals": lambda: col != value,
            "in": lambda: col.in_([value]),
            "not_in": lambda: ~col.in_([value]),
            "lt": lambda: col < value if isinstance(value, (int, float, datetime, date)) else None,
            "lte": lambda: col <= value if isinstance(value, (int, float, datetime, date)) else None,
            "gt": lambda: col > value if isinstance(value, (int, float, datetime, date)) else None,
            "gte": lambda: col >= value if isinstance(value, (int, float, datetime, date)) else None,
            "between": lambda: None,  # Between requires array, not single value
            "date_is": lambda: col == value if isinstance(value, (datetime, date)) else None,
            "date_is_not": lambda: col != value if isinstance(value, (datetime, date)) else None,
            "date_before": lambda: col < value if isinstance(value, (datetime, date)) else None,
            "date_after": lambda: col > value if isinstance(value, (datetime, date)) else None,
        }

        handler = filter_handlers.get(match_mode)
        if not handler:
            raise ValueError(f"Invalid match mode '{match_mode}'")

        return handler()

    def _build_filter_clauses(self, model_class: Type, filters: Dict[str, Dict[str, Any]]):
        """Build filter clauses and collect required joins."""
        filter_clauses = []
        joins_needed = set()

        for field, condition in filters.items():
            value = condition.get("value")
            match_mode = condition.get("match_mode")

            # Resolve field path (handles both simple fields and relationships)
            col, relation_attr = self._resolve_field_path(model_class, field)

            # Track relationship attributes that need to be joined
            if relation_attr:
                joins_needed.add(relation_attr)

            # Create filter clause
            clauses = self._create_filter_clause(col, match_mode, value)
            filter_clauses.extend(clauses)

        return filter_clauses, joins_needed

    def _add_active_filters(self, model_class: Type, joins_needed: set, filter_clauses: list):
        """Add is_active = True filters for main model and joined models."""
        # Main model
        if hasattr(model_class, 'is_active'):
            filter_clauses.append(model_class.is_active == True)

        # Joined models
        for relation_attr in joins_needed:
            related_model = relation_attr.property.entity.class_
            if hasattr(related_model, 'is_active'):
                filter_clauses.append(related_model.is_active == True)

    def _determine_order_field(self, model_class: Type, order_by: Optional[str]):
        """Determine the field to order by."""
        if order_by:
            if not hasattr(model_class, order_by):
                raise ValueError(f"'{order_by}' field is not valid for {model_class.__name__}")
            return getattr(model_class, order_by)

        # Default ordering logic
        for default_field in ['created_at', 'id']:
            if hasattr(model_class, default_field):
                return getattr(model_class, default_field)

        # Use first column as fallback
        table_columns = list(model_class.__table__.columns)
        if not table_columns:
            raise ValueError(f"No columns found in model {model_class.__name__}")

        return table_columns[0]

    def _build_queries(
            self, model_class: Type, joins_needed: set, filter_clauses: list,
            order_field, order_direction: str, skip: int, limit: int,
            select_relateds: Optional[list[str]] = None,
            prefetch_relateds: Optional[list[str]] = None
    ):
        """Build the main query and count query."""
        # Create base queries
        query = select(model_class)
        count_query = select(func.count()).select_from(model_class)

        # Add joins for relationships
        for relation_attr in joins_needed:
            query = query.join(relation_attr)
            count_query = count_query.join(relation_attr)

        # Add relationship loading options
        if select_relateds:
            for relation in select_relateds:
                query = query.options(joinedload(getattr(model_class, relation)))

        if prefetch_relateds:
            for relation in prefetch_relateds:
                query = query.options(selectinload(getattr(model_class, relation)))

        # Apply filters
        if filter_clauses:
            query = query.where(and_(*filter_clauses))
            count_query = count_query.where(and_(*filter_clauses))

        # Apply ordering
        if order_direction.lower() == "asc":
            query = query.order_by(order_field)
        else:
            query = query.order_by(desc(order_field))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        return query, count_query

    async def find(
            self,
            session: AsyncSession,
            model: str | Type,
            filters: Dict[str, Dict[str, Any]],
            skip: int = 0,
            limit: int = 100,
            active: bool = True,
            order_by: Optional[str] = None,
            order_direction: str = "desc",
            select_relateds: Optional[list[str]] = None,
            prefetch_relateds: Optional[list[str]] = None
    ) -> Tuple[List[Any], int]:
        """
        Flexible filtering with pagination and sorting. Returns (items, total).

        Args:
            session: Database session
            model: Model class or name of the model to query
            filters: Dictionary of filters in format: {field_name: {match_mode: str, value: Any}}
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            active: Whether to filter by is_active = True
            order_by: Field name to order by (defaults to created_at if available)
            order_direction: 'asc' or 'desc'
            select_relateds: List of relationship names to eager load with joins (joinedload)
            prefetch_relateds: List of relationship names to eager load with separate queries (selectinload)
        """
        # Get the target model class
        model_name = model if isinstance(model, str) else None
        if isinstance(model, str):
            model = self.get_model_class(model)

        # Build query components
        filter_clauses, joins_needed = self._prepare_filters(model, filters, active)
        order_field = self._determine_order_field(model, order_by)

        # Create and execute queries
        query, count_query = self._build_queries(
            model, joins_needed, filter_clauses,
            order_field, order_direction, skip, limit,
            select_relateds, prefetch_relateds
        )

        # Fetch results
        items, total = await self._execute_queries(session, query, count_query)

        return items, total

    def _prepare_filters(self, model_class: Type, filters: Dict[str, Dict[str, Any]], active: bool):
        """
        Prepare all filter clauses and determine required joins.

        Args:
            model_class: The SQLAlchemy model class to filter
            filters: Dictionary of field filters
            active: Whether to add is_active=True filters

        Returns:
            Tuple of (filter_clauses, joins_needed)
        """
        filter_clauses, joins_needed = self._build_filter_clauses(model_class, filters)

        if active:
            self._add_active_filters(model_class, joins_needed, filter_clauses)

        return filter_clauses, joins_needed

    async def _execute_queries(self, session: AsyncSession, query, count_query) -> Tuple[List[Any], int]:
        """
        Execute both the main query and count query, returning results.

        Args:
            session: Database session
            query: Main SQLAlchemy query for items
            count_query: Count query for total records

        Returns:
            Tuple of (items, total_count)
        """
        # Execute main query for items
        result = await session.execute(query)
        items = list(result.scalars().all())

        # Execute count query for total
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()

        return items, int(total)
