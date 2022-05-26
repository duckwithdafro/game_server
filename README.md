# Introduction
This is a very newly layed egg of an idea and it needs time to incubate, as I've only thought about it for a little.
So far, I only decided what I'm going to use to develop it, and I'm not sure how its going to work out.
This is inspired by club penguin and how it gave children something to look forward to before and after school.
With that said, i plan on it to be easily accessible to anyone who wants to use it, whether its on their browser or mobile or a desktop app.

## This is the server for the game.
This means this repository won't be the part that is on a users computer. Here is the [client repository](https://github.com/minecrosters/game_client)!

## The server tech stack

1. [Python 3.8.5](https://www.python.org/downloads/release/python-385/) <!-- specifically 3.8.5 because idk if it matters but im not taking a risk with that --> - Might as well use something familiar to me, makes it easier to develop.
2. [FastAPI](https://fastapi.tiangolo.com/) - Web framework for Python, makes it easier to create RESTful APIs.
3. [SuperTokens python SDK](https://supertokens.com/docs/python/index.html) - For authentication and authorization, makes it easier to create and use tokens. <!-- You didnt think i would implement this myself, did you? -->

### dev dependencies
1. [isort](https://pycqa.github.io/isort/) - Organizes imports in Python code, makes it easier to organize imports.
2. [black](https://black.readthedocs.io/en/stable/) - Formats Python code, makes it easier to read.
3. [poetry](https://python-poetry.org/) - Manages dependencies for Python projects, makes it easier to manage dependencies.