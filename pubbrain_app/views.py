from django.shortcuts import get_object_or_404, render_to_response, render, redirect
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
# from PubBrain.utils import *
from django.contrib.admin.utils import unquote, quote
from django.template import RequestContext, loader
from scripts.pubbrain_search import *
from models import *
import util
import scripts.pubbrain_search
# from statsmodels.tsa.vector_ar.tests.example_svar import mymodel
from django_datatables_view.base_datatable_view import BaseDatatableView

class anatomyCount():
    name=''
    count=-1
    def __init__(self,name,count,regionalPmids):
        self.name=name
        self.count=count
        self.name_query=name.replace(" ","+")
        self.regionalPmids='+OR+'.join(regionalPmids)

def sortDict(dict):
    " return set of dict keys sorted based on values"
    keys=dict.keys()
    values=[dict[key] for key in keys]
    sorted_values=sorted(range(len(values)), key = values.__getitem__)[::-1]
    return [keys[k] for k in sorted_values]

# Create your views here.
def index(request):
#     query='hippocampus'
#     q=get_pubmed_query_results(query)
#     m=get_matching_pmids(q)
#          
#     c,regionalPmids=get_anatomy_count(m)
#     imgfile=mk_image_from_anatomy_count(c,query)
#     regions=[]
#     anatkeys=sortDict(c)
#     for region in anatkeys:
#         regions.append(anatomyCount(region,c[region],regionalPmids[region]))
#     template=loader.get_template('pubbrain_app/index.html')
#     context=RequestContext(request,{'query_results':regions,'query':query,
#                                     'img_max':max(c.values()),'file_name':'%s'%imgfile})
#     return HttpResponse(template.render(context))
    return HttpResponse('Welcome to PubBrain')

def papaya_js_embed(request,pk, iframe=None):
    tpl = 'papaya_embed.tpl.js'
    mimetype = "text/javascript"
    if iframe is not None:
        tpl = 'papaya_frame.html.haml'
        mimetype = "text/html"
    searchObject = PubmedSearch.objects.get(pk=pk)
    context = {'searchObject': searchObject, 'request':request}
    return render_to_response(tpl,
                              context, content_type=mimetype)
def search(request):
    search = request.GET.get('search')
    try:
        searchObject = PubmedSearch.objects.get(query=search)
    except:
        searchObject = pubbrain_search(search)
    template = 'pubbrain_search.html'
    context = {'searchObject':searchObject}
    return render(request, template, context)

def get_tree_data(qs, max_level):
        pk_attname = BrainRegion._meta.pk.attname
        return util.get_tree_from_queryset(qs,max_level=max_level)


def tree_json_view(request):
        node_id = request.GET.get('node')
        query = request.GET.get('query')
        searchObject = PubmedSearch.objects.filter(query=query)[0]
        
        if node_id:
            node = BrainRegion.objects.get(pk=node_id)
            max_level = node.level + 1
        else:
            max_level = 1

        qs = util.get_tree_queryset(
            model=BrainRegion,
            node_id=node_id,
            searchObject=searchObject,
            max_level=max_level,
        )

        tree_data = get_tree_data(qs, max_level)
        return util.JsonResponse(tree_data)

class OrderListJson(BaseDatatableView):
    model = BrainRegion
    columns = ['name','number of hits']
    max_display_length = 500
    
    def render_column(self, row, column):
        return super(OrderListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
#         searchObject = self.context.GET.get('searchObject')
        search = self.request.GET.get('search')
        searchObject = PubmedSearch.objects.get(query=search)
        if searchObject:
            qs = searchObject.brain_regions.all()
        return qs
        