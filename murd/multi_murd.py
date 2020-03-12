import json
from .run_async import run_async


row_col_sep = "|||||"


class MurdMemory(dict):
    required_keys = ["ROW", "COL"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for req_key in self.required_keys:
            if req_key not in self:
                raise Exception("{} must be defined".format(req_key))

        for key, value in self.items():
            self[key] = json.dumps(value) if not isinstance(value, str) \
                else value

    @classmethod
    def prime_mems(cls, mems: list) -> dict:
        return {cls.mem_to_key(mem): ob for ob in mems}
        return list({(cls(**ob)['ROW'], cls(**ob)['COL']):
                     ob for ob in mems}.values())

    @staticmethod
    def row_col_to_key(row, col):
        return "{}{}{}".format(row, row_col_sep, col)

    @staticmethod
    def mem_to_key(mem) -> str:
        return "{}{}{}".format(mem['ROW'], row_col_sep, mem['COL'])


class Murd:
    """ Murd - Matrix: Update, Read, Delate
             - represents a collection of map memory structures
               stored in a key-value store system.

        Backends:
            Primary: String - JSON, CSV
            Secondary: DynamoDB
            Tertiary: S3, local filestore
    """

    def __init__(
        self,
        name='',
        murd='{}',
        murds=[],
        **kwargs
    ):
        self.name = name
        json.loads(murd)
        self.murd = murd
        self.murds = murds
        self.murds.append(self)

    def update(
        self,
        mems=[],
        identifier="Unidentified"
    ):
        if mems is None:
            return

        primed_mems = MurdMemory.prime_mems(mems)
        print("Storing {} memories".format(len(primed_mems)))

        murd = json.loads(self.murd)
        murd = dict(**murd, **primed_mems)
        self.murd = json.dumps(murd)

    def read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None,
        **kwargs
    ):
        murd = json.loads(self.murd)

        matched = list(murd.keys())
        if col is not None:
            prefix = "{}{}{}".format(row, self.row_col_sep, col)
            matched = [key for key in matched if prefix in key]

        if less_than_col is not None:
            maximum = self.row_col_to_key(row, less_than_col)
            matched = [key for key in matched if key < maximum]

        if greater_than_col is not None:
            minimum = self.row_col_to_key(row, greater_than_col)
            matched = [key for key in matched if key > minimum]

        results = [MurdMemory(**murd[key]) for key in matched]

        if 'Limit' in kwargs:
            results = results[:kwargs['Limit']]

        return results

    def read_all(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None,
        **kwargs
    ):
        def read_murd(Murd, **kwargs):
            return Murd.read(**kwargs)

        read_arg_sets = [{
            "Murd": murd,
            "row": row,
            "col": col,
            "greater_than_col": greater_than_col,
            "less_than_col": less_than_col,
            **kwargs
        } for murd in self.murds]
        read_arg_sets, result_sets = zip(*run_async(read_murd, read_arg_sets))
        results = []
        for result_set in result_sets:
            results.extend(result_set)
        return results

    def delete(self, mems):
        murd = json.loads(self.murd)
        primed_mems = MurdMemory.prime_mems(mems)
        keys = [self.mem_to_key(m) for m in primed_mems]
        for key in keys:
            if key not in murd:
                raise Exception("MurdMemory {} not found!".format(key))

        for key in keys:
            murd.pop(key)

        self.murd = json.dumps(murd)

    def connect(
        self,
        foreign_murd
    ):
        """ Join foreign murd into this murd structure """
        if foreign_murd not in self.murds:
            self.murds.append(foreign_murd)
        if self not in foreign_murd.murds:
            foreign_murd.murds.append(self)

    def extend(
        self,
        foreign_murd
    ):
        self.update(json.loads(foreign_murd.murd))

    def __str__(self):
        return self.murd

    def csv_string(self):
        murd = json.loads(self.murd)
        cols = []
        for key, mem in murd.items():
            new_cols = list(mem.keys())
            cols.extend(new_cols)
            cols = list(set(cols))
        csv_string = "key," + ",".join(cols) + "\n"
        for key, mem in murd.items():
            csv_row = key
            for col in cols:
                csv_row += ","
                if col in mem:
                    csv_row += str(mem[col])
            csv_row += "\n"
            csv_string += csv_row
        return csv_string
