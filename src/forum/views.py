﻿# encoding:utf-8
import os.path
import time, datetime, calendar, random, urllib

import shlex

from urllib import quote, unquote
from django.conf import settings
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse,Http404
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.template import RequestContext
from django.utils.html import *
from django.utils import simplejson
from django.core import serializers
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import *
from django.contrib.sites.models import Site

from django.core.exceptions import PermissionDenied

from django.db.models import Q

from utils.html import sanitize_html
from markdown2 import Markdown
#from lxml.html.diff import htmldiff
from forum.diff import textDiff as htmldiff
from forum.forms import *
from forum.models import *
from forum.auth import *
from forum.const import *
from forum.user import *
from forum import auth
from base64 import b64encode
from hashlib import sha256
from settings import MXID_URL, OPENID_PREFIX


# used in index page
INDEX_PAGE_SIZE = 30
INDEX_AWARD_SIZE = 15
INDEX_TAGS_SIZE = 100
# used in tags list
DEFAULT_PAGE_SIZE = 65
# used in questions
QUESTIONS_PAGE_SIZE = 10
# used in users
USERS_PAGE_SIZE = 50
# used in answers
ANSWERS_PAGE_SIZE = 10
markdowner = Markdown(html4tags=True)
question_type = ContentType.objects.get_for_model(Question)
answer_type = ContentType.objects.get_for_model(Answer)
comment_type = ContentType.objects.get_for_model(Comment)
question_revision_type = ContentType.objects.get_for_model(QuestionRevision)
answer_revision_type = ContentType.objects.get_for_model(AnswerRevision)
repute_type =ContentType.objects.get_for_model(Repute)
question_type_id = question_type.id
answer_type_id = answer_type.id
comment_type_id = comment_type.id
question_revision_type_id = question_revision_type.id
answer_revision_type_id = answer_revision_type.id
repute_type_id = repute_type.id
def _get_tags_cache_json():
    tags = Tag.objects.all()
    tags_list = []
    for tag in tags:
        dic = {'n': sanitize_html(tag.name), 'c': tag.used_count }
        tags_list.append(dic)
    tags = simplejson.dumps(tags_list)
    return tags

def index(request):
    view_id = request.GET.get('sort', None)
    view_dic = {
             "latest":"-last_activity_at",
             "hottest":"-answer_count",
             "mostvoted":"-score",
             "trans": "-last_activity_at"
             }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-last_activity_at"
    # group questions by author_id of 28,29
    if view_id == 'trans':
        questions = Question.objects.filter(deleted=False, author__id__in=[28,29]).order_by(orderby)[:INDEX_PAGE_SIZE]
    else:
        questions = Question.objects.filter(deleted=False).order_by(orderby)[:INDEX_PAGE_SIZE]

    questions = questions.select_related('votes', 'flagged_items', 'last_edited_at', 'last_activity_by', 'last_edited_by', 'locked_by', 'author');
    tags = Tag.objects.all().order_by("-id")[:INDEX_TAGS_SIZE]
    MIN = 1
    MAX = 100
    begin = end = 0
    if len(tags) > 0:
        sorted_tags = list(tag.used_count for tag in tags)
        begin = min(sorted_tags)
        end = max(sorted_tags)
    mi = MIN if begin < MIN else begin
    ma = MAX if end > MAX else end
    awards = Award.objects.extra(
        select={'badge_id': 'badge.id', 'badge_name':'badge.name',
                      'badge_description': 'badge.description', 'badge_type': 'badge.type',
					  'user_id': 'auth_user.id', 'user_name': 'auth_user.username', 'real_name' : 'auth_user.real_name'
                      },
        tables=['award', 'badge', 'auth_user'],
        order_by=['-awarded_at'],
        where=['auth_user.id=award.user_id AND badge_id=badge.id'],
    ).values('badge_id', 'badge_name', 'badge_description', 'badge_type', 'user_id', 'user_name', 'real_name')

    return render_to_response('index.html', {
        "questions" : questions,
        "tab_id" : view_id,
        "tags" : tags,
        "max" : ma,
        "min" : mi,
        "awards" : awards[:INDEX_AWARD_SIZE],
        }, context_instance=RequestContext(request))

def faq(request):
    return render_to_response('faq.html', context_instance=RequestContext(request))

def unanswered(request):
    return questions(request, unanswered=True)

