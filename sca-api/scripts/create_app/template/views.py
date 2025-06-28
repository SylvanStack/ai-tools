


from fastapi import APIRouter, Depends
from ..infa.utils.response import SuccessResponse
from . import schemas, crud, models

app = APIRouter()
