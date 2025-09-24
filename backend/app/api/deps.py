from backend.app.schemas.common import PaginationParams

def pagination_params(
    limit: int,
    offset: int
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)