def questions(request, tagname=None, unanswered=False):
    """
    List of Questions, Tagged questions, and Unanswered questions.
    """
    # template file
    # "questions.html" or "unanswered.html"
    template_file = "questions.html"
    # Set flag to False by default. If it is equal to True, then need to be saved.
    pagesize_changed = False
    # get pagesize from session, if failed then get default value
    user_page_size = request.session.get("pagesize", QUESTIONS_PAGE_SIZE)
    # set pagesize equal to logon user specified value in database
    if request.user.is_authenticated() and request.user.questions_per_page > 0:
        user_page_size = request.user.questions_per_page

    try:
        page = int(request.GET.get('page', '1'))
        # get new pagesize from UI selection
        pagesize = int(request.GET.get('pagesize', user_page_size))
        if pagesize <> user_page_size:
            pagesize_changed = True

    except ValueError:
        page = 1
        pagesize  = user_page_size

    # save this pagesize to user database
    if pagesize_changed:
        request.session["pagesize"] = pagesize
        if request.user.is_authenticated():
            user = request.user
            user.questions_per_page = pagesize
            user.save()

    view_id = request.GET.get('sort', None)
    view_dic = {"latest":"-added_at", "active":"-last_activity_at", "hottest":"-answer_count", "mostvoted":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "latest"
        orderby = "-added_at"

    # check if request is from tagged questions
    if tagname is not None:
        objects = Question.objects.filter(deleted=False, tags__name = unquote(tagname)).order_by(orderby)
    elif unanswered:
        #check if request is from unanswered questions
        template_file = "unanswered.html"
        #objects = Question.objects.filter( Q(answer_accepted=False) | Q(answers__vote_up_count__gt=1), deleted=False).order_by(orderby)
        objects = Question.objects.filter( Q(answer_accepted=False), deleted=False, closed=False).exclude(answers__vote_up_count__gt=4).order_by(orderby)
    else:
        objects = Question.objects.filter(deleted=False).order_by(orderby)

    # RISK - inner join queries
    objects = objects.select_related();
    objects_list = Paginator(objects, pagesize)
    questions = objects_list.page(page)

    # Get related tags from this page objects
    related_tags = []
    for question in questions.object_list:
        tags = list(question.tags.all())
        for tag in tags:
            if tag not in related_tags:
                related_tags.append(tag)

    return render_to_response(template_file, {
        "questions" : questions,
        "tab_id" : view_id,
        "questions_count" : objects_list.count,
        "tags" : related_tags,
        "searchtag" : tagname,
        "is_unanswered" : unanswered,
        "context" : {
            'is_paginated' : True,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': questions.has_previous(),
            'has_next': questions.has_next(),
            'previous': questions.previous_page_number(),
            'next': questions.next_page_number(),
            'base_url' : request.path + '?sort=%s&' % view_id,
            'pagesize' : pagesize
        }}, context_instance=RequestContext(request))

#TODO: allow anynomus user to ask question by providing email and username.
@login_required
def ask(request):
    if request.method == "POST":
        form = AskForm(request.POST)
        if form.is_valid():
            added_at = datetime.datetime.now()
            html = sanitize_html(markdowner.convert(form.cleaned_data['text']))
            question = Question(
                title            = strip_tags(form.cleaned_data['title']),
                author           = request.user,
                added_at         = added_at,
                last_activity_at = added_at,
                last_activity_by = request.user,
                wiki             = form.cleaned_data['wiki'],
                tagnames         = form.cleaned_data['tags'].strip(),
                html             = html,
                summary          = strip_tags(html)[:120],
                modeler_version  = form.cleaned_data['modeler_version']
            )
            if question.wiki:
                question.last_edited_by = question.author
                question.last_edited_at = added_at
                question.wikified_at = added_at

            question.save()

            # create the first revision
            QuestionRevision.objects.create(
                question   = question,
                revision   = 1,
                title      = question.title,
                author     = request.user,
                revised_at = added_at,
                tagnames   = question.tagnames,
                summary    = CONST['default_version'],
                text       = form.cleaned_data['text']
            )
            
            register_event('QuestionPosted', request, request.user.openid, question.id, '', '', None)

            return HttpResponseRedirect(question.get_absolute_url())

    else:
        form = AskForm()

    tags = _get_tags_cache_json()
	
    return render_to_response('ask.html', {
        'form' : form,
        'tags' : tags,
        }, context_instance=RequestContext(request))

def question(request, id):
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    view_id = request.GET.get('sort', 'votes')
    view_dic = {"latest":"-added_at", "oldest":"added_at", "votes":"-score" }
    try:
        orderby = view_dic[view_id]
    except KeyError:
        view_id = "votes"
        orderby = "-score"

    question = get_object_or_404(Question, id=id)
    if question.deleted and not can_view_deleted_post(request.user, question):
        raise Http404
    answer_form = AnswerForm(question)
    answers = Answer.objects.get_answers_from_question(question, request.user)
    answers = answers.select_related(depth=1)

    favorited = question.has_favorite_by_user(request.user)
    question_vote = question.votes.select_related().filter(user=request.user)
    if question_vote is not None and question_vote.count() > 0:
        question_vote = question_vote[0]

    user_answer_votes = {}
    for answer in answers:
        vote = answer.get_user_vote(request.user)
        if vote is not None and not user_answer_votes.has_key(answer.id):
            vote_value = -1
            if vote.is_upvote():
                vote_value = 1
            user_answer_votes[answer.id] = vote_value


    if answers is not None:
        answers = answers.order_by("-accepted", orderby)
    objects_list = Paginator(answers, ANSWERS_PAGE_SIZE)
    page_objects = objects_list.page(page)
    # update view count
    Question.objects.update_view_count(question)
    
    return render_to_response('question.html', {
        "question" : question,
        "question_vote" : question_vote,
        "question_comment_count":question.comments.count(),
        "answer" : answer_form,
        "answers" : page_objects.object_list,
        "user_answer_votes": user_answer_votes,
        "tags" : question.tags.all(),
        "tab_id" : view_id,
        "favorited" : favorited,
        "similar_questions" : Question.objects.get_similar_questions(question),
        "context" : {
            'is_paginated' : True,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': page_objects.has_previous(),
            'has_next': page_objects.has_next(),
            'previous': page_objects.previous_page_number(),
            'next': page_objects.next_page_number(),
            'base_url' : request.path + '?sort=%s&' % view_id,
            'extend_url' : "#sort-top"
        }
        }, context_instance=RequestContext(request))

@login_required
def close(request, id):
    question = get_object_or_404(Question, id=id)
    if not can_close_question(request.user, question):
        return HttpResponse('Permission denied.')
    if request.method == 'POST':
        form = CloseForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data['reason']
            question.closed = True
            question.closed_by = request.user
            question.closed_at = datetime.datetime.now()
            question.close_reason = reason
            question.save()
        return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = CloseForm()
        return render_to_response('close.html', {
            'form' : form,
            'question' : question,
            }, context_instance=RequestContext(request))

@login_required
def reopen(request, id):
    question = get_object_or_404(Question, id=id)
    # open question
    if not can_reopen_question(request.user, question):
        return HttpResponse('Permission denied.')
    if request.method == 'POST' :
        Question.objects.filter(id=question.id).update(closed=False,
            closed_by=None, closed_at=None, close_reason=None)
        return HttpResponseRedirect(question.get_absolute_url())
    else:
        return render_to_response('reopen.html', {
            'question' : question,
            }, context_instance=RequestContext(request))

@login_required
def edit_question(request, id):
    question = get_object_or_404(Question, id=id)
    if question.deleted and not can_view_deleted_post(request.user, question):
        raise Http404
    if can_edit_post(request.user, question):
        return _edit_question(request, question)
    elif can_retag_questions(request.user):
        return _retag_question(request, question)
    else:
        raise Http404

def _retag_question(request, question):
    if request.method == 'POST':
        form = RetagQuestionForm(question, request.POST)
        if form.is_valid():
            if form.has_changed():
                latest_revision = question.get_latest_revision()
                retagged_at = datetime.datetime.now()
                # Update the Question itself
                Question.objects.filter(id=question.id).update(
                    tagnames         = form.cleaned_data['tags'],
                    last_edited_at   = retagged_at,
                    last_edited_by   = request.user,
                    last_activity_at = retagged_at,
                    last_activity_by = request.user
                )
                # Update the Question's tag associations
                tags_updated = Question.objects.update_tags(question,
                    form.cleaned_data['tags'], request.user)
                # Create a new revision
                QuestionRevision.objects.create(
                    question   = question,
                    title      = latest_revision.title,
                    author     = request.user,
                    revised_at = retagged_at,
                    tagnames   = form.cleaned_data['tags'],
                    summary    = CONST['retagged'],
                    text       = latest_revision.text
                )
                # send tags updated singal
                tags_updated.send(sender=question.__class__, question=question)

            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = RetagQuestionForm(question)
    return render_to_response('question_retag.html', {
        'question': question,
        'form' : form,
        'tags' : _get_tags_cache_json(),
    }, context_instance=RequestContext(request))


def _edit_question(request, question):
    latest_revision = question.get_latest_revision()
    revision_form = None
    if request.method == 'POST':
        if 'select_revision' in request.POST:
            # user has changed revistion number
            revision_form = RevisionForm(question, latest_revision, request.POST)
            if revision_form.is_valid():
                # Replace with those from the selected revision
                form = EditQuestionForm(question,
                    QuestionRevision.objects.get(question=question,
                        revision=revision_form.cleaned_data['revision']))
            else:
                form = EditQuestionForm(question, latest_revision, request.POST)
        else:
            # Always check modifications against the latest revision
            form = EditQuestionForm(question, latest_revision, request.POST)
            if form.is_valid():
                html = sanitize_html(markdowner.convert(form.cleaned_data['text']))
                if form.has_changed():
                    edited_at = datetime.datetime.now()
                    tags_changed = (latest_revision.tagnames !=
                                    form.cleaned_data['tags'])
                    tags_updated = False
                    # Update the Question itself
                    updated_fields = {
                        'title': form.cleaned_data['title'],
                        'last_edited_at': edited_at,
                        'last_edited_by': request.user,
                        'last_activity_at': edited_at,
                        'last_activity_by': request.user,
                        'tagnames': form.cleaned_data['tags'],
                        'summary': strip_tags(html)[:120],
                        'html': html,
                    }

                    # only save when it's checked
                    # because wiki doesn't allow to be edited if last version has been enabled already
                    # and we make sure this in forms.
                    if ('wiki' in form.cleaned_data and
                        form.cleaned_data['wiki']):
                        updated_fields['wiki'] = True
                        updated_fields['wikified_at'] = edited_at

                    Question.objects.filter(
                        id=question.id).update(**updated_fields)
                    # Update the Question's tag associations
                    if tags_changed:
                        tags_updated = Question.objects.update_tags(
                            question, form.cleaned_data['tags'], request.user)
                    # Create a new revision
                    revision = QuestionRevision(
                        question   = question,
                        title      = form.cleaned_data['title'],
                        author     = request.user,
                        revised_at = edited_at,
                        tagnames   = form.cleaned_data['tags'],
                        text       = form.cleaned_data['text'],
                    )
                    if form.cleaned_data['summary']:
                        revision.summary = form.cleaned_data['summary']
                    else:
                        revision.summary = 'No.%s Revision' % latest_revision.revision
                    revision.save()

                return HttpResponseRedirect(question.get_absolute_url())
    else:

        revision_form = RevisionForm(question, latest_revision)
        form = EditQuestionForm(question, latest_revision)
    return render_to_response('question_edit.html', {
        'question': question,
        'revision_form': revision_form,
        'form' : form,
        'tags' : _get_tags_cache_json()
    }, context_instance=RequestContext(request))


@login_required
def edit_answer(request, id):
    answer = get_object_or_404(Answer, id=id)
    if answer.deleted and not can_view_deleted_post(request.user, answer):
        raise Http404
    elif not can_edit_post(request.user, answer):
        raise Http404
    else:
        latest_revision = answer.get_latest_revision()
        if request.method == "POST":
            if 'select_revision' in request.POST:
                # user has changed revistion number
                revision_form = RevisionForm(answer, latest_revision, request.POST)
                if revision_form.is_valid():
                    # Replace with those from the selected revision
                    form = EditAnswerForm(answer,
                        AnswerRevision.objects.get(answer=answer,
                            revision=revision_form.cleaned_data['revision']))
                else:
                    form = EditAnswerForm(answer, latest_revision, request.POST)
            else:
                form = EditAnswerForm(answer, latest_revision, request.POST)
                if form.is_valid():
                    html = sanitize_html(markdowner.convert(form.cleaned_data['text']))
                    if form.has_changed():
                        edited_at = datetime.datetime.now()
                        updated_fields = {
                            'last_edited_at': edited_at,
                            'last_edited_by': request.user,
                            'html': html,
                        }
                        Answer.objects.filter(id=answer.id).update(**updated_fields)

                        revision = AnswerRevision(
                            answer     = answer,
                            author     = request.user,
                            revised_at = edited_at,
                            text       = form.cleaned_data['text']
                        )

                        if form.cleaned_data['summary']:
                            revision.summary = form.cleaned_data['summary']
                        else:
                            revision.summary = 'No.%s Revision' % latest_revision.revision
                        revision.save()

                        answer.question.last_activity_at = edited_at
                        answer.question.last_activity_by = request.user
                        answer.question.save()

                    return HttpResponseRedirect(answer.get_absolute_url())
        else:
            revision_form = RevisionForm(answer, latest_revision)
            form = EditAnswerForm(answer, latest_revision)
        return render_to_response('answer_edit.html', {
        'answer': answer,
        'revision_form': revision_form,
        'form' : form,
    }, context_instance=RequestContext(request))

QUESTION_REVISION_TEMPLATE = ('<h1>%(title)s</h1>\n'
    '<div class="text">%(html)s</div>\n'
    '<div class="tags">%(tags)s</div>')
def question_revisions(request, id):
    post = get_object_or_404(Question, id=id)
    revisions = list(post.revisions.all())
    for i, revision in enumerate(revisions):
        revision.html = QUESTION_REVISION_TEMPLATE % {
            'title': revision.title,
            'html': sanitize_html(markdowner.convert(revision.text)),
            'tags': ' '.join(['<a class="post-tag">%s</a>' % tag
                              for tag in revision.tagnames.split(' ')]),
        }
        if i > 0:
            revisions[i - 1].diff = htmldiff(revision.html,
                                             revisions[i - 1].html)
        else:
            revisions[i - 1].diff = QUESTION_REVISION_TEMPLATE % {
                'title': revisions[0].title,
                'html': sanitize_html(markdowner.convert(revisions[0].text)),
                'tags': ' '.join(['<a class="post-tag">%s</a>' % tag
                                  for tag in revisions[0].tagnames.split(' ')]),
            }
            revisions[i - 1].summary = None
    return render_to_response('revisions_question.html', {
        'post': post,
        'revisions': revisions,
    }, context_instance=RequestContext(request))

ANSWER_REVISION_TEMPLATE = ('<div class="text">%(html)s</div>')
def answer_revisions(request, id):
    post = get_object_or_404(Answer, id=id)
    revisions = list(post.revisions.all())
    for i, revision in enumerate(revisions):
        revision.html = ANSWER_REVISION_TEMPLATE % {
            'html': sanitize_html(markdowner.convert(revision.text))
        }
        if i > 0:
            revisions[i - 1].diff = htmldiff(revision.html,
                                             revisions[i - 1].html)
        else:
            revisions[i - 1].diff = revisions[i-1].text
            revisions[i - 1].summary = None
    return render_to_response('revisions_answer.html', {
        'post': post,
        'revisions': revisions,
    }, context_instance=RequestContext(request))

#TODO: allow anynomus
@login_required
def answer(request, id):
    question = get_object_or_404(Question, id=id)
    if request.method == "POST":
        form = AnswerForm(question, request.POST)
        if form.is_valid():
            update_time = datetime.datetime.now()
            answer = Answer(
                question = question,
                author = request.user,
                added_at = update_time,
                wiki = form.cleaned_data['wiki'],
                html = sanitize_html(markdowner.convert(form.cleaned_data['text'])),
            )
            if answer.wiki:
                answer.last_edited_by = answer.author
                answer.last_edited_at = update_time
                answer.wikified_at = update_time

            answer.save()
            Question.objects.update_answer_count(question)

            question = get_object_or_404(Question, id=id)
            question.last_activity_at = update_time
            question.last_activity_by = request.user
            question.save()

            AnswerRevision.objects.create(
                answer     = answer,
                revision   = 1,
                author     = request.user,
                revised_at = update_time,
                summary    = CONST['default_version'],
                text       = form.cleaned_data['text']
            )
            
            register_event('AnswerPosted', request, request.user.openid, question.id, answer.id, '', None)

    return HttpResponseRedirect(question.get_absolute_url())

def tags(request):
    stag = ""
    is_paginated = True
    sortby = request.GET.get('sort', 'used')
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    if request.method == "GET":
        if sortby == "name":
            objects_list = Paginator(Tag.objects.all().order_by("name"), DEFAULT_PAGE_SIZE)
        else:
            objects_list = Paginator(Tag.objects.all().order_by("-used_count"), DEFAULT_PAGE_SIZE)

    elif request.method == "POST":
        stag = request.POST.get("ipSearchTag").strip()
        #disable paginator for search results
        is_paginated = False
        if stag is not None:
            objects_list = Paginator(Tag.objects.extra(where=['name like %s'], params=['%' + stag + '%'])[:50] , DEFAULT_PAGE_SIZE)

    try:
        tags = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        tags = objects_list.page(objects_list.num_pages)

    return render_to_response('tags.html', {
        "tags" : tags,
        "stag" : stag,
        "tab_id" : sortby,
        "context" : {
            'is_paginated' : is_paginated,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': tags.has_previous(),
            'has_next': tags.has_next(),
            'previous': tags.previous_page_number(),
            'next': tags.next_page_number(),
            'base_url' : '/tags/?sort=%s&' % sortby
        }

        }, context_instance=RequestContext(request))

def tag(request, tag):
    return questions(request, tagname=tag)

def vote(request, id):
    """
    vote_type:
        acceptAnswer : 0,
        questionUpVote : 1,
        questionDownVote : 2,
        favorite : 4,
        answerUpVote: 5,
        answerDownVote:6,
        offensiveQuestion : 7,
        offensiveAnswer:8,
        removeQuestion: 9,
        removeAnswer:10

    accept answer code:
        response_data['allowed'] = -1, Accept his own answer   0, no allowed - Anonymous    1, Allowed - by default
        response_data['success'] =  0, failed                                               1, Success - by default
        response_data['status']  =  0, By default                                           1, Answer has been accepted already(Cancel)

    vote code:
        allowed = -3, Don't have enough votes left
                  -2, Don't have enough reputation score
                  -1, Vote his own post
                   0, no allowed - Anonymous
                   1, Allowed - by default
        status  =  0, By default
                   1, Cancel
                   2, Vote is too old to be canceled

    offensive code:
        allowed = -3, Don't have enough flags left
                  -2, Don't have enough reputation score to do this
                   0, not allowed
                   1, allowed
        status  =  0, by default
                   1, can't do it again
    """
    response_data = {
        "allowed": 1,
        "success": 1,
        "status" : 0,
        "count"  : 0,
        "message" : ''
    }

    def can_vote(vote_score, user):
        if vote_score == 1:
            return can_vote_up(request.user)
        else:
            return can_vote_down(request.user)

    try:
        if not request.user.is_authenticated():
            response_data['allowed'] = 0
            response_data['success'] = 0

        elif request.is_ajax():
            question = get_object_or_404(Question, id=id)
            vote_type = request.POST.get('type')

            #accept answer
            if vote_type == '0':
                answer_id = request.POST.get('postId')
                answer = get_object_or_404(Answer, id=answer_id)
                # make sure question author is current user
                if question.author == request.user:
                    # answer user who is also question author is not allow to accept answer
                    if answer.author == question.author:
                        response_data['success'] = 0
                        response_data['allowed'] = -1
                    # check if answer has been accepted already
                    elif answer.accepted:
                        onAnswerAcceptCanceled(answer, request.user)
                        response_data['status'] = 1
                        
                        register_event('RetractAcceptedAnswer', request.user.openid, question.id, answer.id, '', None)
                        register_event('AcceptedAnswerRemoved', answer.author.openid, question.id, answer.id, '', None)
                    else:
                        # set other answers in this question not accepted first
                        for answer_of_question in Answer.objects.get_answers_from_question(question, request.user):
                            if answer_of_question != answer and answer_of_question.accepted:
                                onAnswerAcceptCanceled(answer_of_question, request.user)

                        #make sure retrieve data again after above author changes, they may have related data
                        answer = get_object_or_404(Answer, id=answer_id)
                        onAnswerAccept(answer, request.user)
                        
                        register_event('MarkedAnswerAsAccepted', request.user.openid, question.id, answer.id, '', None)
                        register_event('MarkAnswerAccepted', answer.author.openid, question.id, answer.id, '', None)
                else:
                    response_data['allowed'] = 0
                    response_data['success'] = 0
            # favorite
            elif vote_type == '4':
                has_favorited = False
                fav_questions = FavoriteQuestion.objects.filter(question=question)
                # if the same question has been favorited before, then delete it
                if fav_questions is not None:
                    for item in fav_questions:
                        if item.user == request.user:
                            item.delete()
                            response_data['status'] = 1
                            response_data['count']  = len(fav_questions) - 1
                            if response_data['count'] < 0:
                                response_data['count'] = 0
                            has_favorited = True
                            register_event('RetractLikedQuestion', request, request.user.openid, question.id, '', '', None)
                            register_event('LikedQuestionRemoved', request, question.author.openid, question.id, '', '', None)
                # if above deletion has not been executed, just insert a new favorite question
                if not has_favorited:
                    new_item = FavoriteQuestion(question=question, user=request.user)
                    new_item.save()
                    response_data['count']  = FavoriteQuestion.objects.filter(question=question).count()
                    register_event('LikedQuestion', request, request.user.openid, question.id, '', '', None)
                    register_event('ReceivedLike', request, question.author.openid, question.id, '', '', None)
                    
                Question.objects.update_favorite_count(question)

            elif vote_type in ['1', '2', '5', '6']:
                post_id = id
                post = question
                vote_score = 1
                answer = None
                if vote_type in ['5', '6']:
                    answer_id = request.POST.get('postId')
                    answer = get_object_or_404(Answer, id=answer_id)
                    post_id = answer_id
                    post = answer
                if vote_type in ['2', '6']:
                    vote_score = -1

                if post.author == request.user:
                    response_data['allowed'] = -1
                elif not can_vote(vote_score, request.user):
                    response_data['allowed'] = -2
                elif post.votes.filter(user=request.user).count() > 0:
                    vote = post.votes.filter(user=request.user)[0]
                    # unvote should be less than certain time
                    if (datetime.datetime.now().day - vote.voted_at.day) >= VOTE_RULES['scope_deny_unvote_days']:
                        response_data['status'] = 2
                    else:
                        voted = vote.vote
                        answerid = ''
                        if answer:
                            answerid = answer.id

                        if voted > 0:
                            # cancel upvote
                            onUpVotedCanceled(vote, post, request.user)
                            register_event('RetractUpvote', request, request.user.openid, question.id, answerid, '', None)
                            register_event('UpvoteRemoved', request, post.author.openid, question.id, answerid, '', None)
                        else:
                            # cancel downvote
                            onDownVotedCanceled(vote, post, request.user)
                            register_event('RetractDownvote', request, request.user.openid, question.id, answerid, '', None)
                            register_event('DownvoteRemoved', request, post.author.openid, question.id, answerid, '', None)
                            
                        response_data['status'] = 1
                        response_data['count'] = post.score
                elif Vote.objects.get_votes_count_today_from_user(request.user) >= VOTE_RULES['scope_votes_per_user_per_day']:
                    response_data['allowed'] = -3
                else:
                    vote = Vote(user=request.user, content_object=post, vote=vote_score, voted_at=datetime.datetime.now())
                    if vote_score > 0:
                        # upvote
                        answerid = ''
                        if answer:
                            answerid = answer.id
                        
                        onUpVoted(vote, post, request.user)
                        
                        register_event('Upvoted', request, request.user.openid, question.id, answerid, '', None)
                        register_event('ReceivedUpvote', request, post.author.openid, question.id, answerid, '', None)
                    else:
                        # downvote
                        onDownVoted(vote, post, request.user)
                        
                        register_event('DownVoted', request, request.user.openid, post.id, '', '', None)
                        register_event('ReceivedDownvote', request, post.author.openid, post.id, '', '', None)

                    votes_left = VOTE_RULES['scope_votes_per_user_per_day'] - Vote.objects.get_votes_count_today_from_user(request.user)
                    if votes_left <= VOTE_RULES['scope_warn_votes_left']:
                        response_data['message'] = u'%s votes left' % votes_left
                    response_data['count'] = post.score
            elif vote_type in ['7', '8']:
                post = question
                post_id = id
                if vote_type == '8':
                    post_id = request.POST.get('postId')
                    post = get_object_or_404(Answer, id=post_id)

                if FlaggedItem.objects.get_flagged_items_count_today(request.user) >= VOTE_RULES['scope_flags_per_user_per_day']:
                    response_data['allowed'] = -3
                elif not can_flag_offensive(request.user):
                    response_data['allowed'] = -2
                elif post.flagged_items.filter(user=request.user).count() > 0:
                    response_data['status'] = 1
                else:
                    item = FlaggedItem(user=request.user, content_object=post, flagged_at=datetime.datetime.now())
                    onFlaggedItem(item, post, request.user)
                    response_data['count'] = post.offensive_flag_count
                    # send signal when question or answer be marked offensive
                    mark_offensive.send(sender=post.__class__, instance=post, mark_by=request.user)
            elif vote_type in ['9', '10']:
                post = question
                post_id = id
                if vote_type == '10':
                    post_id = request.POST.get('postId')
                    post = get_object_or_404(Answer, id=post_id)

                if not can_delete_post(request.user, post):
                    response_data['allowed'] = -2
                elif post.deleted:
                    onDeleteCanceled(post, request.user)
                    response_data['status'] = 1
                else:
                    onDeleted(post, request.user)
                    delete_post_or_answer.send(sender=post.__class__, instance=post, delete_by=request.user)
                Question.objects.update_answer_count(question)
        else:
            response_data['success'] = 0
            response_data['message'] = u'Request mode is not supported. Please try again.'

        data = simplejson.dumps(response_data)

    except Exception, e:
        response_data['message'] = str(e)
        data = simplejson.dumps(response_data)
    return HttpResponse(data, mimetype="application/json")

def users(request):
    is_paginated = True
    sortby = request.GET.get('sort', 'reputation')
    suser = request.REQUEST.get('name',  "")
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    if suser == "":
        if sortby == "newest":
	    objects_list = Paginator(User.objects.all().order_by('-date_joined')[:70], USERS_PAGE_SIZE)
        elif sortby == "last":
	    objects_list = Paginator(User.objects.all().order_by('date_joined')[:70], USERS_PAGE_SIZE)
        elif sortby == "user":
	    objects_list = Paginator(User.objects.all().order_by('username')[:70], USERS_PAGE_SIZE)
	elif sortby == "all":
	    objects_list = Paginator(User.objects.all().order_by('-reputation'), USERS_PAGE_SIZE)
        # default
        else:
	    objects_list = Paginator(User.objects.all().order_by('-reputation')[:70], USERS_PAGE_SIZE)
        base_url = '/users/?sort=%s&' % sortby
    else:
        sortby = "reputation"
        objects_list = Paginator(User.objects.extra(where=['username like %s'], params=['%' + suser + '%']).order_by('-reputation'), USERS_PAGE_SIZE)
        base_url = '/users/?name=%s&sort=%s&' % (suser, sortby)

    try:
        users = objects_list.page(page)
    except (EmptyPage, InvalidPage):
        users = objects_list.page(objects_list.num_pages)

    return render_to_response('users.html', {
        "users" : users,
        "suser" : suser,
        "tab_id" : sortby,
        "context" : {
            'is_paginated' : False,
            'pages': objects_list.num_pages,
            'page': page,
            'has_previous': users.has_previous(),
            'has_next': users.has_next(),
            'previous': users.previous_page_number(),
            'next': users.next_page_number(),
            'base_url' : base_url
        }

        }, context_instance=RequestContext(request))

def user(request, id):
    sort = request.GET.get('sort', 'stats')
    user_view = dict((v.id, v) for v in USER_TEMPLATE_VIEWS).get(sort, USER_TEMPLATE_VIEWS[0])
    from forum import views
    func = getattr(views, user_view.view_name)
    return func(request, id, user_view, "user.html")
    
def user_view(request, openid):
    sort = request.GET.get('sort', 'stats')
    user_view = dict((v.id, v) for v in USER_TEMPLATE_VIEWS).get(sort, USER_TEMPLATE_VIEWS[0])
    from forum import views
    func = getattr(views, user_view.view_name)
    
    decoded_openid = urllib.unquote(openid).decode('utf8')
    if not decoded_openid.startswith("https"):
        decoded_openid = OPENID_PREFIX + decoded_openid
        
    if decoded_openid.endswith("/"):
        decoded_openid = decoded_openid[:-1]
    
    user = get_object_or_404(User, openid=decoded_openid)
    return func(request, user.id, user_view, "user_plain.html")

def user_stats(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    
    offset = 0
    if request.GET.has_key('page'):
        offset = 100*int(request.GET['page'])

    questions = Question.objects.extra(
        select={
            'favorited_myself' : 'SELECT count(*) FROM favorite_question f WHERE f.user_id = %s AND f.question_id = question.id',
            'la_user_id' : 'auth_user.id',
            'la_username' : 'auth_user.username',
            'la_user_gold' : 'auth_user.gold',
            'la_user_silver' : 'auth_user.silver',
            'la_user_bronze' : 'auth_user.bronze',
            'la_user_reputation' : 'auth_user.reputation',
            'la_real_name' : 'auth_user.real_name'
            },
        select_params=[user_id],
        tables=['question', 'auth_user'],
        where=['question.deleted = 0 AND question.author_id=%s AND question.last_activity_by_id = auth_user.id'],
        params=[user_id],
    ).values('favorited_myself',
             'id',
             'title',
             'author_id',
             'added_at',
             'answer_accepted',
             'answer_count',
             'comment_count',
             'view_count',
             'favourite_count',
             'summary',
             'tagnames',
             'vote_up_count',
             'vote_down_count',
             'last_activity_at',
             'la_user_id',
             'la_username',
             'la_user_gold',
             'la_user_silver',
             'la_user_bronze',
             'la_user_reputation',
             'la_real_name')[:100]

    for question in questions:
        question['vote_count'] = question['vote_up_count'] - question['vote_down_count']
    questions = sorted(questions, key = lambda k : k['vote_count'], reverse=True)

    answered_questions = Question.objects.extra(
        select={
            'vote_up_count' : 'answer.vote_up_count',
            'vote_down_count' : 'answer.vote_down_count',
            'answer_id' : 'answer.id',
            'accepted' : 'answer.accepted',
            'comment_count' : 'answer.comment_count'
            },
        tables=['question', 'answer'],
        where=['answer.deleted=0 AND answer.author_id=%s AND answer.question_id=question.id'],
        params=[user_id],
        select_params=[user_id]
    ).distinct().values('comment_count',
                        'id',
                        'answer_id',
                        'title',
                        'author_id',
                        'accepted',
                        'answer_count',
                        'vote_up_count',
                        'vote_down_count')[offset:(offset+100)]

    for answered_question in answered_questions:
        answered_question['vote_count'] = answered_question['vote_up_count'] - answered_question['vote_down_count']
    answered_questions = sorted(answered_questions, key = lambda k : k['vote_count'], reverse=True)

    answered_questions_count = Answer.objects.filter(deleted=False, author=user_id).count()
    up_votes = Vote.objects.get_up_vote_count_from_user(user)
    down_votes = Vote.objects.get_down_vote_count_from_user(user)
    votes_today = Vote.objects.get_votes_count_today_from_user(user)
    votes_total = VOTE_RULES['scope_votes_per_user_per_day']
    tags = user.created_tags.all().order_by('-used_count')[:50]

    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
        "questions" : questions,
        "answered_questions" : answered_questions,
        "up_votes" : up_votes,
        "down_votes" : down_votes,
        "total_votes": up_votes + down_votes,
        "votes_today_left": votes_total-votes_today,
        "votes_total_per_day": votes_total,
        "tags" : tags,
        "answered_questions_count" : answered_questions_count,
        "next_page" : offset/100+1,
    }, context_instance=RequestContext(request))

