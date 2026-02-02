from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError

# Create your models here.
class Author(models.Model):
    name = models.CharField()
    last_name = models.CharField()

class Book(models.Model):
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('RE', 'Reading'),
        ('FI', 'Finished')
    ]
    title = models.CharField(max_length=50)
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES
    )
    published_date = models.DateField()
    read_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True)
    cover_image = models.FileField(upload_to='covers/', blank=True)

    def clean(self):
        super().clean()
        if self.read_date and self.read_date < self.published_date:
            raise ValidationError({"read_date": "The read date must be after the published date"})

    def __str__(self):
        return self.title