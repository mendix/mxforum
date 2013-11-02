import os, sys
import smtplib
from email.mime.text import MIMEText

from django.core.management.base import LabelCommand
from forum.models import Question, Subscription
from django.db.models import Q
from datetime import datetime, timedelta

import settings
from collections import defaultdict

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("I need a timespan to check")
        sys.exit(1)
    else:
        smtp = smtplib.SMTP('smtp.mendix.nl')
        timespan = sys.argv[1]
        all_subscriptions = Subscription.objects.filter().order_by('user')
        f = (datetime.now() - timedelta(minutes=int(timespan)))
        questions = Question.objects.filter(last_activity_at__gte=f)

        subscriptions = filter( (lambda s: s.question in questions and str(s.question.last_activity_by) !=  str(s.user.username)), all_subscriptions)
        ordered_subs = defaultdict(set)
        for s in subscriptions:
            ordered_subs[s.user].add(s)
        
        original_header = "Dear %s,\n\nYou are receiving this message because you have subscribed to receive mail whenever any of your questions have activity. The following questions have seen activity in the last 24 hours:\n\n"
        original_footer = "You can unsubscribe to any of these questions by updating your profile at %s/users/%s?sort=subscriptions\n\nKind regards,\nthe MxForum Team"
        for user in ordered_subs.iterkeys():
            message = original_header % user.real_name
            for s in ordered_subs[user]:
                q = s.question
                message += "%s\n%s%s last activity by %s at %s\n\n" % (q.title, settings.MY_URL, q.get_absolute_url(), q.last_activity_by.real_name, q.last_activity_at)
            message += original_footer % (settings.MY_URL, user.id)
            msg = MIMEText(message)
            msg['Subject'] = 'MxForum daily digest'
            msg['From'] = 'mxforum@mendix.com'
            msg['To'] = user.username
            smtp.sendmail('mxforum@mendix.com', [user.username], msg.as_string())


        smtp.quit()
