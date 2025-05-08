# redis
Extracted from the airflow docer compose. It should be a stack service but I did it mostly to de-clutter the airflow file.

reserved redis databases (we try to configure services And avoid using database 0, as that would be a common default value and might cause obscure clashes):

* 1 - airflow

## redisinsight
For fun I added the redisinsight web client: https://hub.docker.com/r/redis/redisinsight

It's avaialble on http://127.0.0.1:8007 you need to configure a new database;

 `redis://default@redis:6379`
