
# -*- coding: utf-8 -*-

import os
import sys
import logging
import requests
import optparse

# Setup logging format for the file
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpc-client.log'),
    level=logging.INFO)
# Adding STDERR output
logging.getLogger().addHandler(logging.StreamHandler())

artifactory_url = 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-rpc/{version}/corda-rpc-{version}.jar'
deps = {
    'kotlin-stdlib-1.3.71.jar' : 'https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-stdlib/1.3.71/kotlin-stdlib-1.3.71.jar',
    'corda-serialization-{version}.jar': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-serialization/{version}/corda-serialization-{version}.jar',
    'corda-node-api-{version}.jar': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-node-api/{version}/corda-node-api-{version}.jar',
    'corda-core-{version}.jar' : 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-core/{version}/corda-core-{version}.jar',
    'corda-rpc-{version}.jar': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-rpc/{version}/corda-rpc-{version}.jar',
    'corda-{version}.jar': 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda/{version}/corda-{version}.jar',
    'guava-28.2-jre.jar': 'https://repo1.maven.org/maven2/com/google/guava/guava/28.2-jre/guava-28.2-jre.jar',
    'slf4j-api-2.0.0-alpha1.jar': 'https://repo1.maven.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha1/slf4j-api-2.0.0-alpha1.jar',
    'caffeine-2.8.1.jar': 'https://repo1.maven.org/maven2/com/github/ben-manes/caffeine/caffeine/2.8.1/caffeine-2.8.1.jar',
    'classgraph-4.8.69.jar': 'https://repo1.maven.org/maven2/io/github/classgraph/classgraph/4.8.69/classgraph-4.8.69.jar',
    # 'proton-j-0.7.jar': 'https://repo1.maven.org/maven2/org/apache/qpid/proton-j/0.7/proton-j-0.7.jar',
    'proton-j-0.33.4.jar': 'https://repo1.maven.org/maven2/org/apache/qpid/proton-j/0.33.4/proton-j-0.33.4.jar',
    'artemis-core-client-2.11.0.jar': 'https://repo1.maven.org/maven2/org/apache/activemq/artemis-core-client/2.11.0/artemis-core-client-2.11.0.jar',
    'javax.json-api-1.1.4.jar': 'https://repo1.maven.org/maven2/javax/json/javax.json-api/1.1.4/javax.json-api-1.1.4.jar',
    'artemis-commons-2.11.0.jar': 'https://repo1.maven.org/maven2/org/apache/activemq/artemis-commons/2.11.0/artemis-commons-2.11.0.jar',
    'jboss-logging-3.4.1.Final.jar': 'https://repo1.maven.org/maven2/org/jboss/logging/jboss-logging/3.4.1.Final/jboss-logging-3.4.1.Final.jar',
    'commons-lang3-3.10.jar': 'https://repo1.maven.org/maven2/org/apache/commons/commons-lang3/3.10/commons-lang3-3.10.jar',
    'eddsa-0.3.0.jar': 'https://repo1.maven.org/maven2/net/i2p/crypto/eddsa/0.3.0/eddsa-0.3.0.jar',
    'bcprov-jdk15on-1.65.jar': 'https://repo1.maven.org/maven2/org/bouncycastle/bcprov-jdk15on/1.65/bcprov-jdk15on-1.65.jar',
    # 'org.apache.servicemix.bundles.bcprov-jdk16-1.46_3.jar': 'https://repo1.maven.org/maven2/org/apache/servicemix/bundles/org.apache.servicemix.bundles.bcprov-jdk16/1.46_3/org.apache.servicemix.bundles.bcprov-jdk16-1.46_3.jar',
    'commons-beanutils-1.9.4.jar': 'https://repo1.maven.org/maven2/commons-beanutils/commons-beanutils/1.9.4/commons-beanutils-1.9.4.jar',
    'commons-logging-1.2.jar': 'https://repo1.maven.org/maven2/commons-logging/commons-logging/1.2/commons-logging-1.2.jar',
    'kotlin-reflect-1.3.72.jar': 'https://repo1.maven.org/maven2/org/jetbrains/kotlin/kotlin-reflect/1.3.72/kotlin-reflect-1.3.72.jar',
    # 'concrete-rx-observable-0.4.1.jar': 'https://repo1.maven.org/maven2/org/coodex/concrete-rx-observable/0.4.1/concrete-rx-observable-0.4.1.jar'
    'rxjava-1.0.2.jar': 'https://repo1.maven.org/maven2/io/reactivex/rxjava/1.0.2/rxjava-1.0.2.jar',
    # 'netty-all-5.0.0.Alpha2.jar': 'https://repo1.maven.org/maven2/io/netty/netty-all/5.0.0.Alpha2/netty-all-5.0.0.Alpha2.jar',
    'netty-all-4.1.49.Final.jar': 'https://repo1.maven.org/maven2/io/netty/netty-all/4.1.49.Final/netty-all-4.1.49.Final.jar',
    'failureaccess-1.0.jar': 'https://repo1.maven.org/maven2/com/google/guava/failureaccess/1.0/failureaccess-1.0.jar'
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
        'port': opts.port,
        'username': opts.username,
        'password': opts.password
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
    from net.corda.core.utilities import NetworkHostAndPort

    rpcAddress = NetworkHostAndPort(opts.hostname, opts.port)
    logging.info("Connecting to {0}".format(rpcAddress))
    # client = CordaRPCClient(HostAndPort.fromString('{host}:{port}'.format(**params)), None, None)
    client = CordaRPCClient(rpcAddress)
    logging.info("RPC client created. Starting Auth process")
    proxy = client.start(opts.username, opts.password).proxy
    # logging.info("Getting proxy object")
    # proxy = client.proxy
    txs = proxy.verifiedTransactions().first

    print "There are %s 'unspent' IOUs on 'NodeA'" % (len(txs))

    if len(txs):
        for txn in txs:
            print(txn.tx.outputs[0].data.iou)

if __name__ == '__main__':
    sys.exit(main())
