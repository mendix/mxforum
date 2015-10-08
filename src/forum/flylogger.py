import datetime

def flog(string):
    with open('forum.log', 'a+') as f:
        f.write( "[%s] %s\n\n" % (datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"), string))
