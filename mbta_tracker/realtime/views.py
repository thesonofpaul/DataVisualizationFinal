from django.shortcuts import render, get_list_or_404
from django.views import generic
from .models import Station
import googlemaps

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
    if request.POST['origin'] is None or request.POST['destination'] is None or request.POST['origin'] == request.POST['destination']:
        return render(request,
                      "realtime/index.html",
                      {'stations': get_list_or_404(Station.objects.order_by('name')),
                       'error_message': "Invalid selection. Please try again."}
                      )

    tag = ' Station, Boston, MA'

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

        transit_directions = gmaps.directions(origin.name + tag,
                                              destination.name + tag,
                                              mode='transit',
                                              departure_time='now')
        driving_directions = gmaps.directions(origin.name + tag,
                                              destination.name + tag,
                                              mode='driving',
                                              departure_time='now')
        walking_directions = gmaps.directions(origin.name + tag,
                                              destination.name + tag,
                                              mode='walking',
                                              departure_time='now')

        bicycling_directions = gmaps.directions(origin.name + tag,
                                                destination.name + tag,
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

        shortest_duration = analyze_duration(transit_duration[VALUE],
                                             driving_duration[VALUE],
                                             walking_duration[VALUE],
                                             bicycling_duration[VALUE])

        params = {'transit_distance': transit_distance[TEXT],
                  'driving_distance': driving_distance[TEXT],
                  'walking_distance': walking_distance[TEXT],
                  'transit_duration': transit_duration[TEXT],
                  'driving_duration': driving_duration[TEXT],
                  'walking_duration': walking_duration[TEXT],
                  'bicycling_distance': bicycling_distance[TEXT],
                  'bicycling_duration': bicycling_duration[TEXT],
                  'origin': origin.name,
                  'destination': destination.name,
                  'key': KEY,
                  'shortest_duration': shortest_duration,
                  }

        return render(request, "realtime/result.html", params)


def analyze_duration(transit_duration, driving_duration, walking_duration, bicycling_duration):
    TIME_DIFF = 300
    result = []

    min_duration = min(transit_duration, driving_duration, walking_duration, bicycling_duration)

    if min_duration == driving_duration:
        result.append('driving')
    elif min_duration == transit_duration:
        result.append('transit')
    elif min_duration == walking_duration:
        result.append('walking')
    elif min_duration == bicycling_duration:
        result.append('bicycling')

    if 'walking' not in result and abs(walking_duration - min_duration) < TIME_DIFF:
        result.append('walking')
    if 'bicycling' not in result and abs(bicycling_duration - min_duration) < TIME_DIFF:
        result.append('bicycling')
    if 'transit' not in result and abs(transit_duration - min_duration) < TIME_DIFF:
        result.append('transit')
    if 'driving' not in result and abs(driving_duration - min_duration) < TIME_DIFF:
        result.append('driving')

    return result
