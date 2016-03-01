"""
Convert Jenkins job definition to jenkins-job-builder yaml

Usage:
    bjj.py [-v] files --path PATH... [--outpath PATH]
    bjj.py [-v] jenkins --jenkins-url URL [--job-regex REGEX] [--user USER]
           [--password PASS] [--outpath PATH]

Options:
    --path PATH         File to convert from
    --jenkins-url URL   Jenkins URL
    --job-regex REGEX   Regular expression to find jobs [Default: .*]
    --user USER         Jenkins user name
    --password PASS     Jenkins user's password or API token
    --outpath PATH      Path to store YAMLs [Default: ./]
    -v --verbose        Verbose output
"""
from docopt import docopt
import logging
from jenkinsapi.jenkins import Jenkins
import yaml
from jinja2 import Environment, PackageLoader
import xmltodict
import json
import re
from os.path import basename
from posixpath import join
from pkg_resources import resource_string


logging.basicConfig(level=logging.INFO)
logging.getLogger('requests').setLevel(logging.CRITICAL)
logger = logging.getLogger('bjj')


class literal_unicode(unicode):
    pass


def literal_unicode_representer(dumper, data):
    return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(literal_unicode, literal_unicode_representer)


class NoTemplate(Exception):
    pass


class FileIterator(object):
    def __init__(self, files):
        if isinstance(files, str):
            self.files = [files]
        else:
            self.files = files

    def __iter__(self):
        for xml_file in self.files:
            yield basename(xml_file), self._et_from_file(xml_file)

    def __len__(self):
        return len(self.files)

    def _et_from_file(self, filename):
        with open(filename, 'r') as xml:
            x_dict = xmltodict.parse(xml)
        return x_dict


class JenkinsIterator(object):
    def __init__(self, jenkins_url, user, passwd, regex=None):
        self.jenkins = Jenkins(jenkins_url, user, passwd)
        if regex is not None:
            self.regex = re.compile(regex)
        else:
            self.regex = None

    def __iter__(self):
        for job_name in self.jenkins.jobs.iterkeys():
            job_config = None
            if self.regex is not None:
                if re.search(self.regex, job_name) is not None:
                    job_config = self.jenkins.jobs[job_name].get_config()
            else:
                job_config = self.jenkins.jobs[job_name].get_config()

            if job_config is not None:
                yield job_name, self._et_from_string(job_config)

    def _et_from_string(self, xml_string):
        return xmltodict.parse(xml_string)


class TemplatedConverter(object):
    def __init__(self, tmpls_path='tmpls', save_path='./'):
        self.tmpls_path = tmpls_path
        self.env = Environment(loader=PackageLoader('bjj', tmpls_path),
                               trim_blocks=True,
                               lstrip_blocks=True,
                               line_statement_prefix='#',
                               line_comment_prefix='## ')
        self.save_path = save_path

    def _parse_top_element(self, el_name, el_data):
        result = ''

        try:
            try:
                tmpl = resource_string(
                    __name__, self.tmpls_path + '/' + el_name + '/base.tmpl'
                )
                tpl = self.env.from_string(tmpl)
                result = tpl.render(**el_data)
                if el_name == 'logRotator':
                    return result
            except IOError:
                pass
            if el_name == 'scm':
                parsed_children = self._parse_element(
                    el_data['@class'],
                    el_data,
                    self.tmpls_path
                )
            else:
                parsed_children = self._parse_element(
                    el_name,
                    el_data,
                    self.tmpls_path
                )
            if len(parsed_children) == 0:
                logger.warning(
                    'Template "{}.tmpl" not found. '
                    'Perhaps XML tag "{}" is not implemented yet'
                    .format(el_name, el_name))
            result += parsed_children

            return result
        except IOError:
            raise NoTemplate(el_name)

    def _parse_element(self, el_name, el_data, path='tmpls'):
        logger.debug('Parsing element "%s"' % el_name)
        result = []

        if not isinstance(el_data, dict):
            return ''
        for el in el_data:
            if el.encode('ascii')[0] == '@':
                continue

            try:
                rel_path = path + '/' + el_name
                tmpl_path = rel_path + '/' + el + '.tmpl'
                logger.debug('Trying to find template "%s"' % tmpl_path)
                tmpl = resource_string(__name__, tmpl_path)
                tpl = self.env.from_string(tmpl)
                if isinstance(el_data[el], list):
                    for item in el_data[el]:
                        result.append(tpl.render(**item))
                else:
                    result.append(tpl.render(**el_data[el]))
            except IOError:
                result.append(self._parse_element(el, el_data[el], rel_path))

        joined = ''.join(result)
        if len(joined.strip()) == 0:
            logger.warning(
                'Template "{}.tmpl" not found. '
                'Perhaps XML tag "{}" is not implemented yet'
                .format(el_name, el_name))

        return joined

    def _convert(self, et):
        """
        Converts one job to yaml string
        """
        if logger.level == logging.DEBUG:
            print json.dumps(et, indent=2)

        # Top level element is parsed here
        job = self._parse_element(et.keys()[0], et)

        for name, data in et['project'].iteritems():
            if not isinstance(data, dict):
                continue
            try:
                job += self._parse_top_element(name, data)
            except NoTemplate as tnf:
                logger.warning(
                    'Template "{}.tmpl" not found. '
                    'Perhaps XML tag "{}" is not implemented yet'
                    .format(tnf.message, name))
        return job

    def convert(self, it):
        """
        Converts iterator of parsed XMLs to yaml files
        """
        # TODO: if iterator has multiple items - make job-group of them
        for name, et in it:
            yaml = self._convert(et)
            yaml_filename = join(self.save_path, name + '.yml')
            logger.info('Writing yaml to %s' % yaml_filename)
            with open(yaml_filename, 'w') as of:
                of.write(yaml)


def main():
    args = docopt(__doc__)

    if args['--verbose']:
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose logging requested')

    if args['files']:
        conv = FileIterator(args['--path'])
    else:
        conv = JenkinsIterator(
            args['--jenkins-url'],
            args['--user'],
            args['--password'],
            args['--job-regex']
        )

    TemplatedConverter(save_path=args['--outpath']).convert(conv)


if __name__ == '__main__':
    main()
