from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def viewer (request):
    #patient = Patient.objects.get(directory=key)
    user = request.user._wrapped.__dict__
    '''
    patient_id = request.GET.get('patient_id', -1)
    #print(user)
    del user['_state']
    del user['last_login']
    del user['date_joined']
    context = {'fix_patient_id': patient_id,
               'user': user
              }
    '''
    context = {}
    return render(request, 'web/viewer.html', context)

