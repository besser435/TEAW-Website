# TEAW-Website


## TODO:
- Figure out how to not erase db dir on push to prod (data will be lost!)
- Improve tmux script


## Git guidelines
There are two branches, `prod` and `dev`. The default is `dev`, and where any changes should be made. 

In the future, changes will be deployed by bringing changes over from dev (or some other branch) to prod using a pull request.
Only once approved, will the PR be merged, and the new changes deployed using a GH webhook. 

Before submitting a PR, run the VS Code task to generate the requirements.txt file for pip.


## Starting a development server
To start a local version of the website for testing/development, run the
`teaw_webserver.py` file. This will start Flask in debug mode, with the logger set
to the DEBUG level. This will also enable Flask's debug mode. For any changes to show
up on the website, the process must be restarted.

> [!NOTE]
> In order for the server and API to work, the SQLite DBs will need to contain information. By default, there is some 
data in them. The data will not be updated unless the `db_updater.py` and `stats_updater.py` processes are started, 
but thats not needed for development. 

TODO: add the example data.



## Starting a production server
To deploy the server, run the `run_prod.sh` script with Bash. This will take the Flask `app` variable inside the
`teaw_webserver` script, and start it with Gunicorn. Note that this disables any debugging features, and can only be ran on Linux.

The `db_updater.py` and `stats_updater.py` processes need to be started, so the databases are updated. It is best to use 
[tmux](https://github.com/tmux/tmux?tab=readme-ov-file#welcome-to-tmux) to open and keep running the DB updaters and the webserver.
In the future there will be a Bash script to automatically destroy an existing tmux session, and create new ones which contain the 
required processes.

(yes I know tmux is not a proper process management tool, but it works well)