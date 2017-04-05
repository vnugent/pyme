from hawkular.metrics import HawkularMetricsClient, MetricType, HawkularMetricsError, HawkularMetricsConnectionError
import ssl
import urllib2

from datetime import datetime, timedelta


import main


class Analytics:

    def __init__(self, host='hawkular-full-hs', scheme='http', path='hawkular/metrics', username='jdoe', password='password', authtoken=None):
        if scheme == 'https':
            port = '443'
        else:
            port = '80'

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.client = HawkularMetricsClient(username=username,
                                            password=password,
                                            scheme=scheme,
                                            host=host,
                                            path=path,
                                            port=port,
                                            context=ctx,
                                            tenant_id='qe-cluster',
                                            authtoken=authtoken)

        self.smoke_test()
        self.definitions = []

    def smoke_test(self):
        tenants = self.client.query_tenants()
        print tenants
        #self.client.create_tenant('qe-cluster')

    def create_gauge_definition(self, definitions):
        self.definitions = definitions # cache definitions
        for item in definitions:
            self.client.create_metric_definition(MetricType.Gauge, item['id'], **item['tags'])

    def tally_metrics(self):
        running_start = datetime(2017, 04, 2, 02, 00, 00)
        running_end = running_start + timedelta(minutes=15)
        for multiplier in range(1, 20):
            self._tally_metrics_by_timerange(running_start, running_end)
            running_start = running_end
            running_end = running_end + timedelta(minutes=15)

    def _tally_metrics_by_timerange(self, start, end):
        print '{} -> {}'.format(start, end)

        for item in self.definitions:
            count = 0
            try:
                data = main.client.query_metric(main.to_type(item['type']),
                                            urllib2.quote(item['id']),
                                            start=start,
                                            end=end)
                count = len(data)
            except (HawkularMetricsError, HawkularMetricsConnectionError) as e:
                e = sys.exc_info()[1]
                print e
                count = -1

            print '{}: {}'.format(item['tags']['pod_name'], count)
            self.client.push(MetricType.Gauge, item['id'], count, start)


if __name__ == "__main__":
    authtoken='XohImNooBHFR0OVvjcYpJ3NgPQ1qq73WKhHvch0VQtg='
    host = 'hawkular-services-analytics.cloud2.jonqe.lab.eng.bos.redhat.com'
    analytics = Analytics(host=host, authtoken=authtoken)

    metrics = main.get_flat_metric_definitions()
    analytics.definitions = metrics  # cache definitions

    #analytics.create_gauge_definition(metrics)

    analytics.tally_metrics()



