import datetime

def log(string):
    with open('log/forum.log', 'a+') as f:
        f.write( "[%s] %s\n\n", (datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S"), string))