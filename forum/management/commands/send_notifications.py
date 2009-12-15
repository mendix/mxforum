from django.core.management.base import LabelCommand
from forum.models import Question, Subscription
from django.db.models import Q
from datetime import datetime, timedelta
import settings
from django.core.mail import send_mail

class Command(LabelCommand):
    args = "[timespan]"
    label = 'duration that we want to check'
    def handle_label(self, timespan, **options):
        all_subscriptions = Subscription.objects.filter(timespan=timespan).order_by('user')
        f = (datetime.now() - timedelta(minutes=int(timespan)))
        questions = Question.objects.filter(last_activity_at__gte=f)

        subscriptions = filter( (lambda x: x.question in questions), all_subscriptions)
        print "subs after filter %s " % subscriptions
        ordered_subs = {}
        for s in subscriptions:
            if s.user not in ordered_subs:
                ordered_subs[s.user] = []
           
            ordered_subs[s.user].append(s)
        print "found %s subs" % len(subscriptions)
        print "found %s orderedsubs " % len(ordered_subs)
		
        print ordered_subs
        original_header = "Dear %s,\n\nYou are receiving this message because you have subscribed to receive mail whenever any of your questions have activity. The following questions have seen activity since the last mail digest that you have received from us:\n\n"
        original_footer = "You can unsubscribe to any of these questions by updating your profile at %s/users/%s?sort=subscriptions\n\nKind regards,\nthe MxForum Team"
        for user in ordered_subs.iterkeys():
            message = original_header % user.real_name
            for s in ordered_subs[user]:
                q = s.question
                message += "%s\n%s%s last activity by %s at %s\n\n" % (q.title, settings.MY_URL, q.get_absolute_url(), q.last_activity_by.real_name, q.last_activity_at)
            message += original_footer % (settings.MY_URL, user.id)
            send_mail('MxForum updates digest', message, 'mxforum@mendix.com', [user.username], fail_silently=False)
            print message


