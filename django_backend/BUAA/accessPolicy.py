from .views import *
from rest_access_policy import AccessPolicy


class WXUserAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "destroy"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user"
        },
        {
            "action": ["retrieve", "update"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self)"]
        },
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        print(view.get_object().id)
        return request.user.id == view.get_object().id






class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": ["publish", "unpublish"],
            "principal": ["group:editor"],
            "effect": "allow"
        }
    ]

