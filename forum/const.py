# encoding:utf-8
"""
All constants could be used in other modules
For reasons that models, views can't have unicode text in this project, all unicode text go here.
"""
CLOSE_REASONS = (
    (1, u'The problem of repeat'),
    (2, u'Technical issues rather than programming'),
    (3, u'Too subjective, the question arising from a quarrel'),
    (4, u'Is not an answer to the "problem"'),
    (5, u'Problems have been solved, have been the right answer'),
    (6, u'Is outdated and can not reproduce the problem'),
    (7, u'Too local, the question of the localization'),
    (8, u'Malicious remarks'),
    (9, u'Spam ads'),
)

TYPE_REPUTATION = (
    (1, 'gain_by_upvoted'),
    (2, 'gain_by_answer_accepted'),
    (3, 'gain_by_accepting_answer'),
    (4, 'gain_by_downvote_canceled'),
    (5, 'gain_by_canceling_downvote'),
    (-1, 'lose_by_canceling_accepted_answer'),
    (-2, 'lose_by_accepted_answer_cancled'),
    (-3, 'lose_by_downvoted'),
    (-4, 'lose_by_flagged'),
    (-5, 'lose_by_downvoting'),
    (-6, 'lose_by_flagged_lastrevision_3_times'),
    (-7, 'lose_by_flagged_lastrevision_5_times'),
    (-8, 'lose_by_upvote_canceled'),
)

TYPE_ACTIVITY_ASK_QUESTION=1
TYPE_ACTIVITY_ANSWER=2
TYPE_ACTIVITY_COMMENT_QUESTION=3
TYPE_ACTIVITY_COMMENT_ANSWER=4
TYPE_ACTIVITY_UPDATE_QUESTION=5
TYPE_ACTIVITY_UPDATE_ANSWER=6
TYPE_ACTIVITY_PRIZE=7
TYPE_ACTIVITY_MARK_ANSWER=8
TYPE_ACTIVITY_VOTE_UP=9
TYPE_ACTIVITY_VOTE_DOWN=10
TYPE_ACTIVITY_CANCEL_VOTE=11
TYPE_ACTIVITY_DELETE_QUESTION=12
TYPE_ACTIVITY_DELETE_ANSWER=13
TYPE_ACTIVITY_MARK_OFFENSIVE=14
TYPE_ACTIVITY_UPDATE_TAGS=15
TYPE_ACTIVITY_FAVORITE=16
TYPE_ACTIVITY_USER_FULL_UPDATED = 17
#TYPE_ACTIVITY_EDIT_QUESTION=17
#TYPE_ACTIVITY_EDIT_ANSWER=18

TYPE_ACTIVITY = (
    (TYPE_ACTIVITY_ASK_QUESTION, u'Question'),
    (TYPE_ACTIVITY_ANSWER, u'Answer'),
    (TYPE_ACTIVITY_COMMENT_QUESTION, u'Comment on the issue of'),
    (TYPE_ACTIVITY_COMMENT_ANSWER, u'Comment answer'),
    (TYPE_ACTIVITY_UPDATE_QUESTION, u'Modification'),
    (TYPE_ACTIVITY_UPDATE_ANSWER, u'Amend the answer'),
    (TYPE_ACTIVITY_PRIZE, u'Award-winning'),
    (TYPE_ACTIVITY_MARK_ANSWER, u'Marking the best answer'),
    (TYPE_ACTIVITY_VOTE_UP, u'Vote in favor of'),
    (TYPE_ACTIVITY_VOTE_DOWN, u'Vote against'),
    (TYPE_ACTIVITY_CANCEL_VOTE, u'Revocation of voting'),
    (TYPE_ACTIVITY_DELETE_QUESTION, u'Delete problem'),
    (TYPE_ACTIVITY_DELETE_ANSWER, u'Delete reply'),
    (TYPE_ACTIVITY_MARK_OFFENSIVE, u'Tag abuse'),
    (TYPE_ACTIVITY_UPDATE_TAGS, u'Update tags'),
    (TYPE_ACTIVITY_FAVORITE, u'Favorites'),
    (TYPE_ACTIVITY_USER_FULL_UPDATED, u'Completion of all personal information'),
    #(TYPE_ACTIVITY_EDIT_QUESTION, u'Editor problem'),
    #(TYPE_ACTIVITY_EDIT_ANSWER, u'Edit the answer'),
)

TYPE_RESPONSE = {
    'QUESTION_ANSWERED' : u'Answer questions',
    'QUESTION_COMMENTED': u'Review of',
    'ANSWER_COMMENTED'  : u'Reply to comment',
    'ANSWER_ACCEPTED'   : u'Best answer',
}

CONST = {
    'closed'            : u'[Closed]',
    'default_version'   : u'Initial version',
    'retagged'          : u'Update the labels',

}