def user_recent(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    def get_type_name(type_id):
        for item in TYPE_ACTIVITY:
            if type_id in item:
                return item[1]

    class Event:
        def __init__(self, time, type, title, summary, answer_id, question_id):
            self.time = time
            self.type = get_type_name(type)
            self.type_id = type
            self.title = title
            self.summary = summary
            self.title_link = u'/questions/%s/%s#%s' %(question_id, title, answer_id)\
                if int(answer_id) > 0 else u'/questions/%s/%s' %(question_id, title)
    class AwardEvent:
        def __init__(self, time, type, id):
            self.time = time
            self.type = get_type_name(type)
            self.type_id = type
            self.badge = get_object_or_404(Badge, id=id)

    activities = []
    # ask questions
    questions = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'active_at' : 'activity.active_at',
            'activity_type' : 'activity.activity_type'
            },
        tables=['activity', 'question'],
        where=['activity.content_type_id = %s AND activity.object_id = question.id AND \
            activity.user_id = %s AND activity.activity_type = %s'],
        params=[question_type_id, user_id, TYPE_ACTIVITY_ASK_QUESTION],
        order_by=['-activity.active_at']
    ).values(
            'title',
            'question_id',
            'active_at',
            'activity_type'
            )
    if len(questions) > 0:
        questions = [(Event(q['active_at'], q['activity_type'], q['title'], '', '0', \
            q['question_id'])) for q in questions]
        activities.extend(questions)

    # answers
    answers = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'active_at' : 'activity.active_at',
            'activity_type' : 'activity.activity_type'
            },
        tables=['activity', 'answer', 'question'],
        where=['activity.content_type_id = %s AND activity.object_id = answer.id AND \
            answer.question_id=question.id AND activity.user_id=%s AND activity.activity_type=%s'],
        params=[answer_type_id, user_id, TYPE_ACTIVITY_ANSWER],
        order_by=['-activity.active_at']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'active_at',
            'activity_type'
            )
    if len(answers) > 0:
        answers = [(Event(q['active_at'], q['activity_type'], q['title'], '', q['answer_id'], \
            q['question_id'])) for q in answers]
        activities.extend(answers)

    # question comments
    comments = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'comment.object_id',
            'added_at' : 'comment.added_at',
            'activity_type' : 'activity.activity_type'
            },
        tables=['activity', 'question', 'comment'],

        where=['activity.content_type_id = %s AND activity.object_id = comment.id AND \
            activity.user_id = comment.user_id AND comment.object_id=question.id AND \
            comment.content_type_id=%s AND activity.user_id = %s AND activity.activity_type=%s'],
        params=[comment_type_id, question_type_id, user_id, TYPE_ACTIVITY_COMMENT_QUESTION],
        order_by=['-comment.added_at']
    ).values(
            'title',
            'question_id',
            'added_at',
            'activity_type'
            )

    if len(comments) > 0:
        comments = [(Event(q['added_at'], q['activity_type'], q['title'], '', '0', \
            q['question_id'])) for q in comments]
        activities.extend(comments)

    # answer comments
    comments = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'added_at' : 'comment.added_at',
            'activity_type' : 'activity.activity_type'
            },
        tables=['activity', 'question', 'answer', 'comment'],

        where=['activity.content_type_id = %s AND activity.object_id = comment.id AND \
            activity.user_id = comment.user_id AND comment.object_id=answer.id AND \
            comment.content_type_id=%s AND question.id = answer.question_id AND \
            activity.user_id = %s AND activity.activity_type=%s'],
        params=[comment_type_id, answer_type_id, user_id, TYPE_ACTIVITY_COMMENT_ANSWER],
        order_by=['-comment.added_at']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'added_at',
            'activity_type'
            )

    if len(comments) > 0:
        comments = [(Event(q['added_at'], q['activity_type'], q['title'], '', q['answer_id'], \
            q['question_id'])) for q in comments]
        activities.extend(comments)

    # question revisions
    revisions = Activity.objects.extra(
        select={
            'title' : 'question_revision.title',
            'question_id' : 'question_revision.question_id',
            'added_at' : 'activity.active_at',
            'activity_type' : 'activity.activity_type',
            'summary' : 'question_revision.summary'
            },
        tables=['activity', 'question_revision'],
        where=['activity.content_type_id = %s AND activity.object_id = question_revision.id AND \
            activity.user_id = question_revision.author_id AND activity.user_id = %s AND \
            activity.activity_type=%s'],
        params=[question_revision_type_id, user_id, TYPE_ACTIVITY_UPDATE_QUESTION],
        order_by=['-activity.active_at']
    ).values(
            'title',
            'question_id',
            'added_at',
            'activity_type',
            'summary'
            )

    if len(revisions) > 0:
        revisions = [(Event(q['added_at'], q['activity_type'], q['title'], q['summary'], '0', \
            q['question_id'])) for q in revisions]
        activities.extend(revisions)

    # answer revisions
    revisions = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'added_at' : 'activity.active_at',
            'activity_type' : 'activity.activity_type',
            'summary' : 'answer_revision.summary'
            },
        tables=['activity', 'answer_revision', 'question', 'answer'],

        where=['activity.content_type_id = %s AND activity.object_id = answer_revision.id AND \
            activity.user_id = answer_revision.author_id AND activity.user_id = %s AND \
            answer_revision.answer_id=answer.id AND answer.question_id = question.id AND \
            activity.activity_type=%s'],
        params=[answer_revision_type_id, user_id, TYPE_ACTIVITY_UPDATE_ANSWER],
        order_by=['-activity.active_at']
    ).values(
            'title',
            'question_id',
            'added_at',
            'answer_id',
            'activity_type',
            'summary'
            )

    if len(revisions) > 0:
        revisions = [(Event(q['added_at'], q['activity_type'], q['title'], q['summary'], \
            q['answer_id'], q['question_id'])) for q in revisions]
        activities.extend(revisions)

    # accepted answers
    accept_answers = Activity.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'added_at' : 'activity.active_at',
            'activity_type' : 'activity.activity_type',
            },
        tables=['activity', 'answer', 'question'],
        where=['activity.content_type_id = %s AND activity.object_id = answer.id AND \
            activity.user_id = question.author_id AND activity.user_id = %s AND \
            answer.question_id=question.id AND activity.activity_type=%s'],
        params=[answer_type_id, user_id, TYPE_ACTIVITY_MARK_ANSWER],
        order_by=['-activity.active_at']
    ).values(
            'title',
            'question_id',
            'added_at',
            'activity_type',
            )
    if len(accept_answers) > 0:
        accept_answers = [(Event(q['added_at'], q['activity_type'], q['title'], '', '0', \
            q['question_id'])) for q in accept_answers]
        activities.extend(accept_answers)
    #award history
    awards = Activity.objects.extra(
        select={
            'badge_id' : 'badge.id',
            'awarded_at': 'award.awarded_at',
            'activity_type' : 'activity.activity_type'
            },
        tables=['activity', 'award', 'badge'],
        where=['activity.user_id = award.user_id AND activity.user_id = %s AND \
            award.badge_id=badge.id AND activity.object_id=award.id AND activity.activity_type=%s'],
        params=[user_id, TYPE_ACTIVITY_PRIZE],
        order_by=['-activity.active_at']
    ).values(
            'badge_id',
            'awarded_at',
            'activity_type'
            )
    if len(awards) > 0:
        awards = [(AwardEvent(q['awarded_at'], q['activity_type'], q['badge_id'])) for q in awards]
        activities.extend(awards)

    activities.sort(lambda x,y: cmp(y.time, x.time))

    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
        "activities" : activities[:user_view.data_size]
    }, context_instance=RequestContext(request))

