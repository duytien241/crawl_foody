from __future__ import absolute_import, unicode_literals
import random
from celery.decorators import task
from celery import Celery

app = Celery()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(10.0, add(1,3), name='add every 10')

@app.task
def add(x, y):
    print('x+y')

@task(name="multiply_two_numbers")
def mul(x, y):
    total = x * (y * random.randint(3, 100))
    return total

@task(name="sum_list_numbers")
def xsum(numbers):
    return sum(numbers)

