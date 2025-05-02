from django.urls import path
from . import views

urlpatterns =[
    path('api/SubmitQuery',views.SubmitQuery,name="QuerySubmission"),
    path('test-mongodb/', views.test_mongodb, name="test-mongodb"),
    path('api/TestView',views.TestView,name="TestView"),
    path('api/results/',views.paginated_results,name="paginatedResults"),
]