def user_responses(request, user_id, user_view, usertemplate):
    """
    We list answers for question, comments, and answer accepted by others for this user.
    """
    class Response:
        def __init__(self, type, title, question_id, answer_id, time, username, user_id, content):
            self.type = type
            self.title = title
            self.titlelink = u'/questions/%s/%s#%s' % (question_id, title, answer_id)
            self.time = time
            self.userlink = u'/users/%s/' % (user_id)
            self.username = username
            self.content = u'%s ...' % strip_tags(content)[:300]

        def __unicode__(self):
            return u'%s %s' % (self.type, self.titlelink)

    user = get_object_or_404(User, id=user_id)
    responses = []
    answers = Answer.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'added_at' : 'answer.added_at',
            'html' : 'answer.html',
            'username' : 'auth_user.username',
            'user_id' : 'auth_user.id'
            },
        select_params=[user_id],
        tables=['answer', 'question', 'auth_user'],
        where=['answer.question_id = question.id AND answer.deleted=0 AND question.deleted = 0 AND \
            question.author_id = %s AND answer.author_id <> %s AND answer.author_id=auth_user.id'],
        params=[user_id, user_id],
        order_by=['-answer.id']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'added_at',
            'html',
            'username',
            'user_id'
            )
    if len(answers) > 0:
        answers = [(Response(TYPE_RESPONSE['QUESTION_ANSWERED'], a['title'], a['question_id'],
        a['answer_id'], a['added_at'], a['username'], a['user_id'], a['html'])) for a in answers]
        responses.extend(answers)


    # question comments
    comments = Comment.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'comment.object_id',
            'added_at' : 'comment.added_at',
            'comment' : 'comment.comment',
            'username' : 'auth_user.username',
            'user_id' : 'auth_user.id'
            },
        tables=['question', 'auth_user', 'comment'],
        where=['question.deleted = 0 AND question.author_id = %s AND comment.object_id=question.id AND \
            comment.content_type_id=%s AND comment.user_id <> %s AND comment.user_id = auth_user.id'],
        params=[user_id, question_type_id, user_id],
        order_by=['-comment.added_at']
    ).values(
            'title',
            'question_id',
            'added_at',
            'comment',
            'username',
            'user_id'
            )

    if len(comments) > 0:
        comments = [(Response(TYPE_RESPONSE['QUESTION_COMMENTED'], c['title'], c['question_id'],
            '', c['added_at'], c['username'], c['user_id'], c['comment'])) for c in comments]
        responses.extend(comments)

    # answer comments
    comments = Comment.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'added_at' : 'comment.added_at',
            'comment' : 'comment.comment',
            'username' : 'auth_user.username',
            'user_id' : 'auth_user.id'
            },
        tables=['answer', 'auth_user', 'comment', 'question'],
        where=['answer.deleted = 0 AND answer.author_id = %s AND comment.object_id=answer.id AND \
            comment.content_type_id=%s AND comment.user_id <> %s AND comment.user_id = auth_user.id \
            AND question.id = answer.question_id'],
        params=[user_id, answer_type_id, user_id],
        order_by=['-comment.added_at']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'added_at',
            'comment',
            'username',
            'user_id'
            )

    if len(comments) > 0:
        comments = [(Response(TYPE_RESPONSE['ANSWER_COMMENTED'], c['title'], c['question_id'],
        c['answer_id'], c['added_at'], c['username'], c['user_id'], c['comment'])) for c in comments]
        responses.extend(comments)

    # answer has been accepted
    answers = Answer.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'added_at' : 'answer.accepted_at',
            'html' : 'answer.html',
            'username' : 'auth_user.username',
            'user_id' : 'auth_user.id'
            },
        select_params=[user_id],
        tables=['answer', 'question', 'auth_user'],
        where=['answer.question_id = question.id AND answer.deleted=0 AND question.deleted = 0 AND \
            answer.author_id = %s AND answer.accepted=1 AND question.author_id=auth_user.id'],
        params=[user_id],
        order_by=['-answer.id']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'added_at',
            'html',
            'username',
            'user_id'
            )
    if len(answers) > 0:
        answers = [(Response(TYPE_RESPONSE['ANSWER_ACCEPTED'], a['title'], a['question_id'],
            a['answer_id'], a['added_at'], a['username'], a['user_id'], a['html'])) for a in answers]
        responses.extend(answers)

    # sort posts by time
    responses.sort(lambda x,y: cmp(y.time, x.time))

    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
        "responses" : responses[:user_view.data_size],

    }, context_instance=RequestContext(request))

