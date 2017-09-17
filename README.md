# heroesinfo
A Heroes of the Storm data extractor for talents and heroes info

## Configuration
You will need a PostgreSQL server running at least the version 9.5, because we make extensive use of the JSONB datatype to store the metrics we extract from the replay.

- Create a database with the name "hotsdata"
- Create a user with the name "hotsdata" and grant ALL to the hotsdata database.
- Create the following tables:
```
create table heroes
(
	id varchar(64) not null,
	patch integer not null,
	name varchar(64),
	role varchar(64),
	universe varchar(64),
	alignment varchar(64),
	rarity varchar(64),
	portrait_icon varchar(128),
	gender varchar(64),
	difficulty varchar(64),
	damage smallint,
	utility smallint,
	complexity smallint,
	survivability smallint,
	attrib_name varchar(10),
	constraint hero_pk
		primary key (id, patch)
)
;

create table talents
(
	id varchar(64) not null,
	patch integer not null,
	name varchar(64),
	hero varchar(64) not null,
	tier smallint,
	position smallint,
	icon varchar(64),
	constraint talents_pk
		primary key (id, patch, hero)
)
;


```

## Running the script
This script assumes you have the files already extracted from the game files, I used [heroesjson](https://github.com/nydus/heroesjson).
Once you have the files, change the path in [line 15](https://github.com/crorella/heroesinfo/blob/master/heroesinfo.py#L15) to the out folder created after you run heroesjson.




