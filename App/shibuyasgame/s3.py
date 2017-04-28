# Taken directly from s3-example

import configparser
import boto
import io
import os

from boto.s3.key import Key
from webapps.settings import BASE_DIR

config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

AWS_ACCESS_KEY = config.get('S3', 'AccessKey')
AWS_SECRET_ACCESS_KEY = config.get('S3', 'SecretKey')
S3_BUCKET_USER = config.get('S3', 'UserBucket')
S3_BUCKET_CHAR = config.get('S3', 'CharBucket')


def s3_upload(uploaded_file, id, user):
    s3conn = boto.connect_s3(AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY)
    if user:
        bucket = s3conn.get_bucket(S3_BUCKET_USER)
    else:
        bucket = s3conn.get_bucket(S3_BUCKET_CHAR)

    k = Key(bucket)
    k.key = 'id-' + str(id)
    k.content_type = uploaded_file.content_type

    if hasattr(uploaded_file,'temporary_file_path'):
        k.set_contents_from_filename(uploaded_file.temporary_file_path())
    else:
        k.set_contents_from_string(uploaded_file.read())

    k.set_canned_acl('public-read')

    return k.generate_url(expires_in=0, query_auth=False)
