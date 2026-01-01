# [TEAW-Website](https://toendallwars.org/)
Welcome to the Git repo for the ToEndAllWars website! Here is the place to find source code, post issues, and submit pull requests. 
We gladly welcome community contributions, we just ask that you test them first. 


## TODO:
- [ ] Put the project in a venv
- [ ] Add a TEAW Times archive page

## Git guidelines
There are two branches, `prod` and `dev`. The default is `dev`, and where any changes should be made. 

In the future, changes will be deployed by bringing changes over from dev (or some other branch) to prod using a pull request.
Only once approved, will the PR be merged, and the new changes deployed using a GH webhook. 

Before submitting a pull request, run the VS Code task to generate the `requirements.txt` file for pip.


## Dependencies
This website uses [Sass](https://sass-lang.com/) for styles, and as such a Sass compiler with `sass` must be available on your development or production machine, and in the system's PATH. Alternatively, you can edit the webserver file to adjust the sass command usage to your needs.

There are also several required Python Packages. Install them with `pip install -r requirements.txt`.


## Starting a development server
To start a local version of the website for testing/development, run the
`teaw_webserver.py` file. This will start Flask in debug mode, with the logger set
to the DEBUG level. This will also enable Flask's debug mode. For any changes to show
up on the website, the process must be restarted.

> [!NOTE]
> In order for the server and API to work, the SQLite DBs will need to contain information. By default, there is some 
data in them. The data will not be updated unless the `db_updater.py` and `stats_updater.py` processes are started, 
but thats not needed for development. 


## Starting a production server
To deploy the server, run the `run_prod.sh` script with Bash. This will take the Flask `app` variable inside the
`teaw_webserver` script, and start it with Gunicorn. Note that this disables any debugging features, and can only be ran on Linux.

The `db_updater.py` and `stats_updater.py` processes need to be started, so the databases are updated. It is best to use 
[tmux](https://github.com/tmux/tmux?tab=readme-ov-file#welcome-to-tmux) to open and keep running the DB updaters and the webserver.

Alternatively, you can use the [create_session.sh](https://github.com/besser435/TEAW-Website/blob/dev/create_session.sh)script to manage the tmux windows and start the tasks. The files can also be ran as processes.

(yes I know tmux is not a proper process management tool, but it works well)