def user_votes(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    if not can_view_user_votes(request.user, user):
        raise Http404
    votes = []
    question_votes = Vote.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 0,
            'voted_at' : 'vote.voted_at',
            'vote' : 'vote',
            },
        select_params=[user_id],
        tables=['vote', 'question', 'auth_user'],
        where=['vote.content_type_id = %s AND vote.user_id = %s AND vote.object_id = question.id AND vote.user_id=auth_user.id'],
        params=[question_type_id, user_id],
        order_by=['-vote.id']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'voted_at',
            'vote',
            )
    if(len(question_votes) > 0):
        votes.extend(question_votes)

    answer_votes = Vote.objects.extra(
        select={
            'title' : 'question.title',
            'question_id' : 'question.id',
            'answer_id' : 'answer.id',
            'voted_at' : 'vote.voted_at',
            'vote' : 'vote',
            },
        select_params=[user_id],
        tables=['vote', 'answer', 'question', 'auth_user'],
        where=['vote.content_type_id = %s AND vote.user_id = %s AND vote.object_id = answer.id AND answer.question_id = question.id AND vote.user_id=auth_user.id'],
        params=[answer_type_id, user_id],
        order_by=['-vote.id']
    ).values(
            'title',
            'question_id',
            'answer_id',
            'voted_at',
            'vote',
            )
    if(len(answer_votes) > 0):
        votes.extend(answer_votes)
    votes.sort(lambda x,y: cmp(y['voted_at'], x['voted_at']))
    
    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
        "votes" : votes[:user_view.data_size]

    }, context_instance=RequestContext(request))

