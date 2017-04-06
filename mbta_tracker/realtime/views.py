from django.http import HttpResponseRedirect
from django.shortcuts import render, get_list_or_404
from django.views import generic
from .models import Station
import googlemaps
import json

ROUTES = 'routes'
LEGS = 'legs'
DISTANCE = 'distance'
DURATION = 'duration'
ARRIVAL_TIME = 'arrival_time'
DEPARTURE_TIME = 'departure_time'
TEXT = 'text'
VALUE = 'value'
KEY = 'AIzaSyB188mNwiom1mDWU9JlpLyWQRRISq8ghjE'


class IndexView(generic.ListView):
    template_name = 'realtime/index.html'
    context_object_name = 'stations'

    def get_queryset(self):
        return get_list_or_404(Station.objects.order_by('name'))


def submit(request):

    if request.POST['origin'] is None or request.POST['destination'] is None:
        return render(request,
                      "realtime/index.html",
                      {'stations': get_list_or_404(Station.objects.order_by('name')),
                       'error_message': "Invalid selection. Please try again."}
                      )

    transit_tag = ' station, Boston, MA'
    driving_tag = ', Boston, MA'

    gmaps = googlemaps.Client(key=KEY)

    try:
        origin = Station.objects.get(id=request.POST['origin'])
        destination = Station.objects.get(id=request.POST['destination'])
    except (KeyError, ValueError, Station.DoesNotExist):
        return render(request,
                      "realtime/index.html",
                      {'stations': get_list_or_404(Station.objects.order_by('name')),
                       'error_message': "Invalid selection. Please try again."}
                      )
    else:
        # print('origin: {}'.format(origin.name))
        # print('destination: {}'.format(destination.name))

        transit_directions = gmaps.directions(origin.name + transit_tag,
                                              destination.name + transit_tag,
                                              mode='transit',
                                              departure_time='now')
        driving_directions = gmaps.directions(origin.name + driving_tag,
                                              destination.name + driving_tag,
                                              mode='driving',
                                              departure_time='now')
        walking_directions = gmaps.directions(origin.name + driving_tag,
                                              destination.name + driving_tag,
                                              mode='walking',
                                              departure_time='now')

        bicycling_directions = gmaps.directions(origin.name + driving_tag,
                                              destination.name + driving_tag,
                                              mode='bicycling',
                                              departure_time='now')

        transit_distance = transit_directions[0][LEGS][0][DISTANCE]
        driving_distance = driving_directions[0][LEGS][0][DISTANCE]
        walking_distance = walking_directions[0][LEGS][0][DISTANCE]
        bicycling_distance = bicycling_directions[0][LEGS][0][DISTANCE]

        transit_duration = transit_directions[0][LEGS][0][DURATION]
        driving_duration = driving_directions[0][LEGS][0][DURATION]
        walking_duration = walking_directions[0][LEGS][0][DURATION]
        bicycling_duration = bicycling_directions[0][LEGS][0][DURATION]

        transit_departure = transit_directions[0][LEGS][0][DEPARTURE_TIME]
        transit_arrival = transit_directions[0][LEGS][0][ARRIVAL_TIME]

        params = {'transit_distance': transit_distance[TEXT],
                  'driving_distance': driving_distance[TEXT],
                  'walking_distance': walking_distance[TEXT],
                  'transit_duration': transit_duration[TEXT],
                  'driving_duration': driving_duration[TEXT],
                  'walking_duration': walking_duration[TEXT],
                  'transit_departure': transit_departure[TEXT],
                  'transit_arrival': transit_arrival[TEXT],
                  'bicycling_distance': bicycling_distance[TEXT],
                  'bicycling_duration': bicycling_duration[TEXT],
                  'origin': origin.name.replace(' ', '+'),
                  'destination': destination.name.replace(' ', '+'),
                  'key': KEY,

                  }

        return render(request, "realtime/result.html", params)

