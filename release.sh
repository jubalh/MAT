#!/bin/sh


# Release script for the MAT


echo "Previous version: $(git describe --abbrev=0)"
echo "Please enter the new version number"
read VERSION

echo '[+] Update version number'
sed s/__version__\ =\ \'[0-9\.]*\'/__version__\ =\ \'${VERSION}\'/ MAT/mat.py # > mat.py
sed s/__version__\ =\ \'[0-9\.]*\'/__version__\ =\ \'${VERSION}\'/ setup.py # > mat.py

echo '[+] Update changelog'
vim -O CHANGELOG <(git log --graph --pretty=format:'%h -%d %s (%cr) )<%an>' --abbrev-commit --date=relative)

echo '[+] Commit the changelog'
git commit CHANGELOG MAT/mat.py setup.py -m 'Update changelog and bump version'

echo '[+] Create a tag'
git tag -s ${VERSION}

echo '[+] Push the tag'
git push --tags origin

echo '[+] Create the release archive'
git archive --format=tar.gz --prefix=mat-${VERSION}/ ${VERSION} > mat-${VERSION}.tar.gz

echo '[+] Sign the archive'
gpg --armor --detach-sign mat-${VERSION}.tar.gz

# Recall
echo '[+] Release done'
echo "[*] Don't forget to:"
echo "\t- Upload archives to https://mat.boum.org/files"
echo "\t- Add changelog to https://mat.boum.org/"
echo "\t- Have a nice day"
