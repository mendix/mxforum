#!/usr/bin/env python
#encoding:utf-8
#-------------------------------------------------------------------------------
# Name:        Syndication feed class for subsribtion
# Purpose:
#
# Author:      Mike
#
# Created:     29/01/2009
# Copyright:   (c) CNPROG.COM 2009
# Licence:     GPL V2
#-------------------------------------------------------------------------------
from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from models import Question
class RssLastestQuestionsFeed(Feed):
    title = u"Mendix Programmer Q & A community - the latest issue of"
    link = u"http://mxforum.mendix.com/questions/"
    description = u"English programmers Q & A community-based programming technology. We do professional and collaborative editing technology can Q & A community."
    #ttl = 10
    #copyright = u'Copyright(c)2009.CNPROG.COM'
    copyright = u'Copyright(c)2009.MENDIX.COM'

    def item_link(self, item):
        return self.link + '%s/' % item.id

    def item_author_name(self, item):
        return item.author.username

    def item_author_link(self, item):
        return item.author.get_profile_url()

    def item_pubdate(self, item):
        return item.added_at

    def items(self, item):
       return Question.objects.filter(deleted=False).order_by('-added_at')[:30]

def main():
    pass

if __name__ == '__main__':
    main()