def user_reputation(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    reputation = Repute.objects.extra(
        select={'positive': 'sum(positive)', 'negative': 'sum(negative)', 'question_id':'question_id', 'title': 'question.title'},
        tables=['repute', 'question'],
        order_by=['-reputed_at'],
        where=['user_id=%s AND question_id=question.id'],
        params=[user.id]
    ).values('positive', 'negative', 'question_id', 'title', 'reputed_at', 'reputation')

    reputation.query.group_by = ['question_id']

    rep_list = []
    for rep in Repute.objects.filter(user=user).order_by('reputed_at'):
        dic = '[%s,%s]' % (calendar.timegm(rep.reputed_at.timetuple()) * 1000, rep.reputation)
        rep_list.append(dic)
    reps = ','.join(rep_list)
    reps = '[%s]' % reps

    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
        "reputation" : reputation,
        "reps" : reps
    }, context_instance=RequestContext(request))

def user_favorites(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    questions = Question.objects.extra(
        select={
            'favorited_myself' : 'SELECT count(*) FROM favorite_question f WHERE f.user_id = %s AND f.question_id = question.id',
            'la_user_id' : 'auth_user.id',
            'la_username' : 'auth_user.username',
            'la_user_gold' : 'auth_user.gold',
            'la_user_silver' : 'auth_user.silver',
            'la_user_bronze' : 'auth_user.bronze',
            'la_user_reputation' : 'auth_user.reputation',
            'la_real_name' : 'auth_user.real_name'
            },
        select_params=[user_id],
        tables=['question', 'auth_user', 'favorite_question'],
        where=['question.deleted = 0 AND question.last_activity_by_id = auth_user.id AND favorite_question.question_id = question.id AND favorite_question.user_id = %s'],
        params=[user_id],
        order_by=['-question.id']
    ).values('favorited_myself',
             'id',
             'title',
             'author_id',
             'added_at',
             'answer_accepted',
             'answer_count',
             'comment_count',
             'view_count',
             'favourite_count',
             'summary',
             'tagnames',
             'vote_up_count',
             'vote_down_count',
             'last_activity_at',
             'la_user_id',
             'la_username',
             'la_user_gold',
             'la_user_silver',
             'la_user_bronze',
             'la_user_reputation',
             'la_real_name')
             
    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "user_template" : usertemplate,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "questions" : questions[:user_view.data_size],
        "view_user" : user
    }, context_instance=RequestContext(request))


