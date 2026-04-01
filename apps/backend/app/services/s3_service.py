# 把 AWS SDK 细节藏在这里，endpoint 不需要知道 S3 怎么工作
def upload_file(file, filename):
    s3_client.upload_fileobj(file, BUCKET_NAME, filename)
`