from django.contrib import admin
from .models import Team, TeamMembership


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1
    autocomplete_fields = ['driver']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'race', 'owner', 'created_at')
    list_filter = ('race__name', 'created_at')
    search_fields = ('name', 'race__name', 'owner__email')
    inlines = [TeamMembershipInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('race', 'owner')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('driver', 'team', 'role', 'created_at')
    list_filter = ('team__race__name', 'role', 'created_at')
    search_fields = ('driver__user__email', 'team__name', 'role')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'team', 'driver', 'driver__user'
        )