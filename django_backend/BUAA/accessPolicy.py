from .models import SuperAdmin
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
            "action": "retrieve",
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": "update",
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


class BlockAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "create", "retrieve"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["update", "destroy"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user",
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)


class OrgAppAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["list", "destroy", "retrieve", "verity"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user",
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)


class OrgAccessPolicy(AccessPolicy):
    statements = [
        {
            {
                "action": ["list", "retrieve", "get_org_by_block", "search_all", "search_org_by_block", "get_recommended_org"],
                "principal": "*",
                "effect": "allow",
            },
            {
                "action": ["create", "destroy"],
                "principal": "*",
                "effect": "allow",
                "condition": "is_super_user",
            },
            {
                "action": ["update"],
                "principal": "*",
                "effect": "allow",
                "condition": ["(is_super_user or is_manager)"]
            },
            {
                "action": ["change_org_owner"],
                "principal": "*",
                "effect": "allow",
                "condition": ["(is_super_user or is_owner)"]
            },
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_manager(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org = view.get_object()
        return OrgManager.objects.filter(org=org.id, person=request.user.id).exists()

    def is_owner(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org = view.get_object()
        return org.owner == request.user.id


class FollowedOrgAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["get_followed_org"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self)"]
        },
        {
            "action": ["create"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self_create)"]
        },
        {
            "action": ["destroy"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self_destroy)"]
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == view.get_object().id

    def is_self_create(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == request.query_params.get('person')

    def is_self_destroy(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == request.query_params.get('user')


class OrgManagerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create", "destroy"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_owner)"]
        },
        {
            "action": "get_all_managers",
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["get_managed_org", "search_managed_org"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self)"]
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_owner(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org_id = request.query_params.get('org')
        org = Organization.objects.get(id=org_id)
        return org.owner == request.user.id

    def is_self(self, request, view, pk, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == pk



class ArticleAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["get_all_managers"],
            "principal": "*",
            "effect": "allow"
        },
        {
            "action": ["create", "destroy"],
            "principal": ["group:editor"],
            "effect": "allow",


        }
    ]

