# Make sure the virtual environment used to run Pontoon exists
if [ -d "./venv" ]
then
    source ./venv/bin/activate
else
    pip3 install virtualenv
    python3 -m virtualenv venv
    source ./venv/bin/activate
    pip install -r requirements.txt
fi

# Flask ENV Variables
export FLASK_ENV=${FLASK_ENV:-development}

# Redis ENV Variables
export REDIS_HOST=${REDIS_HOST:-127.0.0.1}
export REDIS_PORT=${REDIS_PORT:-6379}
export REDIS_DB=${REDIS_DB:-0}
# export REDIS_USER=
# export REDIS_PASS=

# Pontoon ENV Variables
export PONTOON_HOST=${PONTOON_HOST:-127.0.0.1}
export PONTOON_PORT=${PONTOON_PORT:-5000}
export PONTOON_SSL=${PONTOON_SSL:-false}
export PONTOON_AUTH=${PONTOON_AUTH:-false}
# export PONTOON_CERT=
# export PONTOON_KEY=

# If we set --build-only then we won't start the Flask app.
for i in "$@" ; do
  if [[ $i == "--build-only" ]]
  then
    exit 0
  fi
done

# Start Pontoon
python pontoon.py
