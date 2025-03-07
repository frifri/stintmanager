from django.contrib import admin
from .models import Race, RaceDriver, AvailabilityWindow, DrivingAssignment


class AvailabilityWindowInline(admin.TabularInline):
    model = AvailabilityWindow
    extra = 1
    fields = ('start_time', 'end_time')


class DrivingAssignmentInline(admin.TabularInline):
    model = DrivingAssignment
    extra = 1
    fields = ('start_time', 'end_time', 'notes')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'track_name', 'start_time', 'duration_hours', 
                   'created_by', 'created_at')
    list_filter = ('track_name', 'created_at')
    search_fields = ('name', 'track_name', 'created_by__email')
    date_hierarchy = 'start_time'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'track_name')
        }),
        ('Timing', {
            'fields': ('start_time', 'duration_hours', 'avg_lap_time_seconds')
        }),
        ('Ownership', {
            'fields': ('created_by',)
        })
    )


@admin.register(RaceDriver)
class RaceDriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'race', 'timezone', 'created_at')
    list_filter = ('timezone', 'race__name')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 
                    'race__name')
    inlines = [AvailabilityWindowInline, DrivingAssignmentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'race')


@admin.register(AvailabilityWindow)
class AvailabilityWindowAdmin(admin.ModelAdmin):
    list_display = ('race_driver', 'get_race', 'start_time', 'end_time')
    list_filter = ('race_driver__race__name', 'start_time')
    search_fields = ('race_driver__user__email', 'race_driver__race__name')
    
    def get_race(self, obj):
        return obj.race_driver.race.name
    get_race.short_description = 'Race'
    get_race.admin_order_field = 'race_driver__race__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'race_driver__user', 
            'race_driver__race'
        )


@admin.register(DrivingAssignment)
class DrivingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('race_driver', 'get_race', 'start_time', 'end_time', 
                   'duration_display')
    list_filter = ('race_driver__race__name', 'start_time')
    search_fields = ('race_driver__user__email', 'race_driver__race__name', 
                    'notes')
    
    def get_race(self, obj):
        return obj.race_driver.race.name
    get_race.short_description = 'Race'
    get_race.admin_order_field = 'race_driver__race__name'
    
    def duration_display(self, obj):
        return f"{obj.duration_hours():.1f} hours"
    duration_display.short_description = 'Duration'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'race_driver__user', 
            'race_driver__race'
        )