# USSDS

A Ussds listing application.

## Running Locally

Make sure you have Python [installed properly](http://install.python-guide.org).  
Optional, install the [Heroku Toolbelt](https://toolbelt.heroku.com/) and [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone git@github.com:danleyb2/ussds.git
$ cd ussds
$ pip install -r requirements.txt
$ python manage.py migrate
$ heroku local:run python manage.py migrate # ignore if you didn't Heroku Toolbelt
$ python manage.py collectstatic
$ heroku local # ignore if you didn't Heroku Toolbelt
$ python manage.py runserver
```

Your app should now be running on [localhost:8000](http://localhost:8000/).

## Deploying to Heroku

```sh
$ heroku create
$ git push heroku master
$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)

## Documentation
