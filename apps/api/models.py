from django.db import models
from project.s3utils import *

import bcrypt

class User(models.Model):
    first_name      = models.CharField(max_length = 255)
    last_name       = models.CharField(max_length = 255)
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = '1. Users'

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def update(self, **data):
        first_name  = data.get('first_name')
        last_name   = data.get('last_name')

        if first_name:
            self.first_name = first_name.capitalize()

        if last_name:
            self.last_name = last_name.capitalize()

        self.save()

class UserAccount(models.Model):
    user            = models.ForeignKey(User, on_delete=models.CASCADE)
    image           = models.FileField(blank=True, null=True, storage=MediaStorage())
    email           = models.CharField(max_length = 255, blank=True, null=True)
    username        = models.CharField(max_length = 255, blank=True, null=True)
    phone_number    = models.CharField(max_length = 255, blank=True, null=True)
    is_admin        = models.BooleanField(default = False)
    password        = models.CharField(max_length = 255, blank=True, null=True)
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = '1.2. User Account'

    def __str__(self):
        return "%s. %s's account" % (self.id, self.user)

    def __unicode__(self):
        return "%s. %s's account" % (self.id, self.user)


    def check_password(self, password):
        hash_password = bcrypt.hashpw(password.encode(), self.password.encode())
        if self.password.encode() == hash_password:
            return True
        return False


    def update(self, **data):
        email           = data.get('email')
        phone_number    = data.get('phone_number')
        password        = data.get('password')
        image           = data.get('image')

        if email:
            self.email = email
        if phone_number:
            self.phone_number = phone_number
        if image:
            self.image.delete()
            self.image = image
        self.save()

class Sessions(models.Model):
    account         = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    token           = models.CharField(max_length = 255)
    on_session      = models.BooleanField()
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = 'Sessions'
        ordering = ["account", '-created_at']

    def __str__(self):
        return "%s %s | %s" % (self.account.user.first_name, self.account.user.last_name, self.token)

    def __unicode__(self):
        return "%s %s | %s" % (self.account.user.first_name, self.account.user.last_name, self.token)

class Posts(models.Model):
    account         = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    title           = models.CharField(max_length = 255)
    category        = models.CharField(max_length = 255)
    condition       = models.CharField(max_length = 255)
    description     = models.TextField(blank=True, null=True)
    price           = models.CharField(max_length = 255)
    negotiable      = models.BooleanField(default = True)
    city_town       = models.CharField(max_length = 255)
    state           = models.CharField(max_length = 255)
    sold            = models.BooleanField(default = False)
    premium         = models.BooleanField(default = False)
    posted          = models.BooleanField(default = False)

    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = '2.1. Posts'
        ordering = ['-created_at', '-premium']

    def __str__(self):
        return "Post %s by %s" % (self.id, self.account)

    def __unicode__(self):
        return "Post %s by %s" % (self.id, self.account)


    def update(self, data):
        title           = data.get('title')
        category        = data.get('category')
        condition       = data.get('condition')
        description     = data.get('description')
        price           = data.get('price')
        negotiable      = data.get('negotiable')
        city_town       = data.get('city_town')
        state           = data.get('state')

        if title and self.title != title:
            self.title = title

        if category and self.category != category:
            self.category = category

        if condition and self.condition != condition:
            self.condition = condition

        if description and self.description != description:
            self.description = description

        if price and self.price != price:
            self.price = price

        if negotiable is not None and self.negotiable != negotiable:
            self.negotiable = negotiable

        if city_town and self.city_town != city_town:
            self.city_town = city_town

        if state and self.state != state:
            self.state = state

        self.posted = False
        self.save()

    def update_sold(self):
        self.sold = True
        self.save()

class PostPhotos(models.Model):
    post            = models.ForeignKey(Posts, on_delete=models.CASCADE)
    image           = models.FileField(storage=PostPhotosStorage())
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)

    class Meta:
        verbose_name_plural = '2.2. Post Photos'
        ordering = ['-created_at']

    def __str__(self):
        return "%s. Photos by %s" % (self.id, self.post)

    def __unicode__(self):
        return "%s. Photos by %s" % (self.id, self.post)

class UserSavedPosts(models.Model):
    account         = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    post            = models.ForeignKey(Posts, on_delete=models.CASCADE)
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = 'User Saved Posts'
        ordering = ['-created_at']

    def __str__(self):
        return "Saved Post | %s - %s" % (self.account, self.post)

    def __unicode__(self):
        return "Saved Post | %s - %s" % (self.account, self.post)

class UserAccountFollowers(models.Model):
    account         = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='follower')
    following       = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='following')
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)
    class Meta:
        verbose_name_plural = 'User Followers'
        ordering = ['-created_at']

    def __str__(self):
        return "%s is following %s" % (self.account, self.following)

    def __unicode__(self):
        return "%s is following %s" % (self.account, self.following)

class ChatRoom(models.Model):
    room            = models.CharField(max_length=255)
    first           = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='first_user')
    second          = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='second_user')
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)

    class Meta:
        verbose_name_plural = 'Chat room'
        ordering = ['-created_at']

    def __str__(self):
        return "Chat room by %s and %s" % (self.first, self.second)

    def __unicode__(self):
        return "Chat room by %s and %s" % (self.first, self.second)

class Message(models.Model):
    room            = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender          = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='sender')
    message         = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)

    class Meta:
        verbose_name_plural = 'Chat Message'
        ordering = ['created_at']

    def __str__(self):
        return "Message by %s | %s" % (self.sender, self.message)

    def __unicode__(self):
        return "Message by %s | %s" % (self.sender, self.message)

class Review(models.Model):
    reviewer        = models.ForeignKey(UserAccount, related_name='reviewer')
    reviewee        = models.ForeignKey(UserAccount, related_name='reviewee')
    review          = models.TextField()
    rating          = models.IntegerField()
    created_at      = models.DateTimeField(editable=False, auto_now_add = True)
    updated_at      = models.DateTimeField(editable=False, auto_now = True)

    class Meta:
        verbose_name_plural = 'Account Reviews'
        ordering = ['created_at']

    def __str__(self):
        return "%s. %s rated %s as %s" % (
            self.id,
            self.reviewer.user.first_name, 
            self.reviewee.user.first_name,
            self.rating
        )

    def __str__(self):
        return "%s. %s rated %s as %s" % (
            self.id,
            self.reviewer.user.first_name, 
            self.reviewee.user.first_name,
            self.rating
        )
