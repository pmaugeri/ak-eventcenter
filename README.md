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
```

### Help 

Calling the **help** command will give you some help on command you are interested in:
```
> help

Documented commands (type help <topic>):
========================================
create  createFromCsv  get  help  ls  q  quit  rm

Undocumented commands:
======================
cd

> help create

Create a new Event based on a JSON file called 'event-template.json'.

create <Event Name> <Start Time (in milliseconds)> <End Time (in milliseconds)>
```

### Create a new Event

The commands **Create** and **createFromCsv** will use an auxiliary JSON file as a template to create the new Event. This file is named **event-template.json** and should be locate in the current directory where you call the CLI.

You default template file comes with the 3 mandatory fields: the event name, event start time and end event end time. You can customize this file. It is recommended that you first create a "master" event in Akamai portal and retrieves it using command **get**.
