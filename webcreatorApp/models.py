from django.db import models

# Create your models here.
class Keyword(models.Model):
    id = models.AutoField(primary_key=True)
    pic_keywords = models.TextField( default="")
    display_keywords = models.TextField( default="")

    def disp(self):
        print(f" id; {self.id}\nPic keywords: {self.pic_keywords}\ndisplay: {self.display_keywords}")

    def __str__(self):
        return self.display_keywords.split(",")[0]
    

class Imgpath(models.Model):
    fk = models.ForeignKey(Keyword, on_delete=models.CASCADE)  # ForeignKey to Keyword
    paths = models.TextField(default="")  # Field to store concatenated image paths

    def dispf(self):
        print("\n\n")
        print(self.paths)
        print("\n\n")

    def __str__(self):
        return self.fk.display_keywords.split(",")[0]










