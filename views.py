from django.shortcuts import render

from .metadata import *
from .utils import *


# Create your views here.
def index(request):
    return render(request, 'index.html')


def personality(request):
    username = request.GET.get("username")
    posts = fetchPosts(username)
    if posts is None:
        return render(request, 'index.html')

    trait, percentage = predict(posts)
    print(trait)
    data = metadata[trait]
    data['trait'] = trait
    user = api.get_user(username)
    data['username'] = username

    data['name'] = user.name
    data['profile_image'] = user.profile_image_url_https.replace("_normal", "")
    data['location'] = user.location
    data['profile_description'] = user.description
    data['percentages'] = percentage
    return render(request, 'personality.html', data)
