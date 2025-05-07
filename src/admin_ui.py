from fastapi import FastAPI
from sqladmin import Admin, ModelView
from db.base import engine
from db.models import User, Advertisement,AdminApprovalStatus
from markupsafe import Markup

app = FastAPI()

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from constants import (
        DEFAULT_ADMIN_PANEL_USERNAME,
        DEFAULT_ADMIN_PANEL_PASSWORD,
        SECRET_KEY  
)

class SimpleAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == DEFAULT_ADMIN_PANEL_USERNAME and password == DEFAULT_ADMIN_PANEL_PASSWORD:
            request.session.update({"token": SECRET_KEY})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("token") == SECRET_KEY


class UserAdminPanel(ModelView, model=User):
    name = "کاربر"
    name_plural = "کاربران"

    column_list = [
        User.user_id,
        User.username,
        User.first_name,
        User.last_name,
        User.is_admin,
        User.phone_number,
        User.inserted_at
    ]
    
    searchable_columns = [
        User.username
    ]
    
    can_edit = True
    can_delete = False
    can_create = False
    page_size = 20
    page_size_options = [25, 50, 100, 200]
    column_sortable_list = column_list
                            

class AdvertisementAdminPanel(ModelView, model=Advertisement):
    name = "آگهی"
    name_plural = "آگهی‌ها"

    column_list = [
        Advertisement.adv_id,
        Advertisement.user_id,
        Advertisement.vehicle_type,
        Advertisement.advertisement_type,
        Advertisement.admin_approved_status,
        Advertisement.money,
        Advertisement.inserted_at
    ]
    
    searchable_columns = [
        Advertisement.money
    ]
    
    can_edit = True
    can_delete = False
    can_create = False
    page_size = 30
    page_size_options = [25, 50, 100, 200]
    column_sortable_list = column_list
    column_formatters = {
        Advertisement.admin_approved_status: lambda model, field: Markup({
            AdminApprovalStatus.PENDING: "در انتظار",
            AdminApprovalStatus.APPROVED: "تایید شده",
            AdminApprovalStatus.REJECTED: "رد شده"
        }.get(model.admin_approved_status, "نامشخص"))
    }
    
    column_formatters_detail = {
        Advertisement.admin_approved_status: lambda model, field: Markup({
            AdminApprovalStatus.PENDING: "در انتظار",
            AdminApprovalStatus.APPROVED: "تایید شده",
            AdminApprovalStatus.REJECTED: "رد شده"
        }.get(model.admin_approved_status, "نامشخص"))
    }


auth_backend = SimpleAuth(secret_key=SECRET_KEY)  # Use a secure key!

admin = Admin(app, engine, authentication_backend=auth_backend)
admin.add_view(UserAdminPanel)
admin.add_view(AdvertisementAdminPanel)


