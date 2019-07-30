import json
import os
from datetime import datetime
from run_async import run_async


# Format for interpreting String Timestamps to a Datetime object or storing
# Datetime objects as String Timestamps
TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class MurdMemory(dict):
    required_keys = ["ROW", "COL"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for req_key in self.required_keys:
            if req_key not in self:
                raise Exception("{} must be defined".format(req_key))

        for key, value in self.items():
            self[key] = json.dumps(value) if not isinstance(value, str) else value


class Murd:
    """ Murd - Matrix: Update, Read, Delate - represents a collection of map memory structures
        stored in a key-value store system. 

        Backends:
            Primary: String
            Secondary: DynamoDB
            Tertiary: S3, local filestore

        Challenges:
            Primary:
                * Table Creation
                * Simultanenous Request

            Secondary/Tertiary:
                * Optimize file system (directory, folder, contents) for S3 or
                  locally managed key-value store
    """

    row_col_sep = "|||||"

    def __init__(
        self,
        name='',
        murd='{}',
        murds=[],
        **kwargs
    ):
        if name == '':
            name = os.getenv('murd', 'murd')
        self.name = name

        self.murd = murd
        self.murds = murds
        self.murds.append(self)

    @staticmethod
    def prime_mems(mems):
        return list({(MurdMemory(**mem)['ROW'], MurdMemory(**mem)['COL']): mem for mem in mems}.values())

    @staticmethod
    def mem_to_key(mem):
        return "{}{}{}".format(mem['ROW'], Murd.row_col_sep, mem['COL'])

    @staticmethod
    def row_col_to_key(row, col):
        return "{}{}{}".format(row, Murd.row_col_sep, col)

    def update(
        self,
        mems,
        identifier="Unidentified"
    ):
        primed_mems = self.prime_mems(mems)
        creationstamp = datetime.utcnow()
        creationstamp_string = creationstamp.strftime(TIME_FORMAT)

        murd = json.loads(self.murd)

        if len(primed_mems) > 0:
            print("Storing {} memories".format(len(primed_mems)))

            for count, mem in enumerate(primed_mems):
                mem['CREATIONSTAMP'] = creationstamp_string
                murd[self.mem_to_key(mem)] = mem

        self.murd = json.dumps(murd)

    def local_read(
        self,
        row,
        col=None,
        greater_than_mem=None,
        less_than_mem=None,
        **kwargs
    ):
        murd = json.loads(self.murd)

        if col is not None:
            try:
                return [MurdMemory(**murd[Murd.row_col_to_key(row, col)])]
            except Exception:
                raise Exception("Unable to locate mem: {}".format(Murd.row_col_to_key(row, col)))

        matched = list(murd.keys())

        if col is not None:
            prefix = "{}{}{}".format(row, Murd.row_col_sep, col)
            matched = [key for key in matched if prefix in key]

        if less_than_mem is not None:
            minimum = self.row_col_to_key(row, less_than_mem)
            matched = [key for key in matched if key > minimum]

        if greater_than_mem is not None:
            maximum = self.row_col_to_key(row, less_than_mem)
            matched = [key for key in matched if maximum > key]

        results = [MurdMemory(**murd[key]) for key in matched]

        if 'Limit' in kwargs:
            results = results[:kwargs['Limit']]

        return results

    def read(
        self,
        row,
        col=None,
        greater_than_mem=None,
        less_than_mem=None,
        **kwargs
    ):
        if type(row) is list:
            rows = row
            arg_sets = [{
                "row": row,
                "col": col,
                "greater_than_mem": greater_than_mem,
                "less_than_mem": less_than_mem,
                **kwargs
            } for row in rows]

            results = run_async(self.remember, arg_sets)
            memory_mems = {arg_set['mem']: mem for arg_set, mem in results}

            return memory_mems
        else:
            arg_set = {
                "row": row,
                "col": col,
                "greater_than_mem": greater_than_mem,
                "less_than_mem": less_than_mem,
                **kwargs
            }

            results = []
            for murd in self.murds:
                hm_results = murd.local_read(**arg_set)
                results.extend(hm_results)

            return results

    def delete(self, mems):
        murd = json.loads(self.murd)
        primed_mems = self.prime_mems(mems)
        keys = [self.mem_to_key(m) for m in primed_mems]
        for key in keys:
            if key not in murd:
                raise Exception("MurdMemory {} not found!".format(key))

        for key in keys:
            murd.pop(key)

        self.murd = json.dumps(murd)

    def join(
        self,
        foreign_murd
    ):
        """ Become aware of other murd so as to read it as well """
        self.murds.append(foreign_murd)

    def assimilate(
        self,
        foreign_murd
    ):
        pass

    def __str__(self):
        return self.murd
