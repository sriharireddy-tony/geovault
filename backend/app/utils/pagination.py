from fastapi import Query


class PaginationParams:
    """Dependency to parse pagination query params."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=500, description="Page size"),
    ):
        self.page = page
        self.size = size
