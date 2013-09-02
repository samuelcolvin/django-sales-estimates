from models import UserSetting
from dateutil import parser as dtparser
import pytz

def get_value(key):
	default_settings={'site_title': 'Child\'s Farm', 'front_page_count': '6'}
	try:
		s = UserSetting.objects.get(key=key).value
	except:
		if key in default_settings:
			s = default_settings[key]
		else:
			raise Exception('No such setting "' + str(key) + '"')
	if key == 'date_example':
		start = dtparser.parse(s).replace(tzinfo=pytz.utc)
		return start
	elif key in ['front_page_count']:
		return int(s)
	elif key.startswith('email'):
		return s.lower() == 'true'
	else:
		return s