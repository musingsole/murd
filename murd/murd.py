import json
from murd import MurdMemory


class Murd:
    """ Murd - Matrix: Update, Read, Delate
             - represents a collection of map memory structures
               stored in a key-value store system.

        Backends:
            Primary: String - JSON
            Secondary: DynamoDB
            Tertiary: S3
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
        col="",
        greater_than_col=None,
        less_than_col=None,
        **kwargs
    ):
        murd = json.loads(self.murd)

        matched = list(murd.keys())
        prefix = "{}{}{}".format(row, MurdMemory.row_col_sep, col)
        matched = [key for key in matched if prefix in key[:len(prefix)]]

        if less_than_col is not None:
            maximum = MurdMemory.row_col_to_key(row, less_than_col)
            matched = [key for key in matched if key < maximum]

        if greater_than_col is not None:
            minimum = MurdMemory.row_col_to_key(row, greater_than_col)
            matched = [key for key in matched if key > minimum]

        results = [MurdMemory(**murd[key]) for key in matched]

        if 'Limit' in kwargs:
            results = results[:kwargs['Limit']]

        return results

    def delete(self, mems):
        murd = json.loads(self.murd)
        primed_mems = MurdMemory.prime_mems(mems)
        keys = [MurdMemory.mem_to_key(m) for m in primed_mems]
        for key in keys:
            if key not in murd:
                raise Exception("MurdMemory {} not found!".format(key))

        for key in keys:
            murd.pop(key)

        self.murd = json.dumps(murd)
