
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

def main():
    options = optparse.OptionParser(usage='%prog [options]', description='injector')
    options.add_option('--hostname', type='str', default='127.0.0.1', help='hostname')
    options.add_option('--port', type='int', default=6789, help='port')
    options.add_option('--username', type='str', default='corda', help='username')
    options.add_option('--password', type='str', default='password', help='password')
    options.add_option('--version', type='str', default='4.4', help='repeat_count')
    # options.add_option('--action', type='str', default='cash_issue_flow', help='action')
    # options.add_option('--amount', type='float', default=55.00, help='amount')
    # options.add_option('--currency', type='str', default='USD', help='currency')
    # options.add_option('--recipient', type='str', default='Party2', help='recipient')
    # options.add_option('--issuer_ref', type='str', default='1234', help='issuer_ref')
    # options.add_option('--notary', type='str', default='Notary', help='notary')

    opts, args = options.parse_args()

    params = {
        'version': opts.version
    }

    jlibs = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jlibs')
    if not os.path.exists(jlibs):
        logging.info("Creating directory for rpc libs")
        os.mkdir(jlibs)

    rpc_lib = os.path.join(jlibs, 'corda-rpc-{version}.jar'.format(**params))
    if not os.path.exists(rpc_lib):
        logging.info("Download {version} rpc client".format(**params))
        with open(rpc_lib, 'wb') as rpc_lib_file:
            rpc_lib_file.write(requests.get(artifactory_url.format(**params)).content)

    # add library check
    sys.path.append(rpc_lib)    

if __name__ == '__main__':
    sys.exit(main())
