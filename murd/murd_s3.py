import json
from io import BytesIO
import boto3

from .murd import MurdMemory
from .murd import Murd


class MurdS3Client:
    """ Murd API Client """

    def __init__(
        self,
        bucket
    ):
        self.bucket_name = bucket_name
        self.bucket = boto3.resource("s3").Bucket(self.bucket_name)

    def update(
        self,
        mems,
        identifier="Unidentified"
    ):
        mems = MurdMemory.prime_mems(mems)
        data = {'mems': json.dumps(mems)}
        raise Exception("Murd update request failed")

    def read(
        self,
        row,
        col=None,
        greater_than_col=None,
        less_than_col=None
    ):
        s3_client = boto3.client("s3")
        prefix = "" 
        if col is not None:
            prefix = col
        object_summaries = []

        try:
            for object_summary in self.bucket.objects.all():
                if greater_than_col is not None and object_summary.key < greater_than_col:
                    continue
                if less_than_col is not None and object_summary.key > greater_than_col:
                    continue
                if col is not None and col not in object_summary.key:
                    continue
                object_summaries.append(object_summary)
        except s3_client.exceptions.NotFoundException:
            print("Error accessing Murd Bucket")
            raise

        for object_summary in object_summaries:
            read_data = BytesIO()
            data = self.bucket.download_fileobj(Key=object_summary.key, FileObj=read_data)
            try:
                read_data = read_data.read().decode()
                object_murd = Murd(name=object_summary.key, murd=read_data)
            except Exception:
                print(f"Unable to process data from {object_summary.key}")
            all_data.append(object_murd)
        for murd in all_murds:
            murd.join(all_murds)

        read_data = murd.read(row, col, greater_than_col, less_than_col)
        return read_data

    def delete(self, mems):
        mems = MurdMemory.prime_mems(mems)

        s3_client = boto3.client("s3")
        s3_client.delete_object()

        data = {'mems': json.dumps(mems)}
        resp = _request("DELETE", self.url,
                        body=json.dumps(data).encode('utf-8'))

        if resp.status != 200:
            raise Exception("Murd delete request failed")

        stubborn_mems = json.loads(resp.data.decode("utf-8"))
        return [MurdMemory(**sm) for sm in stubborn_mems]
