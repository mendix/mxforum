import sys
from django.core.management.base import BaseCommand, CommandError
from forum.models import Answer, Question, Vote, Repute, User, FavoriteQuestion, Comment
from forum.views import register_event
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    def handle(self, *args, **options):
        
        sys.stdout.write("Migrating activities \n")

        def get_object_or_none(obj_type, obj_id):
            try:
                obj = obj_type.objects.get(id=obj_id)
                return obj
            except ObjectDoesNotExist:
                return None
        
        # type 1
        questions = Question.objects.all()
        sys.stdout.write("Migrating %s questions \n" % len(questions))
        for question in questions:
            register_event('QuestionPosted', None, question.author.openid, question.id, '', '', question.added_at.isoformat())
        
        # type 2
        answers = Answer.objects.all()
        sys.stdout.write("Migrating %s answers \n" % len(answers))
        for answer in answers:
            register_event('AnswerPosted', None, answer.author.openid, answer.question.id, answer.id, '', answer.added_at.isoformat())
        
        # type 3 - comment on question
        comments_q = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Question))
        sys.stdout.write("Migrating %s comments on questions \n" % len(comments_q))
        for comment in comments_q:
            author = get_object_or_none(User, comment.user_id)
            register_event('CommentPosted', None, author.openid, comment.object_id, '', '', comment.added_at.isoformat())
            
        # type 4 - comment on answer
        comments_a = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Answer))
        sys.stdout.write("Migrating %s comments on answers \n" % len(comments_a))
        for comment in comments_a:
            author = get_object_or_none(User, comment.user_id)
            answer = get_object_or_none(Answer, comment.object_id)
            register_event('CommentPosted', None, author.openid, answer.question.id, answer.id, '', comment.added_at.isoformat())
        
        # type 8
        accp_answers = Answer.objects.filter(accepted=1)
        sys.stdout.write("Migrating %s accp_answers \n" % len(accp_answers))
        for answer in accp_answers:
            question = get_object_or_none(Question, answer.question_id)
            register_event('MarkedAnswerAsAccepted', None, question.author.openid, question.id, answer.id, '', answer.accepted_at.isoformat())
            register_event('AnswerWasMarkedAsAccepted', None, answer.author.openid, question.id, answer.id, '', answer.accepted_at.isoformat())
            
        # type 9
        upvotes = Vote.objects.filter(vote=1)
        sys.stdout.write("Migrating %s upvotes \n" % len(upvotes))        
        for vote in upvotes:
            if (ContentType.objects.get_for_id(vote.content_type_id) == ContentType.objects.get_for_model(Answer)):
                answer = get_object_or_none(Answer, vote.object_id)
                user = get_object_or_none(User, vote.user_id)
                register_event('Upvoted', None, user.openid, answer.question_id, answer.id, '', vote.voted_at.isoformat())
                register_event('ReceivedUpvote', None, answer.author.openid, answer.question_id, answer.id, '', vote.voted_at.isoformat())
            else:
                question = get_object_or_none(Question, vote.object_id)
                user = get_object_or_none(User, vote.user_id)
                register_event('Upvoted', None, user.openid, question.id, '', '', vote.voted_at.isoformat())
                register_event('ReceivedUpvote', None, question.author.openid, question.id, '', '', vote.voted_at.isoformat())
                
        # type 10
        downvotes = Vote.objects.filter(vote=-1)
        sys.stdout.write("Migrating %s downvotes \n" % len(downvotes))                
        for vote in downvotes:
            if (ContentType.objects.get_for_id(vote.content_type_id) == ContentType.objects.get_for_model(Answer)):
                answer = get_object_or_none(Answer, vote.object_id)
                user = get_object_or_none(User, vote.user_id)
                register_event('Downvoted', None, user.openid, answer.question_id, answer.id, '', vote.voted_at.isoformat())
                register_event('ReceivedDownvote', None, answer.author.openid, answer.question_id, answer.id, '', vote.voted_at.isoformat())
            else:
                question = get_object_or_none(Question, vote.object_id)
                user = get_object_or_none(User, vote.user_id)
                register_event('Downvoted', None, user.openid, question.id, '', '', vote.voted_at.isoformat())
                register_event('ReceivedDownvote', None, question.author.openid, question.id, '', '', vote.voted_at.isoformat())
                
        # type 16
        fav_questions = FavoriteQuestion.objects.all()
        sys.stdout.write("Migrating %s fav_questions \n" % len(fav_questions))                        
        for fav_q in fav_questions:
            question = get_object_or_none(Question, fav_q.question_id)
            user = get_object_or_none(User, fav_q.user_id)
            register_event('LikedQuestion', None, user.openid, question.id, '', '', fav_q.added_at.isoformat())
            register_event('ReceivedLike', None, question.author.openid, question.id, '', '', fav_q.added_at.isoformat())
        
        sys.stdout.write("Finished migrating activities \n")
