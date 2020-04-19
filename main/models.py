from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django_comments.moderation import CommentModerator
from django_comments_xtd.moderation import moderator, SpamModerator
from main.badwords import badwords


class TutorialCategory(models.Model):
	tutorial_category = models.CharField(max_length=200)
	category_summary = models.CharField(max_length=200)
	category_slug = models.CharField(max_length=200)
	image = models.ImageField(upload_to='photos/%Y/%m/%d')
	class Meta:
		verbose_name_plural = "Categories"

	def __str__(self):
		return self.tutorial_category


class TutorialSeries(models.Model):
	tutorial_series = models.CharField(max_length=200)
	tutorial_category = models.ForeignKey(TutorialCategory, default=1, verbose_name="Category", on_delete=models.SET_DEFAULT)
	series_summary = models.CharField(max_length=200)
	series_image = models.ImageField(upload_to='photos/%Y/%m/%d')

	class Meta:
		verbose_name_plural = "Series"

	def __str__(self):
		return self.tutorial_series


# Create your models here.
class Tutorial(models.Model):
	tutorial_title = models.CharField(max_length=200)
	tutorial_content = models.TextField()
	tutorial_published = models.DateTimeField("date published", default=datetime.now())
	tutorial_series = models.ForeignKey(TutorialSeries, default=1, verbose_name="Series", on_delete=models.SET_DEFAULT)
	tutorial_slug = models.CharField(max_length=200, default=1)
	
	def __str__(self):
		return self.tutorial_title



class PostCommentModerator(XtdCommentModerator):
        email_notification = True
        removal_suggestion_notification = True


        def moderate(self, comment, content_object, request):
            # Make a dictionary where the keys are the words of the message and
            # the values are their relative position in the message.
            def clean(word):
                ret = word
                if word.startswith('.') or word.startswith(','):
                    ret = word[1:]
                if word.endswith('.') or word.endswith(','):
                    ret = word[:-1]
                return ret

            lowcase_comment = comment.comment.lower()
            msg = dict([(clean(w), i)
                        for i, w in enumerate(lowcase_comment.split())])
            for badword in badwords:
                if isinstance(badword, str):
                    if lowcase_comment.find(badword) > -1:
                        return True
                else:
                    lastindex = -1
                    for subword in badword:
                        if subword in msg:
                            if lastindex > -1:
                                if msg[subword] == (lastindex + 1):
                                    lastindex = msg[subword]
                            else:
                                lastindex = msg[subword]
                        else:
                            break
                    if msg.get(badword[-1]) and msg[badword[-1]] == lastindex:
                        return True
            return super(PostCommentModerator, self).moderate(comment,
                                                              content_object,
                                                              request)

moderator.register(Tutorial, PostCommentModerator)
	
