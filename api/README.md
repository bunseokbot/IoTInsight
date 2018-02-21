## IOTInsight backend reference

### How to install

* Download & install python 3.x from official website

  [Download Python 3.x](https://www.python.org/ftp/python/3.6.4/python-3.6.4.exe)

  **You should enable the windows PATH (system environment) option while installing python.**

  ​

* Install python requirement modules

  ```bash
  pip install -r requirements.txt
  ```

  ​

* Download & Install winpcap

  Because of packet dump file level analysis, you have to install winpcap if your computer doesn't installed winpcap or wireshark.

  [Download latest winpcap](https://www.winpcap.org/install/)



### How to test parsers

Just run all testcases in a single `run_tests.py` file and check parsers running normally on your computer.

```bash
python run_tests.py
```

* Want to add more testcase?

  Add python unittest testcase class file at tests/ directory.



### How to run IoTInsight API Server

* Run Redis server

  ```
  bin/redis-server.exe
  ```

  ​

* Run Celery task

  ```bash
  celery -A tasks worker --loglevel=info -P eventlet
  ```

  ​

* Run Flask API server

  ```bash
  python app.py
  ```




### Configuration

All configurations are defined in `config.ini` single file.

* web
  * host: host IP address to bind API server
  * port: API server port
  * threaded: API server multi-threading option
* redis
  * host: redis host
  * port: redis port
  * db: redis database



**Example**

```t
[web]
threaded = True

[redis]
host = localhost
port = 6379
db = 0
```



### API Reference

#### Analysis request

- **image** POST /task/request/image

  **Parameter**

  ```
  filetype=<image file type, packet|onhub>
  filepath=<path of image file>
  ```

  **Response**

  ```json
  {
  	"task_id": "954e023d-fd92-4f9c-8c4f-f25b9d991084"
  }
  ```

  ​

- **account** POST /task/request/account

  **Parameter**

  ```
  service=<cloud service, alexa|smartthings>
  access_token=<access token of cloud service account, optional>
  ```

  |    Cloud Service    |       Login method        |     Required parameters     |
  | :-----------------: | :-----------------------: | :-------------------------: |
  |    Amazon Alexa     | Username / Password based | service, username, password |
  | Samsung Smartthings |    Access Token based     |    service, access_token    |

  **Response**

  ```json
  {
  	"task_id": "954e023d-fd92-4f9c-8c4f-f25b9d991084"
  }
  ```


- **Response if failure or invalid error** (all request API unified response)

  HTTP status code 400

  ```json
  {
  	"message": "<Error Message>"
  }
  ```

  ​

#### Check analysis status

GET /task/status/(id)

```json
{
	"status": "pending|processing|success|failure"
}
```


#### Bulk task upload & automatic filetype detection

POST /task/bulk

**Parameter**

```
filepath=<path to detect filetype>
```

**Response**

```json
{
  "/Users/bunseokbot/Desktop/samples/004-Onhub-diagnostic-report": {
    "filetype": "onhub",
    "task_id": "32db64c5-2730-4b76-9285-2c7ca74a4cb0"
  },
  "/Users/bunseokbot/Desktop/samples/006-SmartHome-Cloud-Provider-AcmeInc-NetworkDump.pcap": {
    "filetype": "packet",
    "task_id": "89a69805-943a-436f-9071-b0e88f03c6de"
  }
}
```

