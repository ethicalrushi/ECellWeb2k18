from django.db import models

# Create your models here.
#Anther random addn

<<<<<<< HEAD
=======

>>>>>>> 81cdb9c8421ab187806be8f969045707294e7b34
MEMBER_TYPE = (
        ('Dir', 'Director, NIT Raipur'),
        ('DnSW', 'Dean Student Welfare'),
        ('DnRC', 'Dean Research & Cons.'),
        ('Fclty','Faculty Incharge'),
        ('MNG', 'Manager'),
        ('HC', 'Head Co-ordinator'),
        ('OC', 'Overall Co-ordinator'),
        ('EXEC', 'Executive'),
    )






class Member(models.Model):
	name = models.CharField(max_length=100)
	#designation = models.CharField(max_length=200)
	url = models.URLField(blank=True, null=True)
	image = models.ImageField(upload_to='static/uploads/team', null=True, blank = True)
	member_type = models.CharField(max_length=5, choices= MEMBER_TYPE, default='EXEC')


	def __self__(self):
<<<<<<< HEAD
		return self.name
=======
		return self.name
>>>>>>> 81cdb9c8421ab187806be8f969045707294e7b34
