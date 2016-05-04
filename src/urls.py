import os.path
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth import *
from django.contrib.auth.views import logout
from forum.views import index
from forum import views as app
from forum.feed import RssLastestQuestionsFeed
from django.views.generic.simple import redirect_to
from settings import MXID_URL
from forum.login_views import login_redirect

admin.autodiscover()
feeds = {
    'rss': RssLastestQuestionsFeed
}

APP_PATH = os.path.dirname(__file__)
urlpatterns = patterns('',
    (r'^$', index),
    (r'^sso/([-a-z0-9]+)/(.*)$', 'forum.login_views.mxid_login'),
    (r'^error$', 'forum.views.error'),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/content/images/favicon.ico'}),
    (r'^favicon\.gif$', 'django.views.generic.simple.redirect_to', {'url': '/content/images/favicon.gif'}),
    (r'^content/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(APP_PATH, 'templates/content').replace('\\','/')}
    ),
    (r'^upfiles/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(APP_PATH, 'templates/upfiles').replace('\\','/')}
    ),
	(r'^accounts/login/$', login_redirect),
    (r'^accounts/logout/$',  logout, {'template_name': 'logout.html'}),
    (r'^accounts/profile/$',  app.profile),
    url(r'^faq/$', app.faq, name='faq'),
    url(r'^answers/(?P<id>\d+)/comments/$', app.answer_comments, name='answer_comments'),
    url(r'^answers/(?P<id>\d+)/edit/$', app.edit_answer, name='edit_answer'),
    url(r'^answers/(?P<id>\d+)/revisions/$', app.answer_revisions, name='answer_revisions'),
    url(r'^questions/$', app.questions, name='questions'),
    url(r'^questions/ask/$', app.ask, name='ask'),
    url(r'^search/$', app.search, name='search'),
    url(r'^questions/unanswered/$', app.unanswered, name='unanswered'),
    url(r'^questions/(?P<id>\d+)/edit/$', app.edit_question, name='edit_question'),
    url(r'^questions/(?P<id>\d+)/close/$', app.close, name='close'),
    url(r'^questions/(?P<id>\d+)/reopen/$', app.reopen, name='reopen'),
    url(r'^questions/(?P<id>\d+)/answer/$', app.answer, name='answer'),
    url(r'^questions/(?P<id>\d+)/vote/$', app.vote, name='vote'),
    url(r'^questions/(?P<id>\d+)/revisions/$', app.question_revisions, name='question_revisions'),
    url(r'^questions/(?P<id>\d+)/comments/$', app.question_comments, name='question_comments'),
    url(r'^questions/(?P<question_id>\d+)/comments/(?P<comment_id>\d+)/delete/$', app.delete_question_comment, name='delete_question_comment'),
    url(r'^answers/(?P<answer_id>\d+)/comments/(?P<comment_id>\d+)/delete/$', app.delete_answer_comment, name='delete_answer_comment'),
    #place general question item in the end of other operations
    url(r'^questions/(?P<id>\d+)//*', app.question, name='question'),
    (r'^tags/$', app.tags),
    (r'^tags/(?P<tag>[^/]+)/$', app.tag),
    (r'^users/$',app.users),
    url(r'^users/(?P<id>\d+)//*', app.user, name='user'),
    url(r'^userview/(?P<openid>.*)', app.user_view, name='user_view'),
    url(r'^badges/$',app.badges, name='badges'),
    url(r'^badges/(?P<id>\d+)//*', app.badge, name='badge'),
    url(r'^messages/markread/$',app.read_message, name='read_message'),
    (r'^admin/(.*)', admin.site.root),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^upload/$', app.upload),
    (r'^user_import/', 'forum.webservices.user_import_service'),
    (r'^user_import/service.wsdl', 'forum.webservices.user_import_service'),
    (r'^user_import2/', 'forum.webservices.user_import_service2'),
    (r'^user_import2/service.wsdl', 'forum.webservices.user_import_service2'),
    (r'^user_points_update/', 'forum.webservices.user_points_update_service'),
    (r'^user_points_update/service.wsdl', 'forum.webservices.user_points_update_service'),
    (r'^addsubscription/$', 'forum.views.add_subscription'),
    (r'^deletesubscription/(?P<id>\d+)/$', 'forum.views.delete_subscription'),
    (r'^questions_feed/([0-9]+)/$', 'forum.views.questions_feed'),
    (r'^users_feed/([0-9]+)/$', 'forum.views.users_feed'),
    (r'^users_csv/$', 'forum.views.csv_users'),
    (r'^questions_csv/$', 'forum.views.csv_questions'),
    (r'^answers_csv/$', 'forum.views.csv_answers'),
    (r'^ideaforum/$', app.open_ideaforum),
)