def user_preferences(request, user_id, user_view, usertemplate):
    user = get_object_or_404(User, id=user_id)
    return render_to_response(user_view.template_file,{
        "tab_name" : user_view.id,
        "tab_description" : user_view.tab_description,
        "page_title" : user_view.page_title,
        "view_user" : user,
    }, context_instance=RequestContext(request))

def user_subscriptions(request, user_id, user_view, usertemplate):
    """
    user_view is provided as legacy param to work with old b0rked cnprog code
    """
    user = get_object_or_404(User, id=user_id)
    subscriptions = Subscription.objects.filter(user=user)
    return render_to_response('user_subscriptions.html',{
        "tab_name" : "subscriptions",
        "tab_description" : "Manage your subscriptions",
        "page_title" : "Subscriptions",
        "view_user" : user,
        "subscriptions" : subscriptions,
    }, context_instance = RequestContext(request))

def question_comments(request, id):
    question = get_object_or_404(Question, id=id)
    user = request.user
    if request.method == "POST":
        question.last_activity_at =  datetime.datetime.now()
        question.last_activity_by = request.user
        question.save()
    return __comments(request, question, 'question', user)

def answer_comments(request, id):
    answer = get_object_or_404(Answer, id=id)
    if request.method == "POST":
        answer.question.last_activity_at =  datetime.datetime.now()
        answer.question.last_activity_by = request.user
        answer.question.save() 
    user = request.user
    return __comments(request, answer, 'answer', user)

def __comments(request, obj, type, user):
    # only support get comments by ajax now
    if request.is_ajax():
        if request.method == "GET":
            return __generate_comments_json(obj, type, user)
        elif request.method == "POST":
            comment_data = request.POST.get('comment')
            comment = Comment(content_object=obj, comment=comment_data, user=request.user)
            comment.save()
            if (comment.content_type_id == ContentType.objects.get_for_model(Question).id):
                register_event('CommentPosted', request, request.user.openid, comment.object_id, '', '', None)
            else:
                answer = get_object_or_404(Answer, id=comment.object_id)
                register_event('CommentPosted', request, request.user.openid, answer.question.id , answer.id, '', None)
            
            obj.comment_count = obj.comment_count + 1
            obj.save()
            return __generate_comments_json(obj, type, user)

def __generate_comments_json(obj, type, user):
    comments = obj.comments.all().order_by('added_at')
    # {"Id":6,"PostId":38589,"CreationDate":"an hour ago","Text":"hello there!","UserDisplayName":"Jarrod Dixon","UserUrl":"/users/3/jarrod-dixon","DeleteUrl":null}
    json_comments = []
    for comment in comments:
        comment_user = comment.user
        delete_url = ""
        if user != None and auth.can_delete_comment(user, comment):
            #/posts/392845/comments/219852/delete
            delete_url = "/" + type + "s/%s/comments/%s/delete/" % (obj.id, comment.id)
        json_comments.append({"id" : comment.id,
            "object_id" : obj.id,
            "add_date" : comment.added_at.strftime('%Y-%m-%d'),
            "text" : sanitize_html(comment.comment),
            "user_display_name" : sanitize_html(comment_user.real_name),
            "user_url" : sanitize_html("/users/%s/%s" % (comment_user.id, comment_user.real_name)),
            "delete_url" : sanitize_html(delete_url)
        })

    data = simplejson.dumps(json_comments)
    return HttpResponse(data, mimetype="application/json")

def delete_question_comment(request, question_id, comment_id):
    if request.is_ajax():
        question = get_object_or_404(Question, id=question_id)
        comment = get_object_or_404(Comment, id=comment_id)

        question.comments.remove(comment)
        question.comment_count = question.comment_count - 1
        question.save()
        
        register_event('CommentRemoved', request, request.user.openid, question.id, '', '', None)
        
        user = request.user
        return __generate_comments_json(question, 'question', user)

def delete_answer_comment(request, answer_id, comment_id):
    if request.is_ajax():
        answer = get_object_or_404(Answer, id=answer_id)
        comment = get_object_or_404(Comment, id=comment_id)

        answer.comments.remove(comment)
        answer.comment_count = answer.comment_count - 1
        answer.save()
        
        register_event('CommentRemoved', request, request.user.openid, answer.question.id, answer.id, '', None)
        
        user = request.user
        return __generate_comments_json(answer, 'answer', user)

def profile(request):
    return render_to_response('profile.html', {
        'next' : '/',
    }, context_instance=RequestContext(request))

def badges(request):
    badges = Badge.objects.all().order_by('type')
    my_badges = []
    if request.user.is_authenticated():
        my_badges = Award.objects.filter(user=request.user)
        my_badges.query.group_by = ['badge_id']

    return render_to_response('badges.html', {
        'badges' : badges,
        'mybadges' : my_badges,
    }, context_instance=RequestContext(request))

def badge(request, id):
    badge = get_object_or_404(Badge, id=id)
    awards = Award.objects.extra(
        select={'id': 'auth_user.id', 'name': 'auth_user.real_name', 'rep':'auth_user.reputation', 'gold': 'auth_user.gold', 'silver': 'auth_user.silver', 'bronze': 'auth_user.bronze'},
        tables=['award', 'auth_user'],
        where=['badge_id=%s AND user_id=auth_user.id'],
        params=[id]
    ).values('id').distinct()

    return render_to_response('badge.html', {
        'awards' : awards,
        'badge' : badge,
    }, context_instance=RequestContext(request))

def read_message(request):
    if request.method == "POST":
        if request.POST['formdata'] == 'required':
            request.session['message_silent'] = 1

            if request.user.is_authenticated():
                request.user.delete_messages()
    return HttpResponse('')

