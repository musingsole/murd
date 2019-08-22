import json
from urequests import post as post_request
from urequests import put as put_request
from urequests import delete as delete_request


class MurdMemory(dict):
    required_keys = ["ROW", "COL"]

    def __init__(self, **kwargs):
        self = kwargs
        for req_key in MurdMemory.required_keys:
            if req_key not in self:
                raise Exception("{} must be defined".format(req_key))

        for key, value in self.items():
            self[key] = json.dumps(value) if not isinstance(value, str) else value


class MurdClient:
    """ Murd API Client """

    def __init__(
        self,
        url
    ):
        self._url = url

    @staticmethod
    def prime_mems(mems):
        return list({(MurdMemory(**ob)['ROW'], MurdMemory(**ob)['COL']): ob for ob in mems}.values())

    def update(
        self,
        mems,
        identifier="Unidentified"
    ):
        mems = self.prime_mems(mems)
        data = {'mems': json.dumps(mems)}
        resp = put_request(url=self.url, data=data)

        if resp.status_code != 200:
            raise Exception("Murd update request failed")

    def read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None
    ):
        data = {"row": row}
        if col is not None:
            data['col'] = col
        if greater_than_col is not None:
            data['greater_than_col'] = greater_than_col
        if less_than_col is not None:
            data['less_than_col'] = less_than_col
        resp = post_request(url=self.url, data=data)

        if resp.status_code != 200:
            raise Exception("Murd update request failed")

        read_data = json.loads(resp.text)
        read_data = [MurdMemory(**rd) for rd in read_data]
        return read_data

    def delete(self, mems):
        mems = self.prime_mems(mems)
        data = {'mems': json.dumps(mems)}
        resp = delete_request(url=self.url, data=data)

        if resp.status_code != 200:
            raise Exception("Murd delete request failed")

        stubborn_mems = json.loads(resp.text)
        return [MurdMemory(**sm) for sm in stubborn_mems]
