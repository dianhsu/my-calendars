import pytz
import requests
from bs4 import BeautifulSoup
import traceback
import os
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vDatetime


def run():
    url = 'https://clist.by'

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        calendars = {}
        for item in soup.select("#list-view #contests .contest"):
            start_time = datetime.strptime(item.select(".start-time a")[0].attrs['href'][58:71], '%Y%m%dT%H%M').replace(
                tzinfo=pytz.utc)

            duration = item.select(".duration")[0].string
            if duration.endswith('days'):
                end_time = start_time + timedelta(days=int(duration.split(' ')[0]))
            elif duration.endswith('months'):
                continue
            elif duration.endswith('years'):
                continue
            else:
                tmp = duration.split(':')
                minutes = 0
                for it in tmp:
                    minutes = minutes * 60 + int(it)
                end_time = start_time + timedelta(minutes=minutes)
            title = item.select('.event .title_search')[0].string
            link = item.select('.event .title_search')[0].attrs['href']
            target = item.select('.event .resource a small')[0].string
            target = target.replace('/', '_')

            if calendars.get(target, None) is None:
                calendars[target] = []
            calendars[target].append({
                'title': title,
                'link': link,
                'start_time': start_time,
                'end_time': end_time,
                'target': target
            })

        for key in calendars.keys():
            cal = Calendar()
            cal.add('prodid', '-//My calendar product//dianhsu.com//')
            cal.add('version', '2.0')
            cal.add('X-WR-TIMEZONE', 'UTC')
            cal.add('X-WR-CALNAME', key)
            cal.add('CALSCALE', 'GREGORIAN')
            cal.add('method', 'PUBLISH')
            for item in calendars[key]:
                event = Event()
                event.add('summary', item['title'])
                event.add('dtstart', item['start_time'])
                event.add('dtend', item['end_time'])
                event.add('description', item['link'])
                event.add('uid', str(item['title']).replace(' ', '') + '@dianhsu.com')
                cal.add_component(event)
            with open(os.path.join('ics', f'{key}.ics'), 'wb') as f:
                f.write(cal.to_ical())
    except:
        traceback.print_exc()
