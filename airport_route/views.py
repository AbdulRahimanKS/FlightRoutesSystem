from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.db.models import Avg
from django.views import View
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import AirportForm, RouteForm, SearchNthNodeForm, ShortestNodeForm
from .models import Airport, Route
from collections import deque


# Home Page View
class HomepageView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        routes = Route.objects.all()
        
        context['total_airports'] = Airport.objects.count()
        context['total_routes'] = routes.count()
        context['longest_route'] = routes.order_by('-duration').first()
        return context
    

# Add Airport View
class AddAirportView(CreateView):
    template_name = 'add_airport.html'
    form_class = AirportForm
    success_url = reverse_lazy('add_airport')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Airport added successfully")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        airports = Airport.objects.all().order_by('created_at')
        return self.render_to_response(self.get_context_data(airport_form=form, airports=airports))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'airport_form' not in context:
            context['airport_form'] = self.get_form()
        context['airports'] = Airport.objects.all().order_by('created_at')
        return context


# Delete Airport View
class DeleteAirportView(View):
    def post(self, request, pk):
        airport = get_object_or_404(Airport, pk=pk)
        
        is_used = Route.objects.filter(
            models.Q(from_airport=airport) | models.Q(to_airport=airport)
        ).exists()
        
        if is_used:
            messages.error(request, f"Cannot delete airport, it is used in one or more routes")
        else:
            airport.delete()
            messages.success(request, f"Airport deleted successfully")
            
        return redirect('add_airport')
    

# Add Route View
class AddRouteView(CreateView):
    template_name = 'add_route.html'
    form_class = RouteForm
    success_url = reverse_lazy('add_route')
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Airport Route added successfully")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        routes = Route.objects.all().select_related('from_airport', 'to_airport').order_by('created_at')
        return self.render_to_response(self.get_context_data(route_form=form, routes=routes))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'route_form' not in context:
            context['route_form'] = self.get_form()
        context['routes'] = Route.objects.all().select_related('from_airport', 'to_airport').order_by('created_at')
        return context


# Delete Route View
class DeleteRouteView(View):
    def post(self, request, pk):
        route = get_object_or_404(Route, pk=pk)
        
        if route.children.exists():
            child_count = route.children.count()
            messages.error(request, f'Cannot delete this route. It has {child_count} child route(s) connected to it')
            return redirect('add_route')
        
        if not route.parent:
            root_routes = Route.objects.filter(parent__isnull=True)
            if root_routes.count() == 1:
                messages.warning(request, 'You are deleting the root route. This will remove the entire route tree')
                
        route.delete()
        messages.success(request, 'Airport Route deleted successfully')
        return redirect('add_route')


# Search Nth Node View
class SearchNthNode(TemplateView):
    template_name = 'search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SearchNthNodeForm()
        context['result'] = kwargs.get('result', None)
        context['path'] = kwargs.get('path', [])
        return context
    
    def post(self, request, *args, **kwargs):
        form = SearchNthNodeForm(request.POST)
        result = None
        path = []

        if form.is_valid():
            airport = form.cleaned_data['airport']
            direction = form.cleaned_data['direction']
            nth_position = form.cleaned_data['nth_position']

            current = airport
            path.append({'airport': current, 'duration': 0})
            total_duration = 0

            for i in range(nth_position):
                try:
                    route = Route.objects.get(
                        from_airport=current,
                        position=direction
                    )
                    current = route.to_airport
                    total_duration += route.duration
                    path.append({
                        'airport': current,
                        'duration': route.duration,
                        'total_duration': total_duration
                    })
                except Route.DoesNotExist:
                    messages.warning(request, f"Cannot find {nth_position}th {direction} node")
                    break
            else:
                if current:
                    result = {
                        'airport_code': current.code,
                        'airport_name': current.name,
                        'total_duration': total_duration
                    }
                messages.success(
                    request,
                    f"Found {nth_position}th {direction} node: {current.name} "
                    f"(Total duration: {total_duration} mins)"
                )

        context = self.get_context_data(form=form, result=result, path=path)
        return self.render_to_response(context)


# Shortest Node
class ShortestNode(TemplateView):
    template_name = 'shortest_node.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs.get('form', ShortestNodeForm())
        context['result'] = kwargs.get('result', None)
        context['path'] = kwargs.get('path', [])
        context['error_message'] = kwargs.get('error_message', None)
        return context
    
    def post(self, request, *args, **kwargs):
        form = ShortestNodeForm(request.POST)
        result = None
        path_details = []
        error_message = None

        if form.is_valid():
            start = form.cleaned_data['from_airport']
            end = form.cleaned_data['to_airport']

            result_data = self.bfs_shortest_path(start, end)

            if result_data:
                result = {
                    'total_duration': result_data['total_duration'],
                    'path': result_data['path'],
                    'num_hops': len(result_data['path']) - 1,
                    'path_display': " → ".join(result_data['path']),
                }
                path_details = result_data['path_details']
                messages.success(
                    request,
                    f"Shortest path found: {result['path_display']} "
                    f"({result['total_duration']} mins)"
                )
            else:
                error_message = "No path found between these airports"
                messages.warning(request, error_message)

        context = self.get_context_data(
            form=form,
            result=result,
            path=path_details,
            error_message=error_message
        )
        return self.render_to_response(context)

    def bfs_shortest_path(self, start_airport, end_airport):
        """
        BFS algorithm to find shortest path by duration between two airports
        """
        queue = deque([(start_airport, 0, [start_airport.name], [])])
        visited = set()

        while queue:
            current, duration, path, details = queue.popleft()
            if current == end_airport:
                return {
                    'total_duration': duration,
                    'path': path,
                    'path_details': details
                }

            if current.id in visited:
                continue
            visited.add(current.id)

            routes = Route.objects.filter(from_airport=current).select_related('to_airport')

            for route in routes:
                if route.to_airport.id not in visited:
                    new_duration = duration + float(route.duration)
                    new_path = path + [route.to_airport.name]
                    new_details = details + [{
                        'from_airport': route.from_airport.name,
                        'to_airport': route.to_airport.name,
                        'duration': route.duration,
                        'position': route.position
                    }]
                    queue.append((
                        route.to_airport,
                        new_duration,
                        new_path,
                        new_details
                    ))
        return None
