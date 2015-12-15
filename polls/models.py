from django.db import models
from django.contrib.auth.models import User, UserManager


class MyModelManager(models.Manager):
    def get_new_queryset(self):
        return super(MyModelManager, self).get_queryset().order_by('-created')

    def get_best_queryset(self):
        return super(MyModelManager, self).get_queryset().order_by('-rating')


class CustomUser(User):
    avatar = models.ImageField()
    objects = UserManager()


class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)
    objects = models.Manager()


class Like(models.Model):
    value = models.IntegerField()
    author = models.ForeignKey(CustomUser)


class Question(models.Model):
    title = models.TextField()
    content = models.TextField()
    created = models.DateTimeField()
    author = models.ForeignKey(CustomUser)
    tags = models.ManyToManyField(Tag)
    rating = models.IntegerField(default=0)
    likes = models.ManyToManyField(Like)

    objects = models.Manager()
    manager = MyModelManager()


class Answer(models.Model):
    created = models.DateTimeField()
    question = models.ForeignKey(Question, null=False)
    content = models.TextField()
    author = models.ForeignKey(CustomUser)
    rating = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)
    likes = models.ManyToManyField(Like)


class Logic:

    @staticmethod
    def get_tag(tag):
        testtag = Tag.objects.filter(title=tag)
        if testtag:
            return Question.manager.get_best_queryset().filter(tags__title__exact=tag)
        else:
            return Question.objects.none()

    @staticmethod
    def get_order(question):
        return question.answer_set.order_by('-rating', '-created')
