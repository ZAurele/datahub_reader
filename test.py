from datapackage import Package

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook

from datetime import datetime

import json

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

ext = 'csv'

DATA = {
         'global-temp':
            {
                'label':'Global temperature evolution',
                'files':
                    {
                        'monthly':
                            {
                                'format': 
                                    {
                                        'name':0,
                                        'x':1,
                                        'y':2
                                    },
                                 'label':'Relative mean temperature'
                            }
                    }
            },
         'sea-level-rise':
            {
                'label':'Sea level rise',
                'files':
                    {
                        'csiro_recons_gmsl_mo_2015':
                            {
                                'format': 
                                    {
                                        'x':0,
                                        'y':1
                                    },
                                 'label':'Relative mean sea level'
                            }
                    }
            },
         'co2-fossil-global':
            {
                'label':'Global CO2 Emissions from Fossil Fuels (Solid fuel)',
                'files':
                    {
                        'global':
                            {
                                'format': 
                                    {
                                        'x':0,
                                        'y':4,
                                        'x_type': 'year_int'
                                    },
                                 'label':'Relative global CO2 emission'
                            }
                    }
            },
         'co2-ppm':
            {
                'label':'CO2 PPM - Trends in Atmospheric Carbon Dioxide',
                'files':
                    {
                        'co2-mm-mlo':
                            {
                                'format': 
                                    {
                                        'x':0,
                                        'y':3
                                    },
                                 'label':'Relative atmospheric CO2'
                            }
                    }
            }
       }

colors = ['red','blue','black','green']

DATASETS = {}
for data_type, infos in DATA.items():
    files = infos['files']
    package = Package('https://datahub.io/core/%s/datapackage.json'%data_type)

    # print list of all resources:
    print(package.resource_names)

    dataset = {}

    # print processed tabular data (if exists any)
    for resource in package.resources:
        if resource.descriptor['datahub']['type'] == 'derived/csv':
            object = resource.descriptor
            name = object['name']
            rows_count = object['rowcount']
            
            rows = resource.read()
            short_name = name.replace('_' + ext,'')
            
            wrong_format = False
            if short_name in files:
                #print(resource.descriptor)
                format = files[short_name]['format']
                label = files[short_name]['label']
                
                j = 0
                for row in rows:
                    if 'name' in format:
                        key = row[format['name']]
                    else:
                        key = ''
                        
                    current_date    = row[format['x']]
                    value           = row[format['y']]
                    
                    if 'x_type' in format:
                        if format['x_type'] == 'year_int':
                            current_date = datetime.strptime(str(current_date), '%Y')
                    
                    if not key in dataset:
                        dataset[key] = {'x':[],'y':[],'label':label}
                    dataset[key]['x'].append(current_date)
                    dataset[key]['y'].append(float(value))
                    j += 1
            else:

                print('%s / %s: Unknowned format: %s'%(data_type,name,rows[0]))
                        
    DATASETS[data_type] = dataset

fig, host = plt.subplots()

output = 'datasets.json'
JSON_OUTPUT = {}
for data_type, dataset in DATASETS.items():
    JSON_OUTPUT[data_type] = {}
    for source, values in dataset.items():
        JSON_OUTPUT[data_type]['x'] = []
        JSON_OUTPUT[data_type]['y'] = []
        JSON_OUTPUT[data_type]['source'] = source
        
        x, y = values['x'], values['y']
        
        for i in range(len(x)):
            JSON_OUTPUT[data_type]['x'].append(str(x[i]))
            JSON_OUTPUT[data_type]['y'].append(y[i])
    
with open(output,'w') as f:
    json.dump(JSON_OUTPUT, f)

plots = []

i = 0
j = 0
offset = 1.2
offset_add = 0.2
for data_type, dataset in DATASETS.items():
    k = 0
    for source, values in dataset.items():
        if k == 0:
            x, y = values['x'], values['y']
            print(x[0],' : ',type(x[0]))
            label = "%s: %s"%(data_type,source) if source != '' else data_type
            
            if i == 0:
                axe = host
            else:
                axe = host.twinx()
            if i > 1:
                axe.spines["right"].set_position(("axes", offset))
                make_patch_spines_invisible(axe)
                axe.spines["right"].set_visible(True)
                offset += offset_add
            
            axe.set_ylabel(values['label'])
            
            PLT,  = axe.plot(x,y, label=label, color=colors[j])
            axe.yaxis.label.set_color(PLT.get_color())
            axe.tick_params(axis='y', colors=PLT.get_color())
            plots.append(PLT)
            j += 1
            k += 1
    i += 1
    
fig.subplots_adjust(right=0.5)
        
# beautify the x-labels
plt.gcf().autofmt_xdate()

host.set_xlabel('Date')
host.legend(plots, [l.get_label() for l in plots])

plt.show()