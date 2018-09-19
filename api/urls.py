from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='viewer', permanent=True), name='web_index'),
    url(r'^test$', views.test, name='test'),
    url(r'^lineChartData$', views.lineChartData, name='lineChartData'),
#    url(r'^image/(..)/(.+)$', views.image, name='image'),
#    url(r'^annotations/(.+)$', views.annotations, name='annotations'),
#    url(r'^set_image_status$', views.set_image_status, name='set_image_status'),
#    url(r'^set_patient_status$', views.set_patient_status, name='set_patient_status'),
#    url(r'^patient$', views.patient, name='patient'),
#    url(r'^reset_all_patient', views.reset_all_patient, name='reset_all_patient'),
]

