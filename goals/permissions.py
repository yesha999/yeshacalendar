from rest_framework import permissions

from goals.models import BoardParticipant, GoalCategory, Board, Goal, GoalComment


class BoardPermission(permissions.IsAuthenticated):
    """
    Пермишн наследуется от IsAuthenticated и добавляет новый функционал:
    разрешает изменять, удалять доску только ее создателю
    """
    def has_object_permission(self, request, view, obj: Board):
        _filter = {"user": request.user, "board": obj}
        if request.method not in permissions.SAFE_METHODS:
            _filter.update({"role": BoardParticipant.Role.owner})
        return BoardParticipant.objects.filter(**_filter).exists()


class GoalCategoryPermission(permissions.IsAuthenticated):
    """
    Пермишн наследуется от IsAuthenticated и добавляет новый функционал:
    разрешает изменять, удалять категорию только ее создателю и редактору доски
    """
    def has_object_permission(self, request, view, obj: GoalCategory):
        _filter = {"user": request.user, "board": obj.board}
        if request.method not in permissions.SAFE_METHODS:
            _filter.update({
                'role__in': [
                    BoardParticipant.Role.owner,
                    BoardParticipant.Role.writer
                ]
            })
        return BoardParticipant.objects.filter(**_filter).exists()


class GoalPermission(permissions.IsAuthenticated):
    """
    Пермишн наследуется от IsAuthenticated и добавляет новый функционал:
    разрешает изменять, удалять цель только создателю или редактору доски
    """
    def has_object_permission(self, request, view, obj: Goal):
        _filter = {"user": request.user, "board": obj.category.board}
        if request.method not in permissions.SAFE_METHODS:
            _filter.update({"role__in": [BoardParticipant.Role.owner, BoardParticipant.Role.writer]})
        return BoardParticipant.objects.filter(**_filter).exists()


class GoalCommentPermission(permissions.IsAuthenticated):
    """
    Пермишн наследуется от IsAuthenticated и добавляет новый функционал:
    разрешает изменять, удалять комментарий только его создателю (возвращает False в ином случае)
    """
    def has_object_permission(self, request, view, obj: GoalComment):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class GoalCommentCreatePermission(permissions.IsAuthenticated):
    """
    Пермишн наследуется от IsAuthenticated и добавляет новый функционал:
    разрешает добавлять комментарии к целям только создателям или редакторам доски
    """
    def has_object_permission(self, request, view, obj: GoalComment):
        if request.method in permissions.SAFE_METHODS:
            return True
        return BoardParticipant.objects.filter(user=request.user, board=obj.goal.category.board,
                                               role__in=[BoardParticipant.Role.owner,
                                                         BoardParticipant.Role.writer]).exists()
