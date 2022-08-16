from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created", "updated", "board")
    search_fields = ("title", "user", "board")


class GoalAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "status", "priority", "description", "due_date", "created", "updated")
    search_fields = ("title", "user", "category", "status", "priority", "description")


admin.site.register(GoalCategory, GoalCategoryAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(GoalComment)
admin.site.register(Board)
admin.site.register(BoardParticipant)

