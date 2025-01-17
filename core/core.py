# SPDX-License-Identifier: MIT
#
# Copyright (C) 2023 Efinix, Inc.

from core.variables import *
from core.utils import *

"""
get_value: get a value for a given property string

@prop (str): property string

return: string of value
"""
def get_value(prop):
    # remove tail character
    prop = prop.rstrip('\n')
    props = prop.split()

    return props[len(props) -1]

"""
get_peripheral_properties: get a list of a peripheral's properties

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: list of peripheral's properties for a given peripheral
"""
def __get_peripheral_properties(cfg, peripheral, exclude_properties="", exclude=False):
    props = []

    for line in cfg:
        if exclude:
            if exclude_properties in line:
                continue

        if peripheral in line:
            props.append(line)

    return props

def get_peripheral_properties(cfg, peripheral):
    return __get_peripheral_properties(cfg, peripheral,
                                        exclude_properties="",
                                        exclude=False)

def get_peripheral_properties_exclude(cfg, peripheral, exclude_properties, exclude=True):
    return  __get_peripheral_properties(cfg, peripheral, exclude_properties, exclude)

"""
get_property_value: get the value of peripheral properties from soc.h

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter
@name (str): properties name such as SIZE, INTERRUPT

return: string of the property value
"""
def __get_property_value(cfg, peripheral, name, match=False, exclude=False):
    value = ''
    props = get_peripheral_properties(cfg, peripheral)

    if exclude:
        for prop in props:
            if name in prop:
                props.remove(prop)

        name = peripheral

    for prop in props:
        if match:
            prop_name = prop.split()[1]
            if name == prop_name:
                value = get_value(prop)

        else:
            if name in prop:
                value = get_value(prop)

    return value

def get_property_value(cfg, peripheral, name):
    return  __get_property_value(cfg, peripheral, name, match=False)

def get_property_value_match(cfg, peripheral, name):
    return __get_property_value(cfg, peripheral, name, match=True)

def get_property_value_exclude(cfg, peripheral, name):
    return __get_property_value(cfg, peripheral, name, match=False, exclude=True)

"""
get_size: get the peripheral allocated memory size

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: string of size of memory allocated for the peripheral in hex
"""
def get_size(cfg, peripheral):
    size = 0

    if 'APB' in peripheral:
        size = get_property_value(cfg, peripheral, 'SIZE')

    else:
        size = get_property_value(cfg, peripheral, IO_SIZE)

    if not size:
        keyword_size = 'SYSTEM_{0}_IO_{1}'.format(peripheral, IO_SIZE)
        print("Error: Size for {0} is invalid. Expecting {1}".format(peripheral, keyword_size))

    return size


def get_base_address(cfg):
    props = get_peripheral_properties(cfg, BASE_ADDR_PROP)
    for prop in props:
        addr = get_value(prop)
    return addr

"""
get_address: get the address of the peripheral

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: string of address of the peripheral in hex
"""
def get_address(cfg, peripheral):
    addr = 0

    if 'APB' in peripheral:
        addr = get_property_value_exclude(cfg, peripheral, 'SIZE')

    else:
        addr = get_property_value(cfg, peripheral, PERIPHERAL)

    if not addr:
        keyword_addr = '{0}_{1}'.format(peripheral, PERIPHERAL)
        print("Error: Address for {0} not found. Expecting {1}".format(peripheral, keyword_addr))
    return addr

"""
get_peripheral_base_address: calculate the base address of peripheral

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: string of peripheral base address in hex
"""
def get_peripheral_base_address(cfg, peripheral):
    addr = get_address(cfg, peripheral)
    base = get_base_address(cfg)

    addr = hex(int(addr, 0) - int(base, 0))

    return addr

def get_peripheral_address(cfg, peripheral):
    addr = get_address(cfg, peripheral)

    return addr

def check_bus_keyword(bus_name):
    keywords = ["SYSTEM_BMB", "SYSTEM_AXI", "SYSTEM_RAM"]
    bus_name = bus_name.upper()

    for keyword in keywords:
        if bus_name in keyword:
            bus_name = keyword
            break

    return bus_name

def get_bus_address(cfg, bus_name):
    bus_name = check_bus_keyword(bus_name)
    addr = get_property_value_exclude(cfg, bus_name, "SIZE ")

    return addr

"""
get_interrupt_id: get interrupt number of peripheral

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: string of interrupt of the peripheral
"""
def get_interrupt_id(cfg, peripheral):
    irq_name = "{0}_{1}".format(peripheral, INTERRUPT)

    irq = get_property_value(cfg, peripheral, irq_name)
    return irq

"""
get_frequency: get the frequency of soc

@cfg (list): raw data of soc.h

return: string of soc's frequency
"""
def get_frequency(cfg):
    freq = ''
    props = get_peripheral_properties(cfg, FREQUENCY)
    for prop in props:
        freq = get_value(prop)

    return freq


