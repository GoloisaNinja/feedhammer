from django.db import models

class Feed(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField(unique=True)

    def __str__(self):
        return self.title

class Article(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    link = models.URLField(max_length=500)
    pub_date = models.DateTimeField()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title
