__author__ = 'coco'
from django.conf.urls import url
import view.views

urlpatterns = [
    url(r'^showrawlist/$', view.views.rawlist, name="showrawlist"),
    url(r'^showabnormallist/$', view.views.showabnormallist, name="showabnormallist"),
    url(r'^getmiddlelist/$', view.views.getmiddlelist, name="getmiddlelist"),
    url(r'^showmiddlelist/(?P<id>\d+)/$', view.views.showmiddlelist, name="showmiddlelist"),
    url(r'^deletelist/(?P<id>\d+)/$', view.views.deletelist, name="deletelist"),
    url(r'^getapriorilist/$', view.views.getapriorilist, name="getapriorilist"),
    url(r'^showapriorilist/(?P<id>\d+)/$', view.views.showapriorilist, name="showapriorilist"),
    url(r'^apriorifilter/$', view.views.apriorifilter, name="apriorifilter"),
    url(r'^getsimultaneousprocess/$', view.views.getsimultaneousprocess, name="getsimultaneousprocess"),
    url(r'^showresultlist/$', view.views.showresultlist, name="showresultlist"),
    url(r'^showgenelist/(?P<id>\d+)/$', view.views.showgenelist, name="showgenelist"),
    url(r'^calculategenelist/$', view.views.calculategenelist, name="calculategenelist"),
    url(r'^genecalculate/$', view.views.genecalculate, name="genecalculate"),
    url(r'^savegene/$', view.views.savegene, name="savegene"),
    url(r'^uploadsql/$', view.views.uploadsql, name="uploadsql"),
    url(r'^markabnormal/$', view.views.markabnormal, name="markabnormal"),
    url(r'^marknormal/$', view.views.marknormal, name="marknormal"),
    url(r'^showgeneabnormallist/$', view.views.showgeneabnormallist, name="showgeneabnormallist"),
    url(r'^showaprioriabnormallist/$', view.views.showaprioriabnormallist, name="showaprioriabnormallist"),
    url(r'^aprioriexceptfilter/$', view.views.aprioriexceptfilter, name="aprioriexceptfilter"),
    url(r'^showexceptlist/(?P<id>\d+)/$', view.views.showexceptlist, name="showexceptlist"),
    #    url(r'^showmarkovlist/$', view.views.showmarkovlist, name="showmarkovlist"),
]
