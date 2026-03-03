from fastapi import APIRouter, Depends
from app.deps.auth import require_token
from app.errors import AppError
from app.schema.user import UserOut, UserCreate
from app.schema.default import DefaultResponse, CreatedResponse

router = APIRouter()

@router.get("/users/me", response_model=DefaultResponse[UserOut], dependencies=[Depends(require_token)])
def get_current_user():
    return {
        "success": True,
        "data": {
            "user_id": auth["user_id"],
            "token": auth["token"][:10] + "..."
        }
    }

# In-memory data store
_fake_db: list[dict] = [
{"id": 1,"name": "Alice","email": "alice@example.com", "role": "admin","created_at": "2024-01-01T00:00:00"},
{"id": 2,"name": "Bob","email": "bob@example.com", "role": "user","created_at": "2024-01-01T00:00:00"}
]
@router.get("/users/{user_id}", response_model=DefaultResponse[UserOut])
def get_user(user_id: int):
    user = next((u for u in _fake_db if u["id"] == user_id), None)
    if not user:
        raise AppError(
            status_code=404,
            code="USER_NOT_FOUND",
            message=f"User dengan ID {user_id} tidak ditemukan",
            detail=[]
        )
    return {
        "success": True,
        "data": user
    }

@router.get("/users", response_model=DefaultResponse[list[UserOut]])
def list_users():
    return {
        "success": True,
        "data": _fake_db,
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 2
        }
    }

@router.post("/users", status_code=201, response_model=CreatedResponse[UserCreate])
def create_user(user: UserCreate):
    return {
        "success": True,
        "data": user
    }

# @router.get("/users/{user_id}")
# def get_user(user_id: int):
#     return {
#         "success": True,
#         "data": {
#             "id": user_id,
#             "name": "Sample User",
#             "email": "user@example.com"
#         }
#     }
