from rest_framework.permissions import BasePermission


class MyPermission(BasePermission):
    message = "sorry,您没有权限"
    def has_permission(self, request, view):
        # 内置封装的方法
        '''
        判断该用户有没有权限
        '''
        # 判断用户是不是VIP用户
        # 如果是VIP用户就返回True
        # 如果是普通用户就返会Flase

        if request.method in ["POST","PUT","DELETE"]:
            # print(111)
            print(request.user.username)
            print(request.user.type)
            print(type(request.user.type))
            if request.user.type == 2:   # 是VIP用户
                print(2222)
                return True
            else:
                return False
        else:
            return True

    def has_object_permission(self, request, view, obj):
        # 用来判断针对的obj权限：
        # 例如：是不是某一个人的评论
        '''
        只有评论人是自己才能删除选定的评论
        '''
        if request.method in ["PUT","DELETE"]:
            print(obj.user.username)
            print(request.user.username)
            if obj.user == request.user:
                # 表示当前评论对象的用户就是登陆用户
                return True
            else:
                return False
        else:
            return True