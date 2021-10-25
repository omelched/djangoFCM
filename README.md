# djangoFCM<sup><sup>_v0.1.0_</sup></sup>

Django app which stores, manages FCM push tokens and interacts with them.

## Description

**djangoFCM** is Django-compatible application which stores FCM push tokens,
their parameters, and automates push notifications routines.

Main feature is for **djangoFCM** to be a "plug-in" Django application, thus capable to 
work with "little-to-no" configuring and changes to Django project.

### Features

**djangoFCM** @ [v0.1.0](https://github.com/omelched/djangoFCM/releases/tag/v0.1.0) can:

 - store push tokens
 - store push tokens` arbitrary parameters with types:
   - foreign key
 - store push notifications
 - send scheduled push notifications
 - compose recipients for push notifications based on user-specified conditions

### Usage example

_TODO_

#### sample_project

[`sample-project`](sample_project) is a showcase django project.
You can reference to it for usage cases, examples, testing.
You must never deploy `sample_project` in production due to exposed `SECRET_KEY`.

## Getting Started

### Dependencies

#### System dependencies

In means of automatisation, **djangoFCM** heavily relies on `celery` (via `django-celery-beat`), thus it is your task
to provide `celery` and `celerybeat` processes and message broker (e.g. `rabbitMQ`). 

#### Python packages

* `django~=3.2.8` <sub><sub>might work on lesser versions, not tested</sub></sub>
* `django-celery-beat~=2.2.1` <sub><sub>might work on lesser versions, not tested</sub></sub>
* `pyfcm~=1.5.4` <sub><sub>might work on lesser versions, not tested</sub></sub>

#### Django applications

* `django_celery_beat`

### Installing

#### Using Python Package Index

* make sure to use latest `pip`:
  ```shell
  python3 -m pip install --upgrade pip
  ```

* install `djangoFCM`:
  ```shell
  python3 -m pip install djangoFCM
  ```
  
#### OR download package from releases

* download release asset (`.tar.gz` or `.whl`)

* make sure to use latest `pip`:
  ```shell
  python3 -m pip install --upgrade pip
  ```

* install `djangoFCM` from file:
  ```shell
  python3 -m pip install /path/to/downloaded/asset.tar.gz # or .whl
  ```

#### OR clone from repository 

* clone project:
  ```shell
  git clone \
          --depth=1 \
          --branch=master \
          git@github.com:omelched/djangoFCM.git \
          </path/to/downloads>
  ```

* move `/djangoFCM/djangoFCM` solely to folder containing django apps
  ```shell
  mv      </path/to/downloads>/djangoFCM/djangoFCM \
          </path/to/django/project/apps>
  ```
  
* remove leftovers
  ```shell
  rm -rf  </path/to/downloads>/djangoFCM
  ```

### Configuring

#### Installing application

Add `djangoFCM` to `INSTALLED_APPS` in your Django project `settings.py`.

If you installed package [the third way](#or-clone-from-repository), `</path/to/django/project/apps>`
must be added to `PYTHONPATH`. If you not sure add code below in your Django project `manage.py` before calling `main()`:
```python
sys.path.append('</path/to/django/project/apps>')
```

Provide FCM api key via `DJANGOFCM_FCM_API_KEY` in your Django project `settings.py`.

#### Celery

Make sure to point celery to `djangoFCM.tasks.send_push_notification` task. 
Use `app.autodiscover_tasks()` in your `celeryapp` module or specify in settings:
```python
CELERY_IMPORTS = (
    'djangoFCM.tasks',
)
```

Provide Celery worker to execute tasks, e.g:
```shell
venv/bin/celery -A sample_project worker -l INFO
```

Official [documentation](https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html) may help.

#### Celerybeat

Provide Celery beat to start scheduled tasks, e.g:

```shell
venv/bin/celery -A sample_project beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Official [documentation](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#using-custom-scheduler-classes)
on custom schedulers.

## Authors

[@omelched](https://github.com/omelched) _(Denis Omelchenko)_

### Contributors

<img width=20% src="https://64.media.tumblr.com/7b59c6105c40d611aafac4539500fee1/tumblr_njiv6sUfgO1tvqkkro1_640.gifv" title="tumbleweed"/>

## Changelist

**djangoFCM** version history and changelist available at [releases](https://github.com/omelched/djangoFCM/releases) page.

## License

This project is licensed under the **GNU APGLv3** License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspiration, code snippets, etc.
