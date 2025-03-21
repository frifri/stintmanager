from django.contrib import admin
from .models import Team, TeamMembership


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1
    autocomplete_fields = ['user']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__email')
    inlines = [TeamMembershipInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'team__name', 'role')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'team', 'user'
        )