
# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
import optparse

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpc-client.log'),
    level=logging.INFO)

artifactory_url = 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-rpc/{version}/corda-rpc-{version}.jar'
deps = {
    'kotlin-stdlib-1.3.71.jar' : 'https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-stdlib/1.3.71/kotlin-stdlib-1.3.71.jar',
    'corda-core-{version}.jar' : 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-core/{version}/corda-core-{version}.jar',
    'corda-rpc-{version}.jar': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-rpc/{version}/corda-rpc-{version}.jar',
    'guava-28.2-jre.jar': 'https://repo1.maven.org/maven2/com/google/guava/guava/28.2-jre/guava-28.2-jre.jar'
}

def main():
    options = optparse.OptionParser(usage='%prog [options]', description='corda rpc injector')
    options.add_option('--hostname', type='str', default='127.0.0.1', help='hostname')
    options.add_option('--port', type='int', default=6789, help='port')
    options.add_option('--username', type='str', default='corda', help='username')
    options.add_option('--password', type='str', default='password', help='password')
    options.add_option('--version', type='str', default='4.4', help='corda version')
    # options.add_option('--action', type='str', default='cash_issue_flow', help='action')
    # options.add_option('--amount', type='float', default=55.00, help='amount')
    # options.add_option('--currency', type='str', default='USD', help='currency')
    # options.add_option('--recipient', type='str', default='Party2', help='recipient')
    # options.add_option('--issuer_ref', type='str', default='1234', help='issuer_ref')
    # options.add_option('--notary', type='str', default='Notary', help='notary')

    opts, args = options.parse_args()

    params = {
        'version': opts.version,
        'host': opts.hostname,
        'port': opts.port
    }

    jlibs = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jlibs')
    if not os.path.exists(jlibs):
        logging.info("Creating directory for rpc libs")
        os.mkdir(jlibs)

    # add library check
    for jar_name in deps:
        full_jar_name = jar_name.format(**params)
        jlib = os.path.join(jlibs, full_jar_name)
        if not os.path.exists(jlib):
            url = deps[jar_name].format(**params)
            logging.info("Download {0} lib".format(full_jar_name))
            with open(jlib, 'wb') as lib_file:
                lib_file.write(requests.get(url).content)
        sys.path.append(jlib)
    from com.google.common.net import HostAndPort
    from net.corda.client.rpc import CordaRPCClient
    client = CordaRPCClient(HostAndPort.fromString('{host}:{port}'.format(**params)), None, None)
    client.start("user1", "test")
    proxy = client.proxy(None,0)
    print "Proxy is",proxy
    txs = proxy.verifiedTransactions().first

    print "There are %s 'unspent' IOUs on 'NodeA'" % (len(txs))

    if len(txs):
        for txn in txs:
            print(txn.tx.outputs[0].data.iou)

if __name__ == '__main__':
    sys.exit(main())
