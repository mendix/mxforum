from django.core.management.base import NoArgsCommand
from forum.models import Question
from django.db.models import Q
from django.core.mail import send_mail

class Command(NoArgsCommand):
	def handle_noargs(self, **options):
		questions = Question.objects.filter( Q(answer_accepted=False), deleted=False).exclude(answers__vote_up_count__gt=4).order_by("author")
		ordered_questions = {}
		for q in questions:
			if q.author not in ordered_questions:
				ordered_questions[q.author] = []
			ordered_questions[q.author].append(q)

		for u, qs in ordered_questions.iteritems():
			message = "Dear %s\n\nThank you for participating in the MxCommunity.\n\nWe noticed you still have some questions on the Forum without an Accepted Answer.\n\n" % q.author.real_name
			message += "We were wondering if you found your answer among those given. If not, try giving more information concerning the problem or try rephrasing the question.\n\n"
			for q in qs[:2]:
				message += "%s\nhttps://mxforum.mendix.com%s\n\n" % (q.title, q.get_absolute_url())
			message +=  "If you have found your answer, we would like you to select it as Accepted Answer so future viewers can quickly see what the best answer is.\n\n"
			message += "You can also vote on questions and answers, this helps other people find    their answers faster and rewards people for helping out.\n\n"
			message += "Please enjoy your stay on the MxCommunity and don't hesitate to ask more questions!\n\nKind regards,"
			send_mail('Have you found your answer on the Mendix Forum?', message, 'mxforum@mendix.com', ['robert.van.thof@mendix.com'], fail_silently=False)
