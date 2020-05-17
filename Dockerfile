###############
# Base Python #
###############
FROM python:3.8-slim-buster AS base-autoapi

# Virtualenv PATH
ENV PATH="/opt/venv/bin:$PATH"


######################
# Base testing image #
######################
FROM base-autoapi AS base-testing-autoapi

RUN apt update --quiet 3 > /dev/null 2>&1 && \
	apt install --no-install-recommends --yes --quiet 3 gnupg curl > /dev/null 2>&1 && \
	curl -fsSL https://www.mongodb.org/static/pgp/server-4.2.asc | apt-key add - > /dev/null 2>&1 && \
	echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" > /etc/apt/sources.list.d/mongodb-org-4.2.list && \
	apt update --quiet 3 > /dev/null 2>&1 && \
	apt install --no-install-recommends --yes --quiet 3 mongodb-org-server=4.2.6 > /dev/null 2>&1


#################
# Builder image #
#################
FROM base-autoapi AS builder-autoapi

WORKDIR /app

# Create Virtualenv
RUN python -m venv /opt/venv

# Upgrade python tools
COPY requirements-tools.txt ./
RUN pip install --quiet --upgrade --requirement requirements-tools.txt

# Install python dependencies
COPY requirements.txt ./
RUN pip install --quiet --requirement requirements.txt

# Install AutoApi
COPY auto_api ./auto_api
COPY LICENSE setup.py setup.cfg ./
RUN pip install --quiet --no-dependencies .


#################
# Testing image #
#################
FROM base-testing-autoapi AS testing-autoapi

WORKDIR /app

# Installed python modules
COPY --from=builder-autoapi /opt/venv /opt/venv

# Install python dev dependencies
COPY requirements-dev.txt ./
RUN pip install --quiet --requirement requirements-dev.txt

# Run tests
COPY tests ./tests
COPY run_tests.py ./
RUN python run_tests.py


####################
# Production image #
####################
FROM base-autoapi AS runtime-autoapi

# Installed python modules
COPY --from=builder-autoapi /opt/venv /opt/venv

# AutoApi user
ARG user=app
RUN useradd --create-home $user

# AutoApi port
ARG port=8686
ENV PORT=$port
EXPOSE $port

# AutoApi entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Setup service
USER $user
WORKDIR /home/$user
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--bind :", "echo $PORT"]