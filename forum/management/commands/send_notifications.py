from django.core.management.base import LabelCommand
from forum.models import Question, Subscription
from django.db.models import Q
from datetime import datetime, timedelta

class Command(LabelCommand):
    args = "[timespan]"
    label = 'duration that we want to check'
    def handle_label(self, timespan, **options):
        subscriptions = Subscription.objects.filter(timespan=timespan).order_by('user')
        f = (datetime.now() - timedelta(minutes=int(timespan)))
        questions = Question.objects.filter(last_activity_at__gte=f)

        print "subs before filteri %s" % subscriptions
        subs2 = filter( (lambda x: x.question in questions), subscriptions)
        print "subs after filter %s " % subs2
        #for s in subscriptions:
        #    if s.user not in ordered_subs:
        #        ordered_subs[s.user] = []
            
        #    ordered_subs[s.user].append(s)
        print "found %s subs" % len(subscriptions)
		
        print "found %s questions" % len(questions)
        for q in questions[:3]:
            print "title %s, time %s" % (q.title, q.last_activity_at)
            pass
