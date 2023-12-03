from django.db import models

# Create your models here.
class Keyword(models.Model):
    pic_keywords = models.TextField( null=False)
    display_keywords = models.TextField( null=False )
    reverse = models.BooleanField(default=False)
    titlebar = models.BooleanField(default=True)

    def __str__(self):
        if self.titlebar:
            return self.display_keywords.split(",")[0]
        else:
            return f" No Title - items: {self.display_keywords}"
    

    

class Imgpath(models.Model):
    fk = models.ForeignKey(Keyword, on_delete=models.CASCADE)  # ForeignKey to Keyword
    paths = models.TextField(default="")  # Field to store concatenated image paths

    def __str__(self):
        return self.fk.display_keywords.split(",")[0]










