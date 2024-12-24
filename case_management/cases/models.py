from django.db import models

class Judge(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class CaseType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Case(models.Model):
    case_number = models.CharField(max_length=255, unique=True)
    parties = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    judge = models.ForeignKey(Judge, on_delete=models.CASCADE)
    case_type = models.ForeignKey(CaseType, on_delete=models.CASCADE)
    meeting_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.case_number} - {self.parties}"
