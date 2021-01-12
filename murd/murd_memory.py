import json


row_col_sep = "|||||"


class MurdMemory(dict):
    row_col_sep = row_col_sep
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
        return {cls.mem_to_key(mem): mem for mem in mems}

    @staticmethod
    def row_col_to_key(row, col):
        return "{}{}{}".format(row, row_col_sep, col)

    @staticmethod
    def mem_to_key(mem) -> str:
        return "{}{}{}".format(mem['ROW'], row_col_sep, mem['COL'])
