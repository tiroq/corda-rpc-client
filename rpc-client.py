
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import logging
import requests
import optparse
import importlib

__version__ = '0.2.1'

# Setup logging format for the file
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpc-client.log'),
    level=logging.INFO)
# Adding STDERR output
logging.getLogger().addHandler(logging.StreamHandler())

artifactory_url = 'https://ci-artifactory.corda.r3cev.com/artifactory/corda-releases/net/corda/corda-rpc/{version}/corda-rpc-{version}.jar'

def main():
    options = optparse.OptionParser(usage='%prog [options]', description='corda rpc injector')
    options.add_option('--hostname', type='str', default='127.0.0.1', help='hostname')
    options.add_option('--port', type='int', default=6789, help='port')
    options.add_option('--username', type='str', default='corda', help='username')
    options.add_option('--password', type='str', default='password', help='password')
    options.add_option('--version', type='str', default='4.4', help='corda version')
    options.add_option('--dependencies_config', type='str', default='.gdeps.yaml', help='file with all required dependencies')
    # options.add_option('--amount', type='float', default=55.00, help='amount')

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
    deps = yaml.load(open(opts.dependencies_config))
    logging.info("Required {0} dependencies. Start loading them ...".format(len(deps['libs'])))
    for dependency in deps['libs']:
        jar_name = dependency['name']
        logging.debug('Start working with dependency: {0}'.format(dependency))
        full_jar_name = jar_name.format(**params)
        jlib = os.path.join(jlibs, full_jar_name)
        if not os.path.exists(jlib):
            url = dependency['link'].format(**params)
            logging.info("Download {0} lib".format(full_jar_name))
            with open(jlib, 'wb') as lib_file:
                lib_file.write(requests.get(url).content)
        else:
            logging.debug('Already downloaded: {0}'.format(full_jar_name))
        sys.path.append(jlib)
        if 'class' in dependency:
            _classes = dependency['class']
            classes = []
            if isinstance(_classes, basestring):
                classes = [_classes]
            elif isinstance(_classes, list):
                classes = _classes
            for _class in classes:
                class_name = _class.split('.')[-1]
                logging.info('Loading {0} class.'.format(_class))
                globals()[class_name] = __import__(_class.rsplit('.', 1)[0], {}, {}, [class_name], 0)

    rpcAddress = NetworkHostAndPort(opts.hostname, opts.port)
    logging.info("Connecting to {0}".format(rpcAddress))
    client = CordaRPCClient(rpcAddress)
    logging.info("RPC client created. Starting Auth process")
    proxy = client.start(opts.username, opts.password).proxy
    print dir(proxy)
    # txs = proxy.verifiedTransactions().first
    vault = proxy.vaultQueryBy(QueryCriteria.VaultQueryCriteria(), PageSpecification(), Sort([]), Cash.State).states
    print vault
    print proxy.stateMachinesSnapshot()
    print proxy.networkMapSnapshot()
    print "There are %s 'unspent' IOUs on 'NodeA'" % (len(txs))

    if len(txs):
        for txn in txs:
            print(txn.tx.outputs[0].data.iou)

if __name__ == '__main__':
    sys.exit(main())
