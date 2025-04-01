from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_example():
    return {"message": "This is an example endpoint"}
