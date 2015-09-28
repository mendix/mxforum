import settings
from forum.models import Activity, Answer, Question
from const import *
from views import register_event

if __name__ == '__main__':
    
    def register_vote(event_type, received, activity):
        answer = get_object_or_404(Answer, id=activity.object_id)
        if answer is not None:
            if not received:
                register_event(event_type, None, activity.user_id, answer.question_id, answer.id, '', activity.active_at)
            else:
                register_event(event_type, None, answer.author.user_id, answer.question_id, answer.id, '', activity.active_at)
        else:
            question = get_object_or_404(Question, id=activity.object_id)
            if not received:
                register_event(event_type, None, activity.user_id, question.id, '', '', activity.active_at)
            else:
                register_event(event_type, None, question.author.user_id, question.id, '', '', activity.active_at)
    
    activities = Activity.objects.exclude(
        activity_type=[3,4,5,6,7,14,15,17]
    ).order_by('-active_at')
    
    for activity in activities:
        activity_type = activity.activity_type
        
        if   activity_type == 1:
            register_event('QuestionPosted', None, activity.user_id, activity.object_id, '', '', activity.active_at)
            
        elif activity_type == 2:
            register_event('AnswerPosted', None, activity.user_id, activity.object_id, '', '', activity.active_at)
            
        elif activity_type == 8:
            answer = get_object_or_404(Answer, id=activity.object_id)
            register_event('MarkedAnswerAsAccepted', None, activity.user_id, answer.question_id, activity.object_id, '', activity.active_at)
            register_event('AnswerWasMarkedAsAccepted', None, answer.author.user_id, answer.question_id, activity.object_id, '', activity.active_at)
            
        elif activity_type == 9:
            register_vote('Upvoted', False, activity)
            register_vote('ReceivedUpvote', True, activity)
            
        elif activity_type == 10:
            register_vote('Downvoted', False, activity)
            register_vote('ReceivedDownvote', True, activity)
            
        elif activity_type == 11:
            vote = get_object_or_404(Vote, id=activity.object_id)
            if vote.vote == 1:
                # Cancel upvote
                answer = get_object_or_404(Answer, id=vote.object_id)
                if answer is not None:
                    # Vote on answer
                    register_event('RetractUpvote', None, activity.user_id, answer.question_id, answer.id, '', activity.active_at)
                    register_event('UpvoteRemoved', None, answer.author.user_id, answer.question_id, answer.id, '', activity.active_at)
                else:
                    # Vote on question
                    question = get_object_or_404(Question, id=vote.object_id)
                    register_event('RetractUpvote', None, activity.user_id, question.id, '', '', activity.active_at)
                    register_event('UpvoteRemoved', None, question.author.user_id, question.id, '', '', activity.active_at)
            else:
                # Cancel downvote
                if answer is not None:
                    # Vote on answer
                    register_event('RetractDownvote', None, activity.user_id, answer.question_id, answer.id, '', activity.active_at)
                    register_event('DownvoteRemoved', None, answer.author.user_id, answer.question_id, answer.id, '', activity.active_at)
                else:
                    # Vote on question
                    question = get_object_or_404(Question, id=vote.object_id)
                    register_event('RetractDownvote', None, activity.user_id, question.id, '', '', activity.active_at)
                    register_event('DownvoteRemoved', None, question.author.user_id, question.id, '', '', activity.active_at)
            
        elif activity_type == 12:
            register_event('RemovedQuestion', None, activity.user_id, activity.object_id, '', '', activity.active_at)
            
        elif activity_type == 13:
            answer = get_object_or_404(Answer, id=vote.object_id)
            register_event('RemovedAnswer', None, activity.user_id, answer.question_id, answer.id, '', activity.active_at)
            
        elif activity_type == 16:
            question = get_object_or_404(Question, id=activity.object_id)
            register_event('LikedQuestion', None, activity.user_id, question.id, '', '', activity.active_at)
            register_event('ReceivedLike', None, question.author, question.id, '', '', activity.active_at)