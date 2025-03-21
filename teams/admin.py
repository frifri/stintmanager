from django.contrib import admin
from .models import Team, TeamMembership, TeamRaceEntry


class TeamMembershipInline(admin.TabularInline):
    model = TeamMembership
    extra = 1
    autocomplete_fields = ['user']


class TeamRaceEntryInline(admin.TabularInline):
    model = TeamRaceEntry
    extra = 1
    autocomplete_fields = ['race']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'owner__email')
    inlines = [TeamMembershipInline, TeamRaceEntryInline]
    
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


@admin.register(TeamRaceEntry)
class TeamRaceEntryAdmin(admin.ModelAdmin):
    list_display = ('team', 'race', 'created_at')
    list_filter = ('race__name', 'created_at')
    search_fields = ('team__name', 'race__name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'race')