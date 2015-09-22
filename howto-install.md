# How to install the forum using python locally


- Install python 2.7.10
- Install MySQL
- Install pip
- Install all the requirements.txt (`'pip install -r requirements.txt'` should work)
- Make you get django 1.0 [Tarball here](https://www.djangoproject.com/download/1.0.4/tarball/)
- Unpack tarball and run `'python setup.py install'`
- Install [Possibly needed (Microsoft Visual C++ Compiler for Python 2.7)](http://www.microsoft.com/en-us/download/confirmation.aspx?id=44266)
- install [mysql-connector-c-6.0.2-win32.msi](http://dev.mysql.com/downloads/file.php?id=378015) (needed because of this answer: http://stackoverflow.com/a/19056568)

# Starting the server

- python manage.py runserver
- Goto localhost:8000