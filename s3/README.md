# minio S3 service
A common object store for freeds.
docs: https://min.io/docs/minio/container/index.html

Normally you'd be on cloud but that's not "free". So we spin up our own S3 object store.
minio is production grade and not a mock service like s3-ninja (which was the first I tried).
Turned out minio was actually easier to use than s3-ninja since it is properly documented.