def get_status(okay=False):
    if okay:
        return "okay"
    else:
        return "disabled"


"""
count_peripheral: count the number for the peripheral in the soc

@cfg (list): raw data of soc.h
@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter

return: number of peripheral in the soc
"""
def count_peripheral(cfg, peripheral):
    count = 0

    props = get_peripheral_properties_exclude(cfg, peripheral, "SIZE")
    for prop in props:
        if PERIPHERAL in prop:
            count = count + 1

        if 'APB' in prop:
            count = count + 1

    return count

def get_cpu_count(cfg):
    count = 0

    props = get_peripheral_properties(cfg, SUPERVISOR)
    count = len(props)

    if count == 0:
        count = 1

    return count


"""
get_cache_way: get number of I/D cache way

@cfg (list): raw data of soc.h
@cache_type (str): ICACHE or DCACHE cache

return: number of cache way for I or D cache
"""
def get_cache_way(cfg, core, cache_type):
    cache_type = "{}_WAY".format(cache_type)
    system_core = "SYSTEM_CORES_{}".format(core)
    way = get_property_value(cfg, system_core, cache_type)

    return way


def get_cache_size(cfg, core, cache_type):
    cache_type = "{}_SIZE".format(cache_type)
    system_core = "SYSTEM_CORES_{}".format(core)
    size = get_property_value(cfg, system_core, cache_type)

    return size

def get_cache_block(cfg, core):
    # SYSTEM_CORES_0_BYTES_PER_LINE
    system_core = "SYSTEM_CORES_{}_BYTES_PER_LINE".format(core)
    block = get_property_value(cfg, system_core, "BYTES_PER_LINE")

    return block

def get_cpu_isa(cfg, core):
    isa = "rv32i" #base extension
    system_core = "SYSTEM_RISCV_ISA_"

    value = get_property_value(cfg, system_core, MMU)
    if value == "1":
        # append 'm' for math RISCV instruction extension
        isa = "{}m".format(isa)

    value = get_property_value(cfg, system_core, ATOMIC)
    if value == "1":
        # append 'a' for atomic RISCV instruction extension
        isa = "{}a".format(isa)

    value = get_property_value(cfg, system_core, COMPRESS)
    if value == "1":
        # append 'c' for compressed RISCV instruction extension
        isa = "{}c".format(isa)


    value = get_property_value(cfg, system_core, FPU)
    if value == "1":
        # append 'f' for floating point percision RISCV instruction extension
        isa = "{}f".format(isa)

    value = get_property_value(cfg, system_core, DOUBLE)
    if value == "1":
        # append 'f' for  double percision RISCV instruction extension
        isa = "{}d".format(isa)


    return isa

def del_node_key(node, keys_to_delete):

    for key in keys_to_delete:
        if key in node:
            del node[key]
    return node

"""
get_cpu_metadata: get metadata of a cpu

@cfg (list): raw data of soc.h
@idx (int): cpu core number

return: dict of a cpu metadata
"""
def get_cpu_metadata(cfg, idx=0):
    node = {}

    core = "core{}".format(idx)
    isa = get_cpu_isa(cfg, idx)
    icache_way = get_cache_way(cfg, idx, ICACHE)
    icache_size = get_cache_size(cfg, idx, ICACHE)
    dcache_way = get_cache_way(cfg, idx, DCACHE)
    dcache_size = get_cache_size(cfg, idx, DCACHE)
    cache_block = get_cache_block(cfg, idx)

    node = {
        "name": "cpu",
        "addr": idx,
        "reg": "reg = <{}>;".format(idx),
        "device_type": 'device_type = "cpu";',
        "compatible": 'compatible = "riscv";',
        "isa": 'riscv,isa = "{}";'.format(isa),
        "tlb": "tlb-split;",
        "status": get_status(okay=True)
    }

    if icache_way and icache_size and dcache_way and dcache_size:
        node.update({
            "icache_way": "i-cache-sets = <{}>;".format(icache_way),
            "icache_size": "i-cache-size = <{}>;".format(icache_size),
            "icache_block_size": "i-cache-block-size = <{}>;".format(cache_block),
            "dcache_way": "d-cache-sets = <{}>;".format(dcache_way),
            "dcache_size": "d-cache-size = <{}>;".format(dcache_size),
            "dcache_block_size": "d-cache-block-size = <{}>;".format(cache_block),
        })

    else:
        system_core = "SYSTEM_CORES_{}".format(idx)
        value = get_property_value(cfg, system_core, MMU)
        if value:
            node.update({"mmu_type": 'mmu_type = "riscv,sv32";'})

    return node

