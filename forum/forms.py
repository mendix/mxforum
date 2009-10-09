import re
from datetime import date
from django import forms
from models import *
from const import *
from forum.emailauth import * 
from django.contrib.auth import authenticate

class TitleField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(TitleField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.TextInput(attrs={'size' : 70, 'autocomplete' : 'off'})
        self.max_length = 255
        self.label  = u'Title'
        self.help_text = u''
        self.initial = ''

    def clean(self, value):
        if len(value) < 10:
            raise forms.ValidationError(u"The length of the title must be greater than 10")

        return value

class EditorField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(EditorField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.Textarea(attrs={'id':'editor'})
        self.label  = u'内容'
        self.help_text = u''
        self.initial = ''

    def clean(self, value):
        if len(value) < 10:
            raise forms.ValidationError(u"Content of at least 10 characters")

        return value

class TagNamesField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(TagNamesField, self).__init__(*args, **kwargs)
        self.required = True
        self.widget = forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'})
        self.max_length = 255
        self.label  = u'Tags'
        self.help_text = u'Please use spaces to separate tags and use - to combine words, for example: model-driven'
        self.initial = ''

    def clean(self, value):
        value = super(TagNamesField, self).clean(value)
        data = value.strip()
        if len(data) < 1:
            raise forms.ValidationError(u'Tags can not be empty')
        list = data.split(' ')
        list_temp = []
        if len(list) > 5:
            raise forms.ValidationError(u'There can be up to 5 labels')
        for tag in list:
            if len(tag) > 30:
                raise forms.ValidationError(u'The length of each label of no more than 20')

            #TODO: regex match not allowed characters here

            if tag.find('/') > -1 or tag.find('\\') > -1 or tag.find('<') > -1 or tag.find('>') > -1 or tag.find('&') > -1 or tag.find('\'') > -1 or tag.find('"') > -1:
            #if not tagname_re.match(tag):
                raise forms.ValidationError(u'Tags, please use English letters or the number of strings (. - _ # Can)')
            # only keep one same tag
            if tag not in list_temp and len(tag.strip()) > 0:
                list_temp.append(tag)
        return u' '.join(list_temp)

class WikiField(forms.BooleanField):
    def __init__(self, *args, **kwargs):
        super(WikiField, self).__init__(*args, **kwargs)
        self.required = False
        self.label  = u'Wiki markup'
        self.help_text = u'Choice community wiki model, question and answer does not count points, the signature does not show the author information'


class SummaryField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super(SummaryField, self).__init__(*args, **kwargs)
        self.required = False
        self.widget = forms.TextInput(attrs={'size' : 50, 'autocomplete' : 'off'})
        self.max_length = 300
        self.label  = u'Update Summary：'
        self.help_text = u'Changes made'

class AskForm(forms.Form):
    title  = TitleField()
    text   = EditorField()
    tags   = TagNamesField()
    wiki = WikiField()

    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))



class AnswerForm(forms.Form):
    text   = EditorField()
    wiki   = WikiField()
    openid = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 40, 'class':'openid-input'}))
    user   = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    email  = forms.CharField(required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    def __init__(self, question, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        if question.wiki:
            self.fields['wiki'].initial = True

class CloseForm(forms.Form):
    reason = forms.ChoiceField(choices=CLOSE_REASONS)

class RetagQuestionForm(forms.Form):
    tags   = TagNamesField()
    # initialize the default values
    def __init__(self, question, *args, **kwargs):
        super(RetagQuestionForm, self).__init__(*args, **kwargs)
        self.fields['tags'].initial = question.tagnames

class RevisionForm(forms.Form):
    """
    Lists revisions of a Question or Answer
    """
    revision = forms.ChoiceField(widget=forms.Select(attrs={'style' : 'width:520px'}))

    def __init__(self, post, latest_revision, *args, **kwargs):
        super(RevisionForm, self).__init__(*args, **kwargs)
        revisions = post.revisions.all().values_list(
            'revision', 'author__username', 'revised_at', 'summary')
        date_format = '%c'
        self.fields['revision'].choices = [
            (r[0], u'%s - %s (%s) %s' % (r[0], r[1], r[2].strftime(date_format), r[3]))
            for r in revisions]
        self.fields['revision'].initial = latest_revision.revision

class EditQuestionForm(forms.Form):
    title  = TitleField()
    text   = EditorField()
    tags   = TagNamesField()
    summary = SummaryField()

    def __init__(self, question, revision, *args, **kwargs):
        super(EditQuestionForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = revision.title
        self.fields['text'].initial = revision.text
        self.fields['tags'].initial = revision.tagnames
        # Once wiki mode is enabled, it can't be disabled
        if not question.wiki:
            self.fields['wiki'] = WikiField()

class EditAnswerForm(forms.Form):
    text = EditorField()
    summary = SummaryField()

    def __init__(self, answer, revision, *args, **kwargs):
        super(EditAnswerForm, self).__init__(*args, **kwargs)
        self.fields['text'].initial = revision.text

class EditUserForm(forms.Form):
    email = forms.EmailField(label=u'Email', help_text=u'Changing your gravatar', required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    realname = forms.CharField(label=u'Real name', required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    website = forms.URLField(label=u'Personal Website', required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    city = forms.CharField(label=u'City', required=False, max_length=255, widget=forms.TextInput(attrs={'size' : 35}))
    about = forms.CharField(label=u'Profile', required=False, widget=forms.Textarea(attrs={'cols' : 60}))

    def __init__(self, user, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].initial = user.email
        self.fields['realname'].initial = user.real_name
        self.fields['website'].initial = user.website
        self.fields['city'].initial = user.location

        self.fields['about'].initial = user.about
        self.user = user

    def clean_email(self):
        """For security reason one unique email in database"""
        if self.user.email != self.cleaned_data['email']:
            if 'email' in self.cleaned_data:
                try:
                    user = User.objects.get(email = self.cleaned_data['email'])
                except User.DoesNotExist:
                    return self.cleaned_data['email']
                except User.MultipleObjectsReturned:
                    raise forms.ValidationError(u'The email have been registered, please choose another email.')
                raise forms.ValidationError("The e-mail account has been registered, please choose another try.")
        else:
            return self.cleaned_data['email']

class FrankAuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    username = forms.CharField(label=("Username"), max_length=50)
    password = forms.CharField(label=("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(FrankAuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(("This account is inactive."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))

        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache

