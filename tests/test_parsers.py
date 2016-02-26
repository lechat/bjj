import os
import fnmatch
from posixpath import join
import xmltodict
import yaml
from bjj import bjj


def find_file_pairs():
    for path, _, filelist in os.walk('./tests/parts'):
        for name in fnmatch.filter(filelist, '*.yaml'):
            part_name = path.split('/')[-1]
            test_name = name.split('.')[0]

            test_case = yaml.load(open(join(path, name), 'r'))

            xml_dict = xmltodict.parse(test_case['xml'])
            if isinstance(test_case['yaml'], (dict, list)):
                yaml_dict = test_case['yaml']
            else:
                yaml_dict = yaml.load(test_case['yaml'])

            yield part_name, test_name, xml_dict, yaml_dict


def pytest_generate_tests(metafunc):
    param_values = []
    for part, test, xml_d, yaml_d in find_file_pairs():
        param_values.append((part, test, xml_d, yaml_d))

    metafunc.parametrize(['part', 'test', 'xml_d', 'yaml_d'], param_values)


def test__parse_element(part, test, xml_d, yaml_d):
    conv = bjj.TemplatedConverter()

    if test == 'project':
        converted = conv._convert(xml_d)
        assert yaml.load(converted) == yaml_d
    else:
        converted = conv._parse_element(part, xml_d)
        assert yaml.load(converted) == yaml_d
