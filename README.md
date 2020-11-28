# DNS Blocklist Queries Using GraphQL

This app queries a blocklist to determine is an IP address is included on that blocklist. This API is implemented in GraphQL and Flask.

## Set-up

Set-up a virtual environment and activate it:

```bash
python3 -m venv env
source env/bin/activate
```

You should see (env) before your command prompt now. (You can type `deactivate` to exit the virtual environment any time.)

Install the requirements:

```bash
pip install -U pip
pip install -r requirements.txt
```

If you are a developer:

```bash
pip install -U pip
pip install -r requirements-dev.txt
```

## Usage

You can run this app either locally, in a Docker container, or deploy it to Heroku.

### Local

Make sure you are in the virtual environment (you should see (env) before your command prompt). If not `source /env/bin/activate` to enter it.

```bash
Usage: flask run
```

### Container

You will need the [Docker Engine](https://docs.docker.com/engine/install/) installed. On Ubuntu:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

You will also need [Docker Compose](https://docs.docker.com/compose/install/) installed. On Ubuntu:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

You can set which port you would like to run it on by setting the environment variable PORT in your shell.

```bash
export PORT=5000
```

Then running it as simple as:

```bash
docker-compose up
```

### Heroku

You will need the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed. On Ubuntu:

```bash
sudo snap install --classic heroku
```

Then you can deploy to Heroku.

```bash
heroku create dns-blocklist-graphql
heroku stack:set container
git push heroku main
```

## Example

There is currently an example running on Heroku [here](https://dns-blocklist-graphql.herokuapp.com/).

## Testing Suite

The app has a full unittest suite.

To run all the tests:

```bash
Usage: test_app.py
```

## Credit

[Secureworks](https://www.secureworks.com/)

## License

DNS Blocklist Queries Using GraphQL is licensed under the [MIT license](https://github.com/danrneal/dns-blocklist-graphql/blob/master/LICENSE).