"""
get_peripherals: get a list of supported peripheral from soc.h

soc.h might have lot of peripherals but it may not supported by the driver.
For example, there are 2 spi and a i2c listed in soc.h. However, i2c is not
supported by the driver. So, @filter_peripherals should only list the supported
peripherals.

@cfg (str): raw data of soc.h
@filter_peripherals: list of supported peripherals

return: list of supported peripheral
"""
def get_peripherals(cfg, filter_peripherals):
    peripherals = []

    for line in cfg:
        periph = ''.join([x for x in filter_peripherals if x in line])
        if periph:
            peripherals.append(periph)

    # remove duplicate from list
    peripherals = list(dict.fromkeys(peripherals))

    return peripherals

"""
override_peripherals: override the peripherals properties

The properties for each peripheral can be overrided using this function.
It need to follow specific data structure to override the existing value.
For example, to override the compatible property for apb_slave_0 node,
the new_cfg should specify as follow.

new_cfg = {
    "overrides": {
        "APB_SLAVE_0": {
            "compatible": "new-apb-slave"
        }
    }
}

APB_SLAVE_0 is the key to override specific peripherals properties.

@peripheral_parent (dict): a dictionary that have all of the peripherals
@new_cfg (dict): new configuration to override the peripheral in @peripheral_parent.
"""
def override_peripherals(peripheral_parent, new_cfg):
    for k1 in peripheral_parent['buses']:
        for k2 in peripheral_parent['buses'][k1]['peripherals']:
            if 'overrides' in new_cfg:
                for u1 in new_cfg['overrides']:
                    if k2 in u1:
                        n_cfg = new_cfg['overrides'][u1]
                        peripheral_node = peripheral_parent['buses'][k1]['peripherals'][k2]
                        peripheral_node.update(n_cfg)
                        node_header = get_node_header(peripheral_node)
                        peripheral_node['header'] = node_header

"""
get_os_data: get operating system data from drivers.json

@is_zephyr (bool): specify is it zephyr else it will choose linux

return: dictionary of operating system data
"""
def get_os_data(is_zephyr=False):
    operating_system = 'linux'

    os_data = load_config_file()

    if is_zephyr:
        operating_system = 'zephyr'

    os_data = os_data['os'][operating_system]

    return os_data

"""
get_driver_data: get the driver data from drivers.json

@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter
@controller (bool): the peripheral is controller peripheral such as plic
@is_zephyr (bool): specify is it zephyr else it will choose linux

return: dictionary of driver data
"""
def get_driver_data(controller=False, is_zephyr=False):
    driver_data = get_os_data(is_zephyr=is_zephyr)

    if controller:
        driver_data = driver_data['controller']
    else:
        driver_data = driver_data['drivers']

    return driver_data

"""
get_driver_private_data: get the driver private data from drivers.json

@peripheral (str): peripheral name such as SPI, I2C. Must be in capital letter
@controller (bool): the peripheral is controller peripheral such as plic
@is_zephyr (bool): specify is it zephyr else it will choose linux

return: dictionary of driver private data
"""
def get_driver_private_data(peripheral, controller=False, is_zephyr=False):
    priv_data = ''
    peripheral = peripheral.lower()

    driver_data = get_driver_data(controller, is_zephyr)

    if peripheral in driver_data:
        if 'private_data' in driver_data[peripheral]:
            priv_data = driver_data[peripheral]['private_data']

    return priv_data

"""
get_node_header: construct the device tree node header

@node (dict): any node which contain label, name and addr

return: string of node header

The node header could be constructed in three different ways
depending on label, name and address property.
For example, if label, name and address are available, it will
create as follows.

label: name@address {

If only label is available, then it will create like this.

label {

Finally, if only name and address are available, then it will create
like this.

name@address {
"""
def get_node_header(node):
    node_header = ''
    addr = ''

    if 'addr' in node:
        addr = str(node['addr'])
        if '0x' in addr:
            addr = addr.strip('0x')

    if 'label' in node and node['label']:
        if 'name' in node and node['name']:
            if 'addr' in node:
                node_header = "{}: {}@{}".format(node['label'], node['name'], addr)
            else:
                node_header = "{}: {}".format(node['label'], node['name'])
        else:
            node_header = "{}".format(node['label'])

    elif 'name' in node and node['name']:
        node_header = "{}@{}".format(node['name'], addr)

    node_header += " {"

    return node_header

def get_child_node_header(node):
    if 'child' in node:
        for child_node in node['child']:
            node_header = get_node_header(node['child'][child_node])
            node['child'][child_node]['header'] = node_header

            child_node = node['child'][child_node]
            if 'child' in child_node:
                for child_node2 in child_node['child']:
                    node_header = get_node_header(child_node['child'][child_node2])
                    child_node['child'][child_node2]['header'] = node_header

    return node