def upload(request):
    class FileTypeNotAllow(Exception):
        pass
    class FileSizeNotAllow(Exception):
        pass
    class UploadPermissionNotAuthorized(Exception):
        pass

    #<result><msg><![CDATA[%s]]></msg><error><![CDATA[%s]]></error><file_url>%s</file_url></result>
    xml_template = "<result><msg><![CDATA[%s]]></msg><error><![CDATA[%s]]></error><file_url>%s</file_url></result>"

    try:
        f = request.FILES['file-upload']
        # check upload permission
        if not can_upload_files(request.user):
            raise UploadPermissionNotAuthorized

        # check file type
        file_name_suffix = os.path.splitext(f.name)[1].lower()
        if not file_name_suffix in settings.ALLOW_FILE_TYPES:
            raise FileTypeNotAllow

        # genetate new file name
        new_file_name = str(time.time()).replace('.', str(random.randint(0,100000))) + file_name_suffix
        # use default storage to store file
        default_storage.save(new_file_name, f)
        # check file size
        # byte
        size = default_storage.size(new_file_name)
        if size > settings.ALLOW_MAX_FILE_SIZE:
            default_storage.delete(new_file_name)
            raise FileSizeNotAllow

        result = xml_template % ('Good', '', default_storage.url(new_file_name))
    except UploadPermissionNotAuthorized:
        result = xml_template % ('', u"Upload picture above is limited to registered users +60 points!", '')
    except FileTypeNotAllow:
        result = xml_template % ('', u"Form only allows 'jpg', 'jpeg', 'gif', 'bmp', 'png', 'tiff' rypes of files!", '')
    except FileSizeNotAllow:
        result = xml_template % ('', u"Only allows upload file size% sK!" % settings.ALLOW_MAX_FILE_SIZE / 1024, '')
    except Exception:
        result = xml_template % ('', u"In the file upload process error, please contact the administrator, thank you.", '')

    return HttpResponse(result, mimetype="application/xml")

def search(request):
    return render_to_response('search.html', {
        }, context_instance=RequestContext(request))

@login_required
def add_subscription(request):
    if 'question' in request.GET:
        question = Question.objects.get(id=request.GET['question'])
        (subscription, created) = Subscription.objects.get_or_create(user=request.user, timespan = 15, question = question)
        subscription.save()
        return HttpResponseRedirect(subscription.question.get_absolute_url())
    return HttpResponseRedirect("/")

@login_required 
def delete_subscription(request, id):
    subscription = Subscription.objects.get(id=id) 
    if subscription.user.id != request.user.id: 
        raise Exception("Can't delete a subscription that doesn't belong to you") 
    subscription.delete() 
    return HttpResponseRedirect("/users/%s/%s?sort=subscriptions" % (request.user.id, request.user.username))

def questions_feed(request, amount):
    funcname =  request.GET.get('callback', "forum.get_questions")
    objects = Question.objects.filter(deleted=False).order_by("-last_activity_at").values('id', 'title', 'last_activity_at')[:amount]
    for o in objects:
        for k in o.iterkeys():
            o[k] = str(o[k])
        o['last_activity_at'] = str(o['last_activity_at'])
    return HttpResponse( "%s(%s);" % (funcname, str(objects)), mimetype="text/plain")

def users_feed(request, amount):
    funcname =  request.GET.get('callback', "forum.get_users")	
    objects = User.objects.all().order_by("-last_seen").values('id', 'real_name', 'about', 'reputation', 'gold', 'silver', 'bronze', 'username')[0:amount]
    from django.core.exceptions import ObjectDoesNotExist
    for o in objects:
        questions = Question.objects.filter(last_activity_by=int(o['id'])).order_by("-last_activity_at")
        if (len(questions)>0):
            myquestion = questions[0]
            o['last_question_id'] = myquestion.id
            o['last_question_title'] = myquestion.title
            o['last_activity_at'] = myquestion.last_activity_at

        o['gravatar'] = "%s/mxid/avatar?hash=%s&thumb=true" % (MXID_URL, b64encode(sha256(o['username']).digest()))
        del o['username']
        for k in o.iterkeys():
            o[k] = str(o[k])
    return HttpResponse("%s(%s);" % (funcname, str(objects)), mimetype="text/json")

def error(request):
    return render_to_response("error.html", {
	"error_message" : request.GET.get('error', "An unknown error occurred"),
     }, context_instance=RequestContext(request))

@login_required
def csv_users(request):
	if not request.user.is_superuser:
		raise PermissionDenied
	if 'till' not in request.GET:
		raise Exception("you must provide a 'till' param in the format 'YYYY-mm-dd'")
	if 'from' not in request.GET:
		raise Exception("you must provide a 'from' in the format 'YYYY-mm-dd'")
	from_string = request.GET['from']
	till_string = request.GET['till']
	till_date = datetime.datetime.strptime(till_string, "%Y-%m-%d")
	from_date = datetime.datetime.strptime(from_string, "%Y-%m-%d")
	users = User.objects.all().extra(select={
			'answer_upvotes' : 'SELECT COUNT(*) from vote where content_type_id=2 and object_id in \
				(SELECT id from answer where author_id=auth_user.id and vote=1 AND voted_at between \'%s\' and \'%s\')' % (from_string, till_string), 
			'answer_downvotes' : 'SELECT COUNT(*) from vote where content_type_id=2 and object_id in \
				(SELECT id from answer where author_id=auth_user.id and vote<0 AND voted_at between \'%s\' and \'%s\')' % (from_string, till_string), 
			'question_upvotes' : 'SELECT COUNT(*) from vote where content_type_id=1 and object_id in \
				(SELECT id from question where author_id=auth_user.id and vote=1)', 
			'question_downvotes' : 'SELECT COUNT(*) from vote where content_type_id=1 and object_id in \
				(SELECT id from question where author_id=auth_user.id and vote<0 AND voted_at between \'%s\' and \'%s\')' % (from_string, till_string),
			'accepted' : 'SELECT COUNT(*) from answer where accepted_at between \'%s\' and \'%s\' and author_id=auth_user.id' % (from_string, till_string),
			'questions_that_i_accepted' : 'SELECT COUNT(*) from answer where accepted_at between \'%s\' and \'%s\' and question_id in (select id from question where author_id=auth_user.id)' % (from_string, till_string),
			'new_gold' : 'SELECT COUNT(*) from award where awarded_at between \'%s\' and \'%s\' and user_id=auth_user.id and badge_id in (select id from badge where type=1)' % (from_string, till_string),
			'new_silver' : 'SELECT COUNT(*) from award where awarded_at between \'%s\' and \'%s\' and user_id=auth_user.id and badge_id in (select id from badge where type=2)' % (from_string, till_string),
			'new_bronze' : 'SELECT COUNT(*) from award where awarded_at between \'%s\' and \'%s\' and user_id=auth_user.id and badge_id in (select id from badge where type=3)' % (from_string, till_string)
		})
			
	return render_to_response("csv_users.html", {"users" : users, }, context_instance=RequestContext(request))

@login_required
def csv_questions(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if 'till' not in request.GET:
        raise Exception("you must provide a 'till' param in the format 'YYYY-mm-dd'")
    if 'from' not in request.GET:
        raise Exception("you must provide a 'from' in the format 'YYYY-mm-dd'")
    from_string = request.GET['from']
    till_string = request.GET['till']
    till_date = datetime.datetime.strptime(till_string, "%Y-%m-%d")
    from_date = datetime.datetime.strptime(from_string, "%Y-%m-%d")
    questions = Question.objects.all().filter(deleted=False).filter(added_at__gte=from_date).filter(added_at__lte=till_date)
    return render_to_response("csv_questions.html", {"questions" : questions, }, context_instance=RequestContext(request))

@login_required
def csv_answers(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    if 'till' not in request.GET:
        raise Exception("you must provide a 'till' param in the format 'YYYY-mm-dd'")
    if 'from' not in request.GET:
        raise Exception("you must provide a 'from' in the format 'YYYY-mm-dd'")
    from_string = request.GET['from']
    till_string = request.GET['till']
    till_date = datetime.datetime.strptime(till_string, "%Y-%m-%d")
    from_date = datetime.datetime.strptime(from_string, "%Y-%m-%d")
    answers = Answer.objects.all().filter(deleted=False).select_related('question').filter(added_at__gte=from_date).filter(added_at__lte=till_date)
    return render_to_response("csv_answers.html", {"answers" : answers, }, context_instance=RequestContext(request))
    
#import webservices

#####################################
#									#
# Call Stuff at Platform Analytics	#
#									#
#####################################
import datetime
import json
import tasks

def register_event(event_type, request, open_id, extra_info, extra_info2, extra_info3, timestamp):
    if hasattr(tasks, 'send_event'):
        if open_id == None or open_id == "":
            return
        
        user_agent = ''
        if request:
            user_agent = request.META['HTTP_USER_AGENT']
            
        if not timestamp:
            timestamp = datetime.datetime.now().isoformat()
    
        event = {
            'EventType' : event_type,
            'OpenId' : open_id,
            'CompanyId' : '',
            'UserAgent' : user_agent,
            'ExtraInfo' : extra_info,
            'ExtraInfo2' : extra_info2,
            'ExtraInfo3' : extra_info3,
            'TimeStamp' : timestamp
        }
        
        p = json.dumps(event)
        tasks.send_event.delay(p)
