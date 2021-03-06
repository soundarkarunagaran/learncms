# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from filebrowser.fields import FileBrowseField

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from concurrency.fields import IntegerVersionField

class Lesson(models.Model):
    PUBLISHED = 'published'
    DRAFT = 'draft'
    LESSON_STATUS_CHOICES = (
        (PUBLISHED,'Published'), # value, label
        (DRAFT, 'Draft'),
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Don't edit this, let it be automatically assigned. Must be unique. If you do edit, you need to edit all lesson-ref slugs referring to this.")
    banner_image = FileBrowseField('Banner Image', max_length=200, directory='banners/', blank=True)
    status = models.CharField(choices=LESSON_STATUS_CHOICES, default=DRAFT, max_length=50)
    reference_blurb = models.CharField(max_length=500, blank=True, help_text="The text which appears when a reference to this lesson is included in some other. Don't use markup.")
    content = models.TextField(blank=True,help_text="The body of the lesson, marked up with web component magic.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, blank=True, related_name='creator')
    updated_by = models.ForeignKey(User, null=True, blank=True, related_name='updater')
    version = IntegerVersionField()

    def get_absolute_url(self):
        return reverse('lesson-detail', args=(self.slug,))

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))


    def __str__(self):
        return self.title


class ZoomingImage(models.Model):
    slug = models.SlugField(unique=True, help_text="You choose. Lowercase letters and numbers and - characters only please.")
    image = models.ImageField(upload_to='zimages',help_text="Upload the full-size version of the image. The system will create the thumbnail.")
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(313, 207)],
                               format='JPEG',
                               options={'quality': 60})

    def get_absolute_url(self):
        return self.image.url


    def __str__(self):
        return self.slug

class CapsuleUnit(models.Model):
    title = models.CharField(max_length=200, help_text="")
    slug = models.SlugField(unique=True, help_text="Don't edit this, let it be automatically assigned. Must be unique.")
    image = FileBrowseField('Image', max_length=200, directory='capsules/', blank=True)
    content = models.TextField(blank=True, help_text="HTML is OK")
    version = IntegerVersionField()

    def __str__(self):
        return self.title

class GeneralImage(models.Model):
    image = FileBrowseField("Media Library File", max_length=200)
    description = models.TextField(blank=True, help_text="Anything that you might want to use to search for this image later.")

    @property
    def filename(self):
        return self.image.filename

    @property
    def url(self):
        return self.image.url

    def __str__(self):
        return self.image.url

class GlossaryTerm(models.Model):
    """(GlossaryTerm description)"""
    lemma = models.CharField(max_length=50, help_text="The canonical form of the word or phrase being defined.")
    definition = models.TextField(help_text="The definition of the term. Don't use markup.")
    # to do: alternate forms? See also? Do we want a page of all the terms?
    def __str__(self):
        return self.lemma

    class Meta:
        ordering = ['lemma']

class Question(models.Model):
    """A simple model for collecting questions from our audience."""
    question = models.TextField(help_text="The question submitted.")
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, help_text="Optionally, an email address of the asker.")
    page = models.CharField(blank=True, max_length=50, help_text="The slug of the lesson page where the question was asked")
    step = models.CharField(blank=True, max_length=100, help_text="As much as possible about where in the page the asker was when asking.")
    step_number = models.IntegerField(null=True)

    @property
    def brief_question(self):
        if self.question:
            if len(self.question) <= 50:
                return self.question
            return self.question[:50] + "…"
        return '[blank question]'

    def __str__(self):
        return self.brief_question
