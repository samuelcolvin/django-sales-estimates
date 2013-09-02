import settings
import inspect, json

class ModelDisplay:
    extra_funcs = ()
    tables = []
    display = True
    
class ModelDisplayMeta:
    orderable = False
    attrs = {'class': 'item_list'}
    per_page=100

def get_display_apps():
    display_modules = map(lambda m: __import__(m + '.display'), settings.DISPLAY_APPS)
    apps={}
    for dm in display_modules:
        apps[dm.__name__] = {}
        for ob_name in dir(dm.display):
            ob = getattr(dm.display, ob_name)
            if does_inherit(ob, 'ModelDisplay'):
                apps[dm.__name__][ob_name] = _process_display(dm, ob_name)
    return apps

def does_inherit(ob, parent):
    return inspect.isclass(ob) and parent in map(lambda c: c.__name__, inspect.getmro(ob)[1:])
                    
def _process_display(dm, ob_name):
    if not hasattr(dm.models, ob_name):
        raise Exception('%s does not have a model called %s' % (dm.__name__, ob_name))
    display = getattr(dm.display, ob_name)
    display.model = getattr(dm.models, ob_name)
    display.app_parent = dm.__name__
    return display

def json_apps(apps):
    return json.dumps(apps, cls=_AppEncode, sort_keys=True, indent=4, separators=(',', ': '))

class _AppEncode(json.JSONEncoder):
    def default(self, obj):
        if inspect.isclass(obj):
            return dir(obj)
        return json.JSONEncoder.default(self, dir(obj))