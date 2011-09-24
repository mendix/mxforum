# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class QuestionAdmin(admin.ModelAdmin):
    """Question admin class"""

class TagAdmin(admin.ModelAdmin):
    """Tag admin class"""
    
class Answerdmin(admin.ModelAdmin):
    """Answer admin class"""

class CommentAdmin(admin.ModelAdmin):
    """  admin class"""

class VoteAdmin(admin.ModelAdmin):
    """  admin class"""
    
class FlaggedItemAdmin(admin.ModelAdmin):
    """  admin class"""    
    
class FavoriteQuestionAdmin(admin.ModelAdmin):
    """  admin class"""  
    
class BadgeAdmin(admin.ModelAdmin):
    """  admin class"""  

class ModelerVersionAdmin(admin.ModelAdmin):
    """ admin class """
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Answer, Answerdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(FlaggedItem, FlaggedItemAdmin)
admin.site.register(FavoriteQuestion, FavoriteQuestionAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(ModelerVersion, ModelerVersionAdmin)
