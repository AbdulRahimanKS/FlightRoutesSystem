from django import forms
from .models import Airport, Route


# Airport Form
class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter airport code (e.g. COK)'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter airport name'}),
        }
        
        
# Route Form
class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['from_airport', 'to_airport', 'position', 'duration', 'parent']
        widgets = {
            'from_airport': forms.Select(attrs={'class': 'form-select'}),
            'to_airport': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter duration (in minutes)'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        from_airport = cleaned_data.get('from_airport')
        to_airport = cleaned_data.get('to_airport')
        position = cleaned_data.get('position')
        parent = cleaned_data.get('parent')

        # Same airport check
        if from_airport and to_airport and from_airport == to_airport:
            self.add_error('to_airport', "From and To airport cannot be the same")

        # Unique check
        if from_airport and position:
            existing_route = Route.objects.filter(from_airport=from_airport, position=position)
            if self.instance.pk:
                existing_route = existing_route.exclude(pk=self.instance.pk)
            
            if existing_route.exists():
                self.add_error('position', f"A route from '{from_airport.name}' with position '{position}' already exists")
                
        # Tree validations                
        if not parent:
            # Allow root routes only if no routes exists / if adding another position from root airport
            root_routes = Route.objects.filter(parent__isnull=True)
            if root_routes.exists():
                root_airport = root_routes.first().from_airport
                if from_airport != root_airport:
                    self.add_error('parent', f"Root routes must start from '{root_airport.name}'. Please select a parent route.")
        else:
            # Parent route validation
            if from_airport and from_airport != parent.to_airport:
                self.add_error('from_airport', "From airport must match parent route's To airport")

        return cleaned_data
    

# Search Form
class SearchNthNodeForm(forms.Form):
    DIRECTION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]
    
    airport = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Starting Airport"
    )
    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Direction"
    )
    nth_position = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Position (e.g., 1, 2 ...)'
        }),
        label="Nth Position"
    )
    
    
# Shortest Node Form
class ShortestNodeForm(forms.Form):
    from_airport = forms.ModelChoiceField(
        queryset=Airport.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="From Airport"
    )
    to_airport = forms.ModelChoiceField(
        queryset=Airport.objects.all(), 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="To Airport"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        from_airport = cleaned_data.get('from_airport')
        to_airport = cleaned_data.get('to_airport')
        
        if from_airport and to_airport and from_airport == to_airport:
            self.add_error('to_airport', "From and To airport cannot be the same")
        
        return cleaned_data