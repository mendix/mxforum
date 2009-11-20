from django.core.management.base import LabelCommand
from forum.models import Question, Subscription
from django.db.models import Q
from datetime import datetime, timedelta

class Command(LabelCommand):
    args = "[timespan]"
    label = 'duration that we want to check'
    def handle_label(self, timespan, **options):
        subscriptions = Subscription.objects.filter(timespan=timespan)
        print len(subscriptions)
        print datetime.now()
        now = datetime.now()
		
        f = (datetime.now() - timedelta(minutes=int(timespan)))
        questions = Question.objects.filter(last_activity_at__gte=f)
        print "found %s questions" % len(questions)
        for q in questions:
            #print "title %s, time %s" % (q.title, q.last_activity_at)
            pass
