from django.db import models


class Visit(models.Model):
    path = models.CharField(max_length=200)
    visited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.path} at {self.visited_at}"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    description = models.TextField(blank=True)
    materials = models.TextField(blank=True)
    made_on = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")

    class Meta:
        ordering = ("-made_on", "-id")

    def __str__(self):
        return self.title


class Photo(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = models.ImageField(upload_to="photos/")
    caption = models.TextField(blank=True)
    alt_text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.alt_text} for {self.project.title}"
