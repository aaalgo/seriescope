import numpy as np
import simplejson as json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from demos.physionet18 import sleep


# Create your views here.

def test (request):
    return JsonResponse({'hello': 'world!'})

def gen_data ():
    return [int(x) for x in np.random.randint(100, 200, size=(20,))]

@csrf_exempt
def lineChartData (request):
    data = json.loads(request.body)
    print(data)

    data = {
      'newVisitis': {
        'expectedData': gen_data(),
        'actualData': gen_data(),
      },
      'messages': {
        'expectedData': gen_data(),
        'actualData': gen_data(),
      },
      'purchases': {
        'expectedData': gen_data(),
        'actualData': gen_data(),
      },
      'shoppings': {
        'expectedData': gen_data(),
        'actualData': gen_data(),
      }
    }
    return JsonResponse(data)

