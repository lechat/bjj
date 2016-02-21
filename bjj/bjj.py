"""
Convert Jenkins job definition to jenkins-job-builder yaml

Usage:
    bjj.py convertfile --path PATH...
    bjj.py convertjob --jenkins-url URL --job-regex REGEX [--user USER]
           [--password PASS]

Options:
    --path PATH         File to convert from
    --jenkins-url URL   Jenkins URL
    --job-regex REGEX   Regular expression to find jobs [Default: .*]
    --user USER         Jenkins user name
    --password PASS     Jenkins user's password or API token
"""
from docopt import docopt
import logging
from jenkinsapi.jenkins import Jenkins
import yaml
from jinja2 import Environment, PackageLoader, TemplateNotFound
import xmltodict
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('bjj')


class literal_unicode(unicode):
    pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(literal_unicode, literal_unicode_representer)


class FileIterator(object):
    def __init__(self, files):
        if isinstance(files, str):
            self.files = [files]
        else:
            self.files = files

    def __iter__(self):
        for xml_file in self.files:
            yield xml_file, self._et_from_file(xml_file)

    def __len__(self):
        return len(self.files)

    def _et_from_file(self, filename):
        with open(filename, 'r') as xml:
            x_dict = xmltodict.parse(xml)
        return x_dict


class JenkinsIterator(object):
    def __init__(self, jenkins_url, user, passwd, regex):
        self.jenkins = Jenkins(jenkins_url, user, passwd)
        self.regex = regex

    def __iter__(self):
        for job_name in self.jenkins.jobs:
            # if regex matches
            # get job xml as string
            job_config = ""
            yield job_name, self._et_from_string(job_config)

    def _et_from_string(xml_string):
        return xmltodict.parse(xml_string)


class TemplatedConverter(object):
    def __init__(self, parts_path='parts'):
        self.env = Environment(loader=PackageLoader('bjj', parts_path),
                               trim_blocks=True,
                               lstrip_blocks=True,
                               line_statement_prefix='#',
                               line_comment_prefix='## ')

    def _parse_element(self, el_name, el_data):
        part = self.env.get_template(el_name + '.part')
        result = part.render(el=el_data)
        return result

    def _convert(self, et, name):
        """
        Converts one job to yaml string
        """
        print json.dumps(et, indent=2)

        # Top level element is parsed here
        job = self._parse_element(et.keys()[0], None)

        for name, data in et['project'].iteritems():
            try:
                job += self._parse_element(name, data)
            except TemplateNotFound:
                logger.warning(
                    'Template "parts/{name}.part" not found. '
                    'Perhaps XML tag "{name}" is not implemented yet'
                    .format(name=name))
        return job

    def convert(self, it):
        """
        Converts iterator of parsed XMLs to yaml files
        """
        # TODO: if iterator has multiple items - make job-group of them
        for name, et in it:
            yaml = self._convert(et, name)
            yaml_filename = name + '.yml'
            with open(yaml_filename, 'w') as of:
                of.write(yaml)


def main():
    args = docopt(__doc__)

    if args['convertfile']:
        conv = FileIterator(args['--path'])
    else:
        conv = JenkinsIterator(
            args['--jenkins-url'],
            args['--user'],
            args['--password'],
            args['--job-regex']
        )

    TemplatedConverter().convert(conv)


if __name__ == '__main__':
    main()
