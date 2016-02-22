import os
import fnmatch
from posixpath import join
import xmltodict
import yaml
from bjj import bjj


def find_file_pairs():
    for path, _, filelist in os.walk('./tests/xml'):
        for name in fnmatch.filter(filelist, '*.xml'):
            part_name = path.split('/')[-1]
            xml_file = xmltodict.parse(open(join(path, name), 'r'))

            test_name = name.split('.')[0]
            yaml_name = join(
                './tests/yaml', part_name, test_name + '.yaml'
            )
            yaml_file = yaml.load(open(yaml_name, 'r'))
            yield part_name, test_name, xml_file, yaml_file


def pytest_generate_tests(metafunc):
    param_values = []
    for part, test, xml_d, yaml_d in find_file_pairs():
        param_values.append((part, test, xml_d, yaml_d))

    metafunc.parametrize(['part', 'test', 'xml_d', 'yaml_d'], param_values)


def test__parse_element(part, test, xml_d, yaml_d):
    conv = bjj.TemplatedConverter()

    assert yaml.load(conv._parse_element(part, xml_d)) == yaml_d
