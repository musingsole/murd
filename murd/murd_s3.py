import json
from io import BytesIO
from collections import defaultdict
import boto3

from .murd import MurdMemory
from .murd import Murd
from .run_async import run_async


class MurdS3Client:
    """ Murd API Client """

    def __init__(
        self,
        bucket_name
    ):
        self.bucket_name = bucket_name
        self.bucket = boto3.resource("s3").Bucket(self.bucket_name)

    def retrieve_s3_summaries(self, row_prefix):
        s3_client = boto3.client("s3")
        try:
            object_summaries = [
                os for os in self.bucket.objects.all() if str(row_prefix) in os.key]
        except s3_client.exceptions.NoSuchBucket:
            raise Exception("Error accessing bucket {self.bucket_name}")

        return object_summaries

    def retrieve_murd_row(self, row, allow_missing=True):
        object_murd = Murd()
        try:
            read_data = BytesIO()
            self.bucket.download_fileobj(Key=row, Fileobj=read_data)
            read_data.seek(0)
            read_data = read_data.read().decode()
            object_murd = Murd(name=row, murd=read_data)
        except Exception:
            if not allow_missing:
                raise Exception(f"Unable to process data from {row}")

        return object_murd

    def retrieve_murd_rows(self, rows, allow_missing=True):
        return run_async(
            self.retrieve_murd_row,
            [{"row": row,
              "allow_missing": allow_missing} for row in rows])

    def update(
        self,
        mems,
        identifier="Unidentified"
    ):
        mems = MurdMemory.prime_mems(mems)
        rows = set([mem['ROW'] for mem in mems])
        mems_by_row = defaultdict(list)
        for mem in mems:
            mems_by_row[mem['ROW']].append(mem)

        murds_by_row = {row: Murd(json.dumps(mems)) for row, mems in mems_by_row.items()}

        for kwargs, murd in run_async(self.retrieve_murd_row, [{"row": row} for row in rows]):
            murds_by_row[kwargs['row']].extend(murd)

        def upload_murd(row, mems, row_murd, bucket):
            row_murd.update(mems)
            murd_json = BytesIO(row_murd.murd.encode())
            bucket.upload_fileobj(Key=row, Fileobj=murd_json)

        kwargs = [{
            "row": row,
            "mems": mems,
            "row_murd": murds_by_row[row],
            "bucket": self.bucket
        } for row, mems in mems_by_row.items()]
        run_async(upload_murd, kwargs)

    def read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None
    ):
        object_summaries = self.retrieve_s3_summaries(row)
        kwargs = [{"row": os.key} for os in object_summaries]
        kwargs, all_murds = zip(*run_async(self.retrieve_murd_row, kwargs))
        all_murds = list(all_murds)
        if not all_murds:
            return []
        murd = all_murds.pop()
        for foreign_murd in all_murds:
            murd.connect(foreign_murd)
        read_data = murd.read_all(row, col, greater_than_col, less_than_col)
        return read_data

    def delete(self, mems):
        mems = MurdMemory.prime_mems(mems)
        rows = set([mem['ROW'] for mem in mems])
        kwargs, all_murds = zip(*self.retrieve_murd_rows(rows))

        s3_client = boto3.client("s3")
        s3_client.delete_object()

        data = {'mems': json.dumps(mems)}
        resp = _request("DELETE", self.url,
                        body=json.dumps(data).encode('utf-8'))

        if resp.status != 200:
            raise Exception("Murd delete request failed")

        stubborn_mems = json.loads(resp.data.decode("utf-8"))
        return [MurdMemory(**sm) for sm in stubborn_mems]
