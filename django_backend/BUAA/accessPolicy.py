from .models import SuperAdmin, OrgManager, Organization, Activity
from .views import *
from rest_access_policy import AccessPolicy


class WXUserAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "destroy", "search_user"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user"
        },
        {
            "action": ["retrieve", "get_boya_followers"],
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
        return request.user == view.get_object()


class BlockAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["update", "destroy", "create"],
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
            "action": ["list", "destroy", "retrieve", "verify"],
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
        return org.owner == request.user


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
        return request.user.id == eval(view.kwargs['pk'])

    def is_self_create(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == request.data.get('person')

    def is_self_destroy(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == eval(request.query_params.get('user'))


class OrgManagerAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create_wrapper"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_owner_create)"]
        },
        {
            "action" : ["destroy"],
            "principal" : "*",
            "effect" : "allow",
            "condition" : ["(is_super_user or is_owner_destroy)"]
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

    def is_owner_create(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org_id = request.data.get('org')
        org = Organization.objects.get(id=org_id)
        return org.owner == request.user

    def is_owner_destroy(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org_id = eval(request.query_params.get('org'))
        org = Organization.objects.get(id=org_id)
        return org.owner == request.user

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == eval(view.kwargs['pk'])

    
class CategoryAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "create"],
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
    
    
class AddressAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "create"],
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


class FeedbackAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["list", "retrieve", "destroy", "search_all_feedback", "search_user_feedback"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user",
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)


class ActAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve", "search_all", "get_org_act", "search_act_by_org", "get_org_act_status", "get_block_act", "get_block_act_status", "search_all", "search_act_by_block", "get_recommended_act" ],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["create", "create_wrapper"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_valid_create)"],
        },
        {
            "action": ["update_wrapper", "destroy_wrapper"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_valid_update)"],
        },
        {
            "action": ["get_user_act_status", "get_user_act", "get_user_unstart_act", "get_user_ing_act", "get_user_finish_act", "get_followed_org_act", "search_user_released_act"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_self",
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_valid_create(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        block_id = request.data.get('block')
        block = Block.objects.get(id=block_id)
        # 不能是博雅版块下的活动
        if block.name == "博雅":
            return False
        # 活动的拥有者必须是自己
        if request.user.id != request.data.get('owner'):
            return False
        # 个人活动可通过
        if block.name == "个人":
            return True
        # 组织下的活动，必须为组织管理员
        org_id = request.data.get('org')
        return OrgManager.objects.filter(org=org_id, person=request.user.id).exists()

    def is_valid_update(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        act_id = eval(view.kwargs['pk'])
        act = Activity.objects.get(id=act_id)
        # 活动拥有者可以改活动
        if act.owner == request.user:
            return True
        # 组织下的活动，管理员可以改活动
        if act.block.name != "个人":
            return OrgManager.objects.filter(org=act.org.id, person=request.user.id).exists()
        # 其余情况均为非法
        return False

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == eval(view.kwargs['user_id'])


class JoinedActAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["create"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self_create)"],
        },
        {
            "action": ["destroy_wrapper"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_valid_destroy)"],
        },
        {
            "action": ["get_act_participants"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_valid_get)"],
        },
        {
            "action": ["get_user_joined_act", "search_user_joined_act", "get_user_joined_act_status", "get_user_joined_act_begin_order"],
            "principal": "*",
            "effect": "allow",
            "condition": ["(is_super_user or is_self)"],
        },
        {
            "action": ["get_act_participants_number"],
            "principal": "*",
            "effect": "allow",
        },

    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_self_create(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == request.data.get('person')

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.user.id == eval(view.kwargs['user_id'])

    def is_valid_destroy(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        # 本人退出
        if request.user.id == eval(request.query_params.get('person')):
            return True

        act_id = eval(request.query_params.get('act'))
        act = Activity.objects.get(id=act_id)
        # 活动负责人
        if request.user == act.owner:
            return True
        # 管理员移除
        if act.org is not None:
            return OrgManager.objects.filter(org=act.org.id, person=request.user.id).exists()
        return False

    def is_valid_get(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        # 活动负责人
        act_id = eval(view.kwargs['act_id'])
        act = Activity.objects.get(id=act_id)
        if request.user == act.owner:
            return True
        # 活动管理员
        if act.org is not None:
            return OrgManager.objects.filter(org=act.org.id, person=request.user.id).exists()
        return False

class CommentAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "create_wrapper", "get_act_comments", "retrieve", "search_by_act", "search_by_user", "get_user_comment"],
            "principal": "*",
            "effect": "allow",
        },
        {
            "action": ["update", "update_wrapper", "destroy"],
            "principal": "*",
            "effect": "allow",
            "condition": "(is_super_user or is_valid)"
        },
        {
            "action": ["search_all_comment"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_super_user"
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_valid(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        comment = view.get_object()
        # 本人
        if comment.user == request.user:
            return True
        # 活动负责人
        if comment.act.owner == request.user:
            return True
        # 组织管理员
        if comment.act.org is not None:
            return OrgManager.objects.filter(org=comment.act.org.id, person=request.user.id).exists()
        return False


class ImageAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["remove_act_avatar", "upload_act_avatar"],
            "principal": "*",
            "effect": "allow",
            "condition": "(is_super_user or is_act_owner_or_manager)"
        },
        {
            "action": ["upload_org_avatar"],
            "principal": "*",
            "effect": "allow",
            "condition": "(is_super_user or is_manager)"
        }
    ]

    def is_super_user(self, request, view, action) -> bool:
        return isinstance(request.user, SuperAdmin)

    def is_act_owner_or_manager(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        act_id = eval(view.kwargs['act_id'])
        act = Activity.objects.get(id=act_id)
        # 活动拥有者
        if act.owner == request.user:
            return True
        # 组织下的活动，管理员
        if act.block.name != "个人":
            return OrgManager.objects.filter(org=act.org.id, person=request.user.id).exists()
        # 其余情况均为非法
        return False

    def is_manager(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        org_id = eval(view.kwargs['org_id'])
        return OrgManager.objects.filter(org=org_id, person=request.user.id).exists()


class OtherAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": "verify_email",
            "principal": "*",
            "effect": "allow",
            "condition": "is_self"
        },
        {
            "action": ["user_org_relation", "user_act_relation"],
            "principal": "*",
            "effect": "allow",
            "condition": "is_self_user"
        }
    ]

    def is_self(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.data.get('id') == request.user.id

    def is_self_user(self, request, view, action) -> bool:
        if not isinstance(request.user, WXUser):
            return False
        return request.data.get('user') == request.user.id
