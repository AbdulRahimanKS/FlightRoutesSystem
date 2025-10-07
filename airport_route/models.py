from django.db import models


# Airport Model 
class Airport(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# Airport Route Model
class Route(models.Model):
    SIDE_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]
    
    from_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='departing_routes')
    to_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='arriving_routes')
    position = models.CharField(max_length=10, choices=SIDE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_airport', 'position']
    
    def __str__(self):
        return f"{self.from_airport.name} -> {self.to_airport.name} ({self.position})"
