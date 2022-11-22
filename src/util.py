import sys
import os

def keyboard_shutdown():
    print('Interrupted\n')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

def createInspectionArea(document):
    inspection_area = []
    for i in range(len(document['fullDocument']['area'])):
        inspection_area.append(
            {
                'lat': document['fullDocument']['area'][i]['lat'],
                'lon': document['fullDocument']['area'][i]['lon']
            })
    return inspection_area
