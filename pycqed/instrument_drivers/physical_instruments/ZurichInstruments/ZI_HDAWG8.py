import time
import logging
import os
from . import zishell_NH as zs
from .ZI_base_instrument import ZI_base_instrument
from qcodes.instrument.parameter import ManualParameter


class ZI_HDAWG8(ZI_base_instrument):

    """
    """

    def __init__(self, name, device: str,
                 server: str='localhost', port=8004, **kw):
        '''
        Input arguments:
            name:           (str) name of the instrument
            server_name:    (str) qcodes instrument server
            address:        (int) the address of the data server e.g. 8006
        '''
        t0 = time.time()

        super().__init__(name=name, **kw)
        self._devname = device
        self._dev = zs.ziShellDevice()
        self._dev.connect_server(server, port)
        print("Trying to connect to device {}".format(self._devname))
        self._dev.connect_device(self._devname, '1GbE')

        self.add_parameter('timeout', unit='s',
                           initial_value=10,
                           parameter_class=ManualParameter)

        dir_path = os.path.dirname(os.path.abspath(__file__))
        base_fn = os.path.join(dir_path, 'zi_parameter_files')

        try:
            self.add_s_node_pars(
                filename=os.path.join(base_fn, 's_node_pars_HDAWG8.json'))
        except FileNotFoundError:
            logging.warning("parameter file for settable parameters"
                            " {} not found".format(self._s_file_name))
        try:
            self.add_d_node_pars(
                filename=os.path.join(base_fn, 'd_node_pars_HDAWG8.json'))
        except FileNotFoundError:
            logging.warning("parameter file for data parameters"
                            " {} not found".format(self._d_file_name))
        self.add_ZIshell_device_methods_to_instrument()
        self.connect_message(begin_time=t0)

    def add_ZIshell_device_methods_to_instrument(self):
        """
        Some methods defined in the zishell are convenient as public
        methods of the instrument. These are added here.
        """
        self.reconnect = self._dev.reconnect
        self.restart_device = self._dev.restart_device
        self.poll = self._dev.poll
        self.sync = self._dev.sync
        self.configure_awg_from_file = self._dev.configure_awg_from_file
        self.configure_awg_from_string = self._dev.configure_awg_from_string
        self.read_from_scope = self._dev.read_from_scope
        self.restart_scope_module = self._dev.restart_scope_module
        self.restart_awg_module = self._dev.restart_awg_module

    def get_idn(self):
        idn_dict = {'vendor': 'ZurichInstruments',
                    'model': self._dev.daq.getByte(
                        '/{}/features/devtype'.format(self._devname)),
                    'serial': self._devname,
                    'firmware': self._dev.geti('system/fwrevision'),
                    'fpga_firmware': self._dev.geti('system/fpgarevision')
                    }
        return idn_dict
