# depman
Dependency management for those who are tired of dependency management.

This tool was written to solve the problem of having to manage lots of dependencies in projects utilize languages with no good dependency management system (i.e C and C++).

While there exist a lot of package management systems for C and C++, there are no good ones that are lightweight and work for any dependency. *depman* aims to provide a simple script that can be added as a git submodule or simply in-place to any repository, and provides limitless dependency management. As it is written in Python, *depman* will run on any platform supported by Python.

*depman* is a source dependency management tool, it manages dependencies by downloading and updating source repositories.

## How to use *depman*

To use depman, you will need Python installed on your system, as well as any version control software required by your dependencies. Currently, depman only supports git, but support for Mercurial, SVN and others are planned.

1. You can add *depman* to your project as a git submodule (after running `git submodule init`):
```bash
git submodule add https://github.com/Mischa-Alff/depman depman
```
Then, you can then simply run *depman* with `python depman/depman.py`

or:

2. You can just add `depman.py` to your codebase.
Then, you can then simply run *depman* with `python path/to/depman.py`

or you can add those python commands to a script, like `depman.sh`:
```bash
#!/bin/bash
python ./path/to/depman.py $@
```

Once depman is installed, you can list the dependencies present in your `depman.json` using `python path/to/depman.py list`.

You can download dependencies using
```bash
python path/to/depman.py update
```

and obtain more detailed information with
```bash
python path/to/depman.py --help
```

## How to write a depman.json

The `depman.json` format is quite simple. Examples can be found at [the examples page](./examples/).

At its simplest, it's just a list of repositories to clone:
```json
{
	"dependencies": [
		{
			"location": "https://github.com/Mischa-Alff/depman.git"
		},
		{
			"location": "https://github.com/github/linguist.git",
			"name": "gh-linguist",
			"version": "v6.3.1"
		}
	]
}
```

This will clone *depman* from the master branch into the `deps/depman` folder, and *linguist* from tag v6.3.1 into the `deps/gh-linguist` folder.

The `deps/` folder is the default location for *depman* dependencies. If you'd like to change it, your `depman.json` file can be changed to look like this:
```json
{
	"config": {
		"dependencies_dir": "./foodeps"
	},
	"dependencies": [
	]
}
```

So far, these are the values that can be used in the depman.json `config` section:

| Name               | Description                                                    |
| ------------------ | -------------------------------------------------------------- |
| *dependencies_dir* | The location to store dependencies in, relative to depman.json |

## Why not just use submodules?

Submodules in Git are notoriously bad for dependency management. They are locked to specific commits, which means if you want to develop a dependency along with a main project, you end up with having to update submodules all the time.

With depman, you can track a specific branch or tag and keep up to date with that, allowing you to lock to a specific version if needed, or stay at the tip of a branch.
