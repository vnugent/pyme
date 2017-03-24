from hawkular.metrics import HawkularMetricsClient, MetricType, HawkularMetricsError

import json, sys, ssl, urllib2
from datetime import datetime, timedelta

epoch = datetime.utcfromtimestamp(0)

#host = 'hawkular-services-openshift-infra.origin.cloud1.hawkular.org'
host= 'hawkular-metrics-openshift-infra.cloud2.jonqe.lab.eng.bos.redhat.com'
path = 'hawkular/metrics'
port = '443'
username = 'hawkular'
#os1
#password = 'gGmfVlFB0tfby_r'
#cluster2
password = 'kw35ccAXWLi5hTC'
tenant_id='promgen'


ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

client = HawkularMetricsClient(username=username,
                               password=password,
                               tenant_id=tenant_id,
                               scheme='https',
                               host=host,
                               path=path,
                               port=port,
                               context=ctx)

defs = client.query_metric_definitions(custom_metric='true')

TypeMap = {
    'counter': MetricType.Counter,
    'gauge': MetricType.Gauge,
    'string': MetricType.String
}


def to_type(short_type):
    return TypeMap.get(short_type, short_type)


def unix_time_millis(dt):
    return '{:.0f}'.format((dt - epoch).total_seconds() * 1000)


def metric_definitions_by_pod():
    pods = {}
    counter = 0
    for item in defs:
        if 'tags' in item:
            tags = item['tags']
            pod_full_name = "{}/{}".format(tags['pod_namespace'], tags['pod_name'])
            counter += 1
            entry = {
                'id': item['id'],
                'type': item['type']
            }

            if pod_full_name in pods:  # entry exists so we just append new metric id
                pods[pod_full_name]['metrics'].append(entry)
            else:
                pods[pod_full_name] = {'metrics': [entry]}
        else:
            pass
    return pods


def metric_data_by_pod(pods):
    counter = 0
    total = len(pods.items())
    percent_completed = 0
    for key, value in pods.items():
        metrics = value['metrics']
        counter += 1
        percent_completed = int(round((counter / float(total)) * 100))
        if percent_completed % 10 == 0:
            print 'Progress {}% ({}/{})'.format(percent_completed, counter, total)

        for m in metrics:
            try:
                now = datetime.utcnow()
                end = unix_time_millis(now - timedelta(minutes=30))
                start = unix_time_millis(now - timedelta(minutes=61))

                data = client.query_metric(to_type(m['type']), urllib2.quote(m['id']), start=start, end=end)
                m['data_count'] = len(data)
            except HawkularMetricsError:
                e = sys.exc_info()[1]
                print e
                m['data_count'] = -1
    return pods


if __name__ == "__main__":
    pods = metric_definitions_by_pod()
    #print(json.dumps(pods, indent=2))
    #print(pods)
    print "Number of pods: {}".format(len(pods))

    pods_with_data = metric_data_by_pod(pods)

    print json.dumps(pods_with_data, indent=4)