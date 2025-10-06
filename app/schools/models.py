import random
import string

from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

from app.users.models import UserBase


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class School(models.Model):
    SHIFT_CHOICES = (
        ('MANANA', 'Mañana'),
        ('TARDE', 'Tarde'),
        ('NOCHE', 'Noche'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='schools', null=True, blank=True)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='school_photos/', null=True, blank=True)
    logo = models.ImageField(upload_to='school_logo/', null=True, blank=True)
    general_description = models.TextField(null=True, blank=True)
    income_description = models.TextField(null=True, blank=True)
    recovery_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    shifts = MultiSelectField(choices=SHIFT_CHOICES, max_length=50, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True, related_name='schools')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.name.lower().replace(' ', '-')
        super(School, self).save(*args, **kwargs)

    @property
    def average_valoration(self):
        comentarios = self.school_comments.all()
        if comentarios.exists():
            return round(sum(c.score for c in comentarios) / comentarios.count(), 2)

        return None

    def generate_recovery_code(self):
        code = string.ascii_letters + string.digits
        while True:
            new_code = ''.join(random.choice(code) for _ in range(10))
            if not School.objects.filter(recovery_code=new_code).exists():
                self.recovery_code = new_code
                self.save()
                return new_code

    def get_shifts_list(self):
        """Retorna una lista de etiquetas legibles para cada turno"""
        if not self.shifts:
            return []
        shift_dict = dict(self.SHIFT_CHOICES)
        # MultiSelectField puede retornar un string separado por comas o una lista
        if isinstance(self.shifts, str):
            shifts_list = [s.strip() for s in self.shifts.split(',') if s.strip()]
        else:
            shifts_list = list(self.shifts)
        return [shift_dict.get(shift, shift) for shift in shifts_list]


class Career(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='careers')
    name = models.CharField(max_length=100, null=False, blank=False)
    scope = models.TextField(null=False, blank=False)
    duration = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.school.name}'

    def get_duration(self):
        if self.duration == 1:
            return f'{self.duration} año'
        return f'{self.duration} años'


class Photo(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='school_photos/')
    description = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Foto de {self.school.name} ({self.id})"
