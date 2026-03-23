from ninja import Router

router = Router()

@router.get("/")
def list_users(request):
    return {"message": "Users API working"}