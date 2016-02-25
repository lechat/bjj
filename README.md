# bjj
Convert Jenkins jobs to yaml understood by OpenStack jenkins-job-builder

The purpose of this library is to enable migration of existing Jenkins jobs to [OpenStack jenkins-job-builder](http://docs.openstack.org/infra/jenkins-job-builder/).

## Usage

```
    bjj.py convertfile --path PATH...
    bjj.py convertjob --jenkins-url URL --job-regex REGEX [--user USER]
           [--password PASS]

Options:
    --path PATH         File to convert from
    --jenkins-url URL   Jenkins URL
    --job-regex REGEX   Regular expression to find jobs [Default: .*]
    --user USER         Jenkins user name
    --password PASS     Jenkins user's password or API token
```

## How does it work?

1. Parse config.xml to python dict
2. Pass that dict to jinja2 template, get string result
3. Write all strings to yaml file

## How to add new xml element parsing?

Say, you need to add parser for String parameter (it is already in code, btw.) XML element for it looks like this:

```
<project>
    <properties>
        <hudson.model.ParametersDefinitionProperty>
			<parameterDefinitions>
				<hudson.model.StringParameterDefinition>
					<name>STR_PARAM</name>
					<description>String something</description>
					<defaultValue></defaultValue>
				</hudson.model.StringParameterDefinition>
			</parameterDefinitions>
        </hudson.model.ParametersDefinitionProperty>
	<properties>
</project>
```

<project> is parsed by itself, so you are interested in top level element, <properties>.

Add dir under "tmpl" named "properties" and then add folder with the name of XML tag for each level: "hudson.model.ParametersDefinitionProperty/parameterDefinitions". Then make "hudson.model.StringParameterDefinition.tmpl" file
and put simple YAML template there:

```

        - string:
            name: '{{ name }}'
            default: '{{ defaultValue|default('', boolean=True) }}'
            description: '{{ description|default('', boolean=True) }}'
```

Note that you will have to keep identation level and sometimes add new line either on top and/or at the end of the template.

If you want to test how new template works, you can run unit tests, but for that you will need to add YAML file containing XML and output YAML. Take a look in "tests/parts" for existing test YAMLs.

## Not currently implemented

* Yaml files are saved next to config.xml's and named "config.xml.yaml"
* Reading jobs from Jenkins not yet implemented
* Making JJB templates from the set of existing jobs

