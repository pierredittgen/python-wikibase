import collections
import datetime

from python_wikibase.data_types.data_type import DataType


class DataTypeException(BaseException):
    pass

# Largely inspired from  https://github.com/dahlia/wikidata/blob/master/wikidata/datavalue.py


class Time(DataType):
    def __init__(self, py_wb, api, language):
        super().__init__(py_wb, api, language)
        self.value = None

    def __str__(self):
        return self.value.isoformat()

    def unmarshal(self, data_value):
        value = data_value["value"]

        # See https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#time
        # for property to extract from data_value

        time = value['time']
        # Strip '+' at beginning of string and 'Z' at the end
        time = time[1:-1]

        tz = value['timezone']
        # Don't take in account 'before' and 'after' property
        precision = value['precision']

        if precision == 11:
            self.value = datetime.date.fromisoformat(time[:-9])
        elif precision == 14:
            val = datetime.datetime.fromisoformat(time)
            val.replace(tzinfo=datetime.timezone(offset=datetime.timedelta(minutes=tz)))
            self.value = val
        return self

    def marshal(self):

        common_properties = {
            "timezone": 0,
            "before": 0,
            "after": 0,
            "calendarmodel": "http://www.wikidata.org/entity/Q1985727"
        }

        if isinstance(self.value, datetime.date):
            return {
                **common_properties,
                "time": "+{}T00:00:00Z".format(self.value.isoformat()),
                "precision": 11
            }
        elif isinstance(self.value, datetime.datetime):
            dt = self.value.astimezone(tz=datetime.timezone.utc)
            return {
                **common_properties,
                "time": "+{}Z".format(iso_str[:19]),
                "precision": 14
            }

    def create(self, value):
        if isinstance(value, datetime.datetime):
            # consider as utc if timezone info is missing
            if value.tzinfo is None:
                value = value.replace(tzinfo=datetime.timezone.utc)

        elif not isinstance(value, datetime.date):
            raise DataTypeException("Unknown value type {!r}".format(value))
        self.value = value

        return self
