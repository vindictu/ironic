# Copyright (c) 2017 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect

import mock

from oslo_utils import importutils

from ironic.common import exception
from ironic.drivers import drac as drac_drivers
from ironic.drivers.modules import drac
from ironic.drivers.modules import inspector
from ironic.drivers.modules import iscsi_deploy
from ironic.drivers.modules.network import flat as flat_net
from ironic.drivers.modules import pxe
from ironic.drivers.modules.storage import noop as noop_storage
from ironic.tests.unit.db import base as db_base


class BaseIDRACTestCase(db_base.DbTestCase):

    def setUp(self):
        super(BaseIDRACTestCase, self).setUp()

    def _validate_interfaces(self, driver, **kwargs):
        self.assertIsInstance(
            driver.boot,
            kwargs.get('boot', pxe.PXEBoot))
        self.assertIsInstance(
            driver.deploy,
            kwargs.get('deploy', iscsi_deploy.ISCSIDeploy))
        self.assertIsInstance(
            driver.management,
            kwargs.get('management', drac.management.DracManagement))
        self.assertIsInstance(
            driver.power,
            kwargs.get('power', drac.power.DracPower))

        # Console interface of iDRAC classic drivers is None.
        console_interface = kwargs.get('console', None)

        # None is not a class or type.
        if inspect.isclass(console_interface):
            self.assertIsInstance(driver.console, console_interface)
        else:
            self.assertIs(driver.console, console_interface)

        self.assertIsInstance(
            driver.inspect,
            kwargs.get('inspect', drac.inspect.DracInspect))

        # iDRAC classic drivers do not have a network interface.
        if 'network' in driver.all_interfaces:
            self.assertIsInstance(
                driver.network,
                kwargs.get('network', flat_net.FlatNetwork))

        self.assertIsInstance(
            driver.raid,
            kwargs.get('raid', drac.raid.DracRAID))

        # iDRAC classic drivers do not have a storage interface.
        if 'storage' in driver.all_interfaces:
            self.assertIsInstance(
                driver.storage,
                kwargs.get('storage', noop_storage.NoopStorage))

        self.assertIsInstance(
            driver.vendor,
            kwargs.get('vendor', drac.vendor_passthru.DracVendorPassthru))


@mock.patch.object(importutils, 'try_import', spec_set=True, autospec=True)
class DracClassicDriversTestCase(BaseIDRACTestCase):

    def setUp(self):
        super(DracClassicDriversTestCase, self).setUp()

    def test_pxe_drac_driver(self, mock_try_import):
        mock_try_import.return_value = True

        driver = drac_drivers.PXEDracDriver()
        self._validate_interfaces(driver)

    def test___init___try_import_dracclient_failure(self, mock_try_import):
        mock_try_import.return_value = False

        self.assertRaises(exception.DriverLoadError,
                          drac_drivers.PXEDracDriver)

    def test_pxe_drac_inspector_driver(self, mock_try_import):
        self.config(enabled=True, group='inspector')
        mock_try_import.return_value = True

        driver = drac_drivers.PXEDracInspectorDriver()
        self._validate_interfaces(driver, inspect=inspector.Inspector)
