# SlaveBot

### Install MySql

https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04

### Install drivers for mysql and python and pip

sudo apt-get install python-pip python-dev libmysqlclient-dev

Clone the project

```
git clone https://github.com/JuniorZavaleta/slave-bot
```

Go to the directory

```
cd slave-bot
```


Create a virtual env
```
virtualenv venv --distribute
```

Activate the virtual env
```
source venv/bin/activate
```

Install the dependencies
```
pip install -r requirements.txt
```

Use ngrok and configure your webhook on developers facebook dashboard