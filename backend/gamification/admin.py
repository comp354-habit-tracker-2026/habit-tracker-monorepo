from django.contrib import admin

from gamification.models import Badge, UserBadge, Streak, Milestone, UserMilestone


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'activity_type', 'threshold', 'points')
    list_filter = ('badge_type', 'activity_type')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge__badge_type',)


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_count', 'longest_count', 'last_activity_date')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric', 'threshold')
    list_filter = ('metric',)


@admin.register(UserMilestone)
class UserMilestoneAdmin(admin.ModelAdmin):
    list_display = ('user', 'milestone', 'reached_at')
