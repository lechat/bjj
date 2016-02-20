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

## Not currently implemented

Nothing really works at this stage:
* Yaml files are not saved, but printed out to stdout
* Reading jobs from Jenkins not implemented

