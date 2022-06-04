# Release Procedure

You can copy the raw source of this document to an issue or pull request for the release to use as an interactive checklist, if desired.

**Note**: We use `pip` instead of `conda` here even on Conda installs, to ensure we always get the latest upstream versions of the build dependencies.


## Prepare

* [ ] Close [GitHub milestone](https://github.com/project-mjolnir/sindri/milestones) and ensure all issues are resolved/moved

* [ ] In a bash-like shell locally and on the Pi/server, set up the variables needed (otherwise, replace them manually)

  ```bash
  # Full version number to release, e.g. '1.2.3b4'
  VERSION='VERSION_NUMBER'
  # Git branch to make the release from, e.g. 'main', 'master' or '1.x'
  MAIN_BRANCH='BRANCH_NAME'
  # Prepare-release branch name
  PREPARE_RELEASE_BRANCH=prepare-release-$VERSION
  # Release branch name, if a new major/minor release, e.g. '1.x' or '0.4.x'
  RELEASE_BRANCH=$MAIN_BRANCH
  # Set mode to 'client' (if on a Pi) or 'server' (if on the central VPS)
  MODE='MODE_NAME'
  ```

  or, all in one line,

  ```bash
  VERSION='VERSION_NUMBER'; MAIN_BRANCH='BRANCH_NAME'; PREPARE_RELEASE_BRANCH=prepare-release-$VERSION; RELEASE_BRANCH=$MAIN_BRANCH; MODE='MODE_NAME'
  ```

* [ ] Update local repo

  ```shell
  git reset --hard && git switch $MAIN_BRANCH && git pull upstream $MAIN_BRANCH
  ```

* [ ] Clean local repo

  ```shell
  git clean -xdi
  ```

* [ ] Perform a quick local smoke-test of the final development version

  ```shell
  python -b -X dev -m pip install -e .
  pylint src/sindri
  python -I -bb -X dev -W error -m sindri --version
  python -I -bb -X dev -W error -m sindri serve-website --mode test
  # Check that output website displays and behaves as expected, with no JS errors
  ```


## Commit

* [ ] Create a new branch for the release

  ```shell
  git switch -c $PREPARE_RELEASE_BRANCH
  ```

* [ ] Ensure docs and metadata are up to date and commit any changes

  * [ ] [Release Guide](./RELEASE.md)
  * [ ] [License](./LICENSE.txt)
  * [ ] [Readme](./README.md)
  * [ ] [Contributing Guide](./CONTRIBUTING.md)
  * [ ] [MANIFEST.in](./MANIFEST.in)
  * [ ] [setup.cfg](./setup.cfg) (Python/dep version reqs, classifiers, other metadata)
  * [ ] [Roadmap](./ROADMAP.md)

* [ ] Update [`CHANGELOG.md`](./CHANGELOG.md) with the latest changes

* [ ] Update `__version__` in [`__init__.py`](./src/sindri/__init__.py) (set release version, remove `.dev0`)

  ```shell
  nano src/sindri/__init__.py
  ```

* [ ] Create release commit

  ```shell
  git commit -m "Release Sindri version $VERSION"
  ```

* [ ] Push the prepare-release branch to your fork

  ```shell
  git push -u origin $PREPARE_RELEASE_BRANCH
  ```

* [ ] Open a [pull request](https://github.com/project-mjolnir/sindri/pulls) for the branch


## Test

* [ ] On the Pi/server, pull the prepare-release branch

  ```shell
  git reset --hard && git fetch --all && git switch $PREPARE_RELEASE_BRANCH
  ```

* [ ] Clean repository of old artifacts

  ```shell
  git clean -xdi
  ```

* [ ] Create and activate a fresh virtual environment for testing

  ```shell
  python -m venv test-env && source test-env/bin/activate
  ```

* [ ] Install/update the packaging stack

  ```build
  python -m pip install --upgrade pip
  pip install --upgrade build setuptools wheel
  ```

* [ ] Build the distribution packages

  ```build
  python -bb -X dev -W error -m build
  ```

* [ ] Install from built wheel

  ```shell
  python -b -X dev -m pip install dist/sindri-$VERSION-py3-none-any.whl
  ```

* [ ] Check environment

  ```shell
  pip check; python -I -bb -X dev -W error -m sindri --version
  ```

* [ ] Test package

  ```
  python -I -bb -X dev -W error -m sindri serve-website --mode $MODE
  # Check that output website displays and behaves as expected, with no JS errors
  ```


## Stage

* [ ] On the Pi/server(s), activate the production virtual environment

* [ ] Disable and stop Sindri service

  ```shell
  sudo systemctl disable sindri-hamma-$MODE && sudo systemctl stop sindri-hamma-$MODE
  ```

* [ ] Reinstall the package from the built wheel

  ```shell
  python -b -X dev -m pip install dist/sindri-$VERSION-py3-none-any.whl
  ```

* [ ] Reinstall service

  ```shell
  sudo /$PATH_TO_VENV/bin/python -I -bb -X dev -W error -m sindri install-service -vvv --mode $MODE --account $ACCOUNT --extra-args "${EXTRA_ARGS}"
  ```

* [ ] Restart services

  ```shell
  sudo systemctl restart sindri-hamma-$MODE
  ```

* [ ] Verify still running, no errors and functioning correctly after 60 seconds

  ```shell
  systemctl status sindri-hamma-$MODE
  ```


## Build

* [ ] Activate the appropriate venv/conda environment

* [ ] Clean local repo

  ```shell
  git clean -xdi
  ```

* [ ] Update the packaging stack

  ```shell
  python -m pip install --upgrade pip
  pip install --upgrade --upgrade-strategy eager build setuptools twine wheel
  ```

* [ ] Build source distribution and wheel

  ```shell
  python -bb -X dev -W error -m build
  ```


## Check

* [ ] Check Pylint

  ```shell
  pylint src/sindri
  ```

* [ ] Check distribution archives

  ```shell
  twine check --strict dist/*
  ```

* [ ] Check installation

  ```shell
  python -b -X dev -m pip install dist/sindri-$VERSION-py3-none-any.whl
  ```

* [ ] Check environment

  ```shell
  pip check; python -I -bb -X dev -W error -m sindri --version
  ```

* [ ] Check functionality

  ```shell
  python -I -bb -X dev -W error -m sindri serve-website --mode test
  # Check that output website displays and behaves as expected, with no JS errors
  ```


## Release

* [ ] Upload distribution packages to PyPI

  ```shell
  twine upload dist/*
  ```

* [ ] Create release tag

  ```shell
  git tag -a v$VERSION -m "Sindri version $VERSION"
  ```

* [ ] Merge the prepare-release branch to `$MAIN_BRANCH`, or the pull request

  ```shell
  git switch $MAIN_BRANCH && git merge $PREPARE_RELEASE_BRANCH
  ```

* [ ] If new major or minor version, create release branch and push

  ```shell
  git switch -c $RELEASE_BRANCH && git push -u origin $RELEASE_BRANCH && git push upstream $RELEASE_BRANCH && git switch $MAIN_BRANCH
  ```


## Finalize

* [ ] Update `__version__` in [`__init__.py`](./src/sindri/__init__.py) (increment to next, add `.dev0`)

  ```shell
  nano src/sindri/__init__.py
  ```

* [ ] Create a `back to work` commit with the next anticipated version on the branch

  ```shell
  git commit -m "Begin development of version $VERSION"
  ```

* [ ] Reinstall the development version locally in editable mode

  ```shell
  python -b -X dev -m pip install -e .
  ```

* [ ] Push new release commits and tags to `$MAIN_BRANCH`

  ```shell
  git push upstream $MAIN_BRANCH --follow-tags
  ```

* [ ] Create a [GitHub release](https://github.com/project-mjolnir/sindri/releases) from the tag with the changelog contents

* [ ] Open a [GitHub milestone](https://github.com/project-mjolnir/sindri/milestones) as needed for the next release


## Deploy

* [ ] On the Pi/server, install the released version from PyPI

  ```shell
  pip install sindri
  ```

  Or, pull the release branch, checkout the tag and editable-install

  ```shell
  git fetch --all && git switch $RELEASE_BRANCH && git checkout v$VERSION && pip install -e .
  ```

* [ ] Restart the service and verify working

  ```shell
  sudo systemctl restart sindri-hamma-$MODE && sleep 10 && systemctl status sindri-hamma-$MODE
  ```


## Cleanup

* [ ] On the Pi/server, remove the clean test virtual environment

  ```shell
  rm -rfd test-env
  ```

* [ ] Delete the prepare-release branch locally and on the Pi/server

  ```shell
  git branch -d $PREPARE_RELEASE_BRANCH
  ```

* [ ] Delete the prepare-release branch on the remote

  ```shell
  git push -d origin $PREPARE_RELEASE_BRANCH
  ```
