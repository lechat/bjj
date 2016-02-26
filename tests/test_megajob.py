import os
import fnmatch
from posixpath import join
import xmltodict
import yaml
from bjj import bjj


def load(part_path, strip_wrapper_lines=0):
    xml_list = []
    yaml_list = []
    for path, _, filelist in os.walk('./tests/parts/' + part_path):
        for name in fnmatch.filter(filelist, '*.yaml'):
            test_case = yaml.load(open(join(path, name), 'r'))

            xml_list.append(test_case['xml'])

            if isinstance(test_case['yaml'], dict or list):
                if len(test_case['yaml']) == 0:
                    continue
                yaml_list.append(test_case['yaml'])
            else:
                if len(test_case['yaml'].strip()) == 0:
                    continue
                yaml_list.append(yaml.load(test_case['yaml']))

    return '\n'.join(xml_list), yaml_list


def test_megajob():
    xml_project = """
    <project>
        <actions/>
        <description>Mega job</description>
        <keepDependencies>false</keepDependencies>
        <canRoam>true</canRoam>
        <disabled>false</disabled>
        <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
        <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
        <concurrentBuild>false</concurrentBuild>
    """
    yaml_dict = {
        'project': {}
    }
    yaml_project = yaml_dict['project']

    x_properties, y_properties = load('properties')
    x_triggers, y_triggers = load('triggers')
    x_builders, y_builders = load('builders')
    x_publishers, y_publishers = load('publishers')
    x_buildWrappers, y_buildWrappers = load('buildWrappers')

    xml_project += '<properties>' + x_properties + '</properties>'
    xml_project += '<triggers>' + x_triggers + '</triggers>'
    xml_project += '<builders>' + x_builders + '</builders>'
    xml_project += '<publishers>' + x_publishers + '</publishers>'
    xml_project += '<buildWrappers>' + x_buildWrappers + '</buildWrappers>'
    xml_project += '</project>'

    yaml_project.update({'properties': y_properties})
    yaml_project.update({'triggers': y_triggers})
    yaml_project.update({'builders': y_builders})
    yaml_project.update({'publishers': y_publishers})
    yaml_project.update({'wrappers': y_buildWrappers})

    xml_dict = xmltodict.parse(xml_project)

    conv = bjj.TemplatedConverter()

    converted = conv._convert(xml_dict)

    assert yaml.load(converted) == yaml_project
