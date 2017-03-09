# encoding: utf-8
from django.db import models
import pickle


class File(models.Model):
    """This is a small demo using just two fields. The slug field is really not
    necessary, but makes the code simpler. ImageField depends on PIL or
    pillow (where Pillow is easily installable in a virtualenv. If you have
    problems installing pillow, use a more generic FileField instead.
anthony cheung
    """
    file = models.FileField(upload_to="uploads")
    slug = models.SlugField(max_length=50, blank=True)

    def __str__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(File, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(File, self).delete(*args, **kwargs)


