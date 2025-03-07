# races/forms.py
from django import forms
from .models import Race
from django.utils import timezone

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ['name', 'description', 'start_time', 'duration_hours', 
                 'track_name', 'avg_lap_time_seconds']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        self.fields['name'].widget.attrs['placeholder'] = '24 Hours of Le Mans 2024'
        self.fields['track_name'].widget.attrs['placeholder'] = 'Circuit de la Sarthe'
        self.fields['avg_lap_time_seconds'].widget.attrs['placeholder'] = '220'
        
        # Convert datetime to input format
        if 'instance' in kwargs and kwargs['instance'] is not None:
            if kwargs['instance'].start_time:
                self.initial['start_time'] = kwargs['instance'].start_time.strftime('%Y-%m-%dT%H:%M')

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now():
            raise forms.ValidationError("Race cannot start in the past")
        return start_time