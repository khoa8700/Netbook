from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField, DateField, FloatField, IntegerField, TextField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.conf import settings
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from datetime import datetime
from ckeditor.fields import RichTextField
import pytz

# Create your models here.

class UserInfo(models.Model):
    ADMIN=1
    AUTHOR=2
    CUSTOMER=3

    ROLE_CHOICES=(
        (ADMIN,'admin'),
        (AUTHOR,'author'),
        (CUSTOMER,'customer'),
    )

    
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.CharField(max_length=200, null=True)
    # phone = models.CharField(max_length=200, null=True)
    avatar = models.ImageField(default="images/noava.png", null=True, blank=True,upload_to="images/")
    birthday = models.DateField(blank=True, null=True)
    hobby = models.CharField(max_length=200, blank=True, null=True)
    job = models.CharField(max_length=200, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES,blank=True,null=True,default=CUSTOMER)

    self_introduction = RichTextField(null=True,blank=True)

    lock_out_time = models.DateTimeField(null=True,blank=True)

    ban_time = models.DateTimeField(null=True,blank=True)
    prev_ban_level = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    def is_banned(self):
        if self.ban_time is None:
            return False
        local_tz = pytz.timezone('Asia/Bangkok')
        current = timezone.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
        userinfo_ban = self.ban_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        print("current day : ",current)
        print("ban day : ",userinfo_ban)

        is_banned = (current <= userinfo_ban)

        print("is banned : ",is_banned)
        return is_banned
    def is_locked_out(self):
        if self.lock_out_time is None:
            return False
        local_tz = pytz.timezone('Asia/Bangkok')
        current = timezone.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
        userinfo_ban = self.lock_out_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        print("current day : ",current)
        print("ban day : ",userinfo_ban)

        is_banned = (current <= userinfo_ban)

        print("is banned : ",is_banned)
        return is_banned

class Tag(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(null=False)
    description = RichTextField(null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args,**kwargs)

BOOL_CHOICES = ((True, 'Finished'), (False, 'Ongoing'))

class Novel(models.Model):
    title = models.CharField(max_length=200, null=True)
    slug = models.SlugField(null=False)
    description = RichTextField()
    thumbnail = models.ImageField(default="images/placeholder.png", null=True, blank=True,upload_to="images/")
    userinfo = ForeignKey(UserInfo,null=True, blank=True,on_delete=models.CASCADE)
    tags = ManyToManyField(Tag)
    avg_rate = FloatField(default=0.0)
    number_rating = IntegerField(default=0)
    views = IntegerField(default=0)
    publication_date = models.DateTimeField(null=True,blank=True)
    status = models.BooleanField(default=False,choices=BOOL_CHOICES)
    def __str__(self):    
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args,**kwargs)
    
    def get_absolute_url(self):
        return reverse('detail',kwargs={'slug':self.slug})
    
    def get_absolute_url_nav(self):
        return reverse('navbar_novel',kwargs={'id_novel':self.id})

    def get_absolute_url_edit(self):
        return reverse('edit_novel',kwargs={'id_novel':self.id})
    
    def get_absolute_url_create_chapter(self):
        return reverse('create_chapter',kwargs={'slug':self.slug})
    
    def get_absolute_url_write_chapters(self):
        return reverse('my_work_detail',kwargs={'slug':self.slug})
    

class Chapter(models.Model):
    novel = ForeignKey(Novel,null=True, blank=True, on_delete=models.CASCADE)
    number = IntegerField()
    content = RichTextField(null=True,blank=True)
    title = models.CharField(max_length=200, null=True, blank = True)
    views = IntegerField(default=0)
    update_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return str(self.novel.title)+"_"+str(self.number)
    
    def get_absolute_url(self):
        slug = self.novel.slug
        return reverse('read',kwargs={'slug':slug,'chapter_number':self.number})
    
    def get_edit_url(self):
        slug = self.novel.slug
        return reverse('edit_chapter',kwargs={'slug':slug,'chapter_number':self.number})
    

# class NovelTag(models.Model):
#     novel = ForeignKey(Novel,null=True, blank=True,on_delete=models.CASCADE)
#     tag = ForeignKey(Tag,null=True, blank=True,on_delete=models.CASCADE)
    
#     def __str__(self):
#         return str(self.novel.title)+" "+str(self.tag.name)

class Rating(models.Model):
    rate = IntegerField()
    novel = ForeignKey(Novel,null=True, blank=True,on_delete=models.CASCADE)
    user = ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE)
    class Meta:
        constraints = [
            CheckConstraint(check=Q(rate__range=(0, 5)), name='valid_rate'),
            UniqueConstraint(fields=['user', 'novel'], name='rating_once'),
        ]

class Following(models.Model):
    is_followed = BooleanField(default=False)
    user = ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE)
    novel = ForeignKey(Novel,null=True, blank=True,on_delete=models.CASCADE)

class Comment(models.Model):
    user = ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE)
    novel = ForeignKey(Novel,null=True, blank=True,on_delete=models.CASCADE)
    content = RichTextField(default="Hello world")
    publication_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.novel.title
    
    # def to_dict(self):
    #     return {
    #         "username" : self.user.userinfo.name,
    #         "content" : self.content,
    #         "publication_date" : self.publication_date.strftime("%Y-%m-%d %H:%M:%S") if self.publication_date is not None else None
    #     }

class Bookmark(models.Model):
    user = ForeignKey(User,null=True, blank=True,on_delete=models.CASCADE)
    novel = ForeignKey(Novel,null=True, blank=True,on_delete=models.CASCADE)
    number = IntegerField()
    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'novel','number'], name='read_chapter'),
        ]