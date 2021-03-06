from django.shortcuts import render_to_response, get_list_or_404
from unittestweb.viewer.models import Builds, Trees, Tests, OS_CHOICES, get_most_failing_tests

def index(request):
  failures = get_list_or_404(Tests.objects.all().order_by('-build__starttime')[:10])
  return render_to_response('viewer/index.html', {'failures': failures})

def trees(request):
  alltrees = Trees.objects.all().order_by('name')
  return render_to_response('viewer/trees.html', {'trees': alltrees})

def tree(request, tree):
  newestbuilds = get_list_or_404(Builds.objects.filter(tree__name__exact=tree).order_by('-starttime')[:5])
  return render_to_response('viewer/tree.html', {'tree': tree, 'newestbuilds': newestbuilds})

def changesets(request):
  build_csets = Builds.objects.values('changeset').distinct()
  return render_to_response('viewer/changesets.html', {'changesets': [b['changeset'] for b in build_csets]})

def changeset(request, changeset):
  builds = get_list_or_404(Builds, changeset__exact=changeset)
  return render_to_response('viewer/changeset.html', {'changeset': changeset, 'builds': builds})

def tests(request):
    test_names = Tests.objects.values('name').distinct()
    return render_to_response('viewer/tests.html', {'tests': [t['name'] for t in test_names]})

def test(request):
  failures = get_list_or_404(Tests.objects.filter(name__exact=request.GET['name']).order_by('-build__starttime'))
  return render_to_response('viewer/test.html', {'test': request.GET['name'], 'failures': failures})

def topfails(request):
  failures = get_most_failing_tests()
  return render_to_response('viewer/topfails.html', {'failures': failures})
  
def timeline(request):
  name = request.GET['name']
  builds = get_list_or_404(Builds, tests__name__exact=name)
  buildlist = []
  desc_list = []
  for b in builds:
    descs = b.tests_set.filter(name__exact=name).order_by('id')
    desc = '\n'.join(descs.values_list('description', flat=True))
    if desc not in desc_list:
      desc_list.append(desc)
    desc_i = desc_list.index(desc)
    buildlist.append({'build': b,
                      'desctype': desc_i,
                      'description': desc,
                      'os': OS_CHOICES[b.os][1],
                      'time': b.startdate().isoformat() + "Z",
                      })
  return render_to_response('viewer/timeline.html', {'test': name,
                                                     'descriptions': desc_list,
                                                     'builds': buildlist})
