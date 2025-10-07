from django.urls import path
from airport_route.views import HomepageView, AddAirportView, DeleteAirportView, AddRouteView, DeleteRouteView, SearchNthNode, ShortestNode


urlpatterns = [
    path('', HomepageView.as_view(), name='home'),
    
    path('add_airport/', AddAirportView.as_view(), name='add_airport'),
    path('delete_airport/<int:pk>/', DeleteAirportView.as_view(), name='delete_airport'),
    
    path('add_route/', AddRouteView.as_view(), name='add_route'),
    path('delete_route/<int:pk>/', DeleteRouteView.as_view(), name='delete_route'),
    
    path('search_nth_node/', SearchNthNode.as_view(), name='search_nth_node'),
    path('shortest_node/', ShortestNode.as_view(), name='shortest_node')
]
