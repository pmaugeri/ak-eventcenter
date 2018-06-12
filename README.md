# ak-eventcenter-tools

This tool is a Command Line Interface (CLI) that wraps [Akamai {Open} API Event Center](https://developer.akamai.com/api/luna/events/overview.html).

The CLI simplifies your operation with the API and offers the following command:
1. customer account navigation (command **cd**)
2. list the Events (command **ls**)
3. get an Event and its details (command **get**)
4. create one new event (command **create**) or create several events using a CSV definition file (command **createFromCsv**)
5. delete one or more events (command **rm**)

## Requirements

- Python 2.7.10 or above

## Installation

```
$ git clone git@github.com:pmaugeri/ak-eventcenter-tools.git
```

## Configuration

Prior to run for the first time the CLI you should edit the file **.edgerc** and add the credentials you obtained to connect to Akamai API endpoint.

## Usage

Run the CLI using the python interpreter:

```
$ python cli.py 
Starting prompt...
> 
```

The first thing you will probably need to do is to change to the master customer account:

```
> cd 1-3AXXXX
1-3AXXXX> 
1-3AXXXX> 
```

