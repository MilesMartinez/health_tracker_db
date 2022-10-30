# Health Tracker Dashboard

## Scope

Creating a dashboard to track and monitor a certain health condition. We will do this by monitoring the times at which a pressure plate is pressed. It is useful for the doctor to know the frequency at which this plate is pressed as well as the times of day it is pressed.

A Raspberry Pi will be used to monitor the pressure plate and send logs to S3 where Athena will be used for querying. Visualizations will be made with Tableau.

## Flowchart

![Flowchart](./images/diagram.png)

## Raspberry Pi Setup

![Raspberry Pi circuit diagram](./images/Raspberry-Pi-Pressure-Pad-Resistor.png.webp)

The Raspberry Pi is constantly monitoring the state of the pressure plate. When pressed, the RPi will log the starting timestamp. Once the plate is let go, the RPi will log the ending timestamp and send these two values in the form of a JSON file to S3. Example: `{"start_ts": "2022-10-29 23:48:53.957035", "end_ts": "2022-10-29 23:53:09.575207"}`

These two data points are enough to answer concerning questions such as

- How many times a day do these sessions occur?
- How long is the average session?
- What hours of the day are these sessions typically occurring?
- Does a particular session deviate from typical behavior?
- What is typical behavior?

## Athena

The beauty of Amazon Athena is that it allows you to directly query S3 with little to no ETL. In this case, no ETL is required. We can immediately build the table and start querying.

To contstruct the table we execute

```
CREATE EXTERNAL TABLE IF NOT EXISTS `default`.`pp` (
  `start_ts` timestamp,
  `end_ts` timestamp
)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES (
  'ignore.malformed.json' = 'FALSE',
  'dots.in.keys' = 'FALSE',
  'case.insensitive' = 'TRUE',
  'mapping' = 'TRUE'
)
STORED AS INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat' OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 's3://<bucke name>/'
TBLPROPERTIES ('classification' = 'json');
```

Now we can query and answer all our questions!

```
select
    date(start_ts) as day,
    extract(hour from start_ts) as hour_of_day,
    start_ts,
    end_ts,
    date_diff('minute', start_ts,end_ts) as duration_mins,
    date_diff('second', start_ts,end_ts) as duration_secs
from presure_plate_logs
```
