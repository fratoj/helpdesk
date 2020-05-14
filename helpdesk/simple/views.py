from django.shortcuts import render
import numpy as np


def index(request):
    return render(request, 'simple/index.html')


def room(request, room_name):
    safe = np.random.normal(size=20, loc=0, scale=1)
    return render(request, 'simple/room.html', {
        'room_name': room_name,
        'some_thing': {
            'yolo': 'fish',
            'test': [1,2,3],
        },
        'stay': safe.tolist()
    })


def question(request):
    return render(request, 'simple/question.html')
