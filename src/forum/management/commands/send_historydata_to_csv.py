import sys
from django.core.management.base import BaseCommand, CommandError
from forum.models import Answer, Question, Vote, Repute, User, FavoriteQuestion, Comment
import csv
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    def handle(self, *args, **options):
    
        with open('events.csv', 'a+') as csvfile:
        
            fieldnames = ['type', 'ua', 'openid', 'qid', 'aid', 'd3', 'time']
            eventswriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            eventswriter.writeheader()
            
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
                eventswriter.writerow({'type': 'QuestionPosted', 'ua': None, 'openid': question.author.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': question.added_at.isoformat()})
            
            # type 2
            answers = Answer.objects.all()
            sys.stdout.write("Migrating %s answers \n" % len(answers))
            for answer in answers:
                eventswriter.writerow({'type': 'AnswerPosted', 'ua': None, 'openid': answer.author.openid, 'qid': answer.question.id, 'aid': answer.id, 'd3': '', 'time': answer.added_at.isoformat()})
            
            # type 3 - comment on question
            comments_q = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Question))
            sys.stdout.write("Migrating %s comments on questions \n" % len(comments_q))
            for comment in comments_q:
                author = get_object_or_none(User, comment.user_id)
                eventswriter.writerow({'type': 'CommentPosted', 'ua': None, 'openid': author.openid, 'qid': comment.object_id, 'aid': '', 'd3': '', 'time': comment.added_at.isoformat()})
                
            # type 4 - comment on answer
            comments_a = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Answer))
            sys.stdout.write("Migrating %s comments on answers \n" % len(comments_a))
            for comment in comments_a:
                author = get_object_or_none(User, comment.user_id)
                answer = get_object_or_none(Answer, comment.object_id)
                eventswriter.writerow({'type': 'CommentPosted', 'ua': None, 'openid': author.openid, 'qid': answer.question.id, 'aid': answer.id, 'd3': '', 'time': comment.added_at.isoformat()})
            
            # type 8
            accp_answers = Answer.objects.filter(accepted=1)
            sys.stdout.write("Migrating %s accp_answers \n" % len(accp_answers))
            for answer in accp_answers:
                question = get_object_or_none(Question, answer.question_id)
                eventswriter.writerow({'type': 'MarkedAnswerAsAccepted', 'ua': None, 'openid': question.author.openid, 'qid': question.id, 'aid': answer.id, 'd3': '', 'time': answer.accepted_at.isoformat()})
                eventswriter.writerow({'type': 'AnswerWasMarkedAsAccepted','ua':  None, 'openid': answer.author.openid,'qid': question.id, 'aid': answer.id, 'd3': '', 'time': answer.accepted_at.isoformat()})
                
            # type 9
            upvotes = Vote.objects.filter(vote=1)
            sys.stdout.write("Migrating %s upvotes \n" % len(upvotes))        
            for vote in upvotes:
                if (ContentType.objects.get_for_id(vote.content_type_id) == ContentType.objects.get_for_model(Answer)):
                    answer = get_object_or_none(Answer, vote.object_id)
                    user = get_object_or_none(User, vote.user_id)
                    eventswriter.writerow({'type': 'Upvoted', 'ua': None, 'openid': user.openid, 'qid': answer.question_id, 'aid' : answer.id, 'd3': '', 'time': vote.voted_at.isoformat()})
                    eventswriter.writerow({'type': 'ReceivedUpvote', 'ua': None, 'openid': answer.author.openid, 'qid': answer.question_id, 'aid': answer.id, 'd3': '', 'time': vote.voted_at.isoformat()})
                else:
                    question = get_object_or_none(Question, vote.object_id)
                    user = get_object_or_none(User, vote.user_id)
                    eventswriter.writerow({'type': 'Upvoted', 'ua': None, 'openid': user.openid, 'qid': question.id, 'aid' : '', 'd3': '', 'time': vote.voted_at.isoformat()})
                    eventswriter.writerow({'type': 'ReceivedUpvote', 'ua': None, 'openid': question.author.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': vote.voted_at.isoformat()})
                    
            # type 10
            downvotes = Vote.objects.filter(vote=-1)
            sys.stdout.write("Migrating %s downvotes \n" % len(downvotes))                
            for vote in downvotes:
                if (ContentType.objects.get_for_id(vote.content_type_id) == ContentType.objects.get_for_model(Answer)):
                    answer = get_object_or_none(Answer, vote.object_id)
                    user = get_object_or_none(User, vote.user_id)
                    eventswriter.writerow({'type': 'Downvoted', 'ua': None, 'openid': user.openid, 'qid': answer.question_id, 'aid': answer.id, 'd3': '', 'time': vote.voted_at.isoformat()})
                    eventswriter.writerow({'type': 'ReceivedDownvote', 'ua': None, 'openid': answer.author.openid, 'qid': answer.question_id, 'aid': answer.id, 'd3': '', 'time': vote.voted_at.isoformat()})
                else:
                    question = get_object_or_none(Question, vote.object_id)
                    user = get_object_or_none(User, vote.user_id)
                    eventswriter.writerow({'type': 'Downvoted', 'ua': None, 'openid': user.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': vote.voted_at.isoformat()})
                    eventswriter.writerow({'type': 'ReceivedDownvote', 'ua': None, 'openid': question.author.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': vote.voted_at.isoformat()})
                    
            # type 16
            fav_questions = FavoriteQuestion.objects.all()
            sys.stdout.write("Migrating %s fav_questions \n" % len(fav_questions))                        
            for fav_q in fav_questions:
                question = get_object_or_none(Question, fav_q.question_id)
                user = get_object_or_none(User, fav_q.user_id)
                eventswriter.writerow({'type': 'LikedQuestion', 'ua': None, 'openid': user.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': fav_q.added_at.isoformat()})
                eventswriter.writerow({'type': 'ReceivedLike', 'ua': None, 'openid': question.author.openid, 'qid': question.id, 'aid': '', 'd3': '', 'time': fav_q.added_at.isoformat()})
            
            sys.stdout.write("Finished migrating activities \n")
