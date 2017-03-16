from hawkular.metrics import HawkularMetricsClient, MetricType

host = 'hawkular-services-openshift-infra.origin.cloud1.hawkular.org'
path = 'hawkular/metrics'
port = '443'
token = 'mzdo3k26Nkn8i7lPccBNBnsJzoAN0e1jJGqpW9Donkk'
tenant_id='promgen'

if __name__ == "__main__":
    client = HawkularMetricsClient(token=token, tenant_id=tenant_id, scheme='https', host=host, path=path, port=port)
    definition = client.query_metric_definitions(custom_metric='true')
    meta = []
    for item in definition:
        metric_type = item['type']
        metric_id = item['id']
        print "id: {}, item: {}".format(metric_id, metric_type)
        if metric_type == 'counter':
            # it would be nice to pass metric_type directly to query_metric()
            # data = client.query_metric(metric_type, metric_id);
            data = client.query_metric(MetricType.Counter, metric_id);
            print data
            break
