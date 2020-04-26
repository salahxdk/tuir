Release Checklist
-----------------

1. Switch to the master branch and stash/commit any uncommited changes.
2. Bump the version number in [tuir/\_\_version\_\_.py](tuir/__version__.py).
3. Update the release notes in the [CHANGELOG.rst](CHANGELOG.rst).
4. Update the contributor list by running [``scripts/build_authors.py``](scripts/build_authors.py).
5. Commit all changes to the correct branch and tag the correct commit with its version.
6. Re-generate the manpage by running [``scripts/build_manpage.py``](scripts/build_manpage.py).
7. Smoke test the new release on Python 3.
8. Push the unpublished changes and the tag.
9. Clean out any old build/release files by running [``scripts/pip_clean.py``](scripts/pip_clean.py).
10. Build the source tarball and binary wheel: ``$ python3 setup.py sdist bdist_wheel``
11. Upload the packages to PyPI: ``$ twine upload dist/*``
12. Verify that the upload was successful: ``$ pip install tuir --upgrade --force-reinstall``
13. Delete any old and unused branches that have been merged.
