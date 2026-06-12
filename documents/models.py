from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.utils.text import slugify


search_vector = SearchVectorField(null=True, blank=True)

class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/%Y/%m/')
    tags = models.ManyToManyField(Tag, blank=True)
    uploaded_by = models.ForeignKey(
        'members.User',
        on_delete=models.PROTECT,
        related_name='documents',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
