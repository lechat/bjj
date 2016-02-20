from jinja2 import Environment, PackageLoader
import xml.etree.ElementTree as ET

env = Environment(loader=PackageLoader('bjj'),
                  trim_blocks=True,
                  lstrip_blocks=True)

et = ET.parse('config.xml').getroot()
print 'BB: ', et.findall('project/blockBuildWhenDownstreamBuilding')

template = env.get_template('jobtemplate.yml')
print template.render(et=et)
