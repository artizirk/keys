#!/usr/bin/env python3
"""
Simple HTTP endpoint for getting list of ssh keys from multible sources
"""

# Monkypatch
from github.NamedUser import NamedUser
NamedUser.__hash__ = lambda self: hash(self.id)

import os
import sys
from functools import lru_cache
from pathlib import Path
from configparser import ConfigParser

from github import Github

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    print("GITHUB_TOKEN environment variable is not set.")
    sys.exit(1)

KEYS_CONFIG = Path(os.environ.get("KEYS_CONFIG", "keys.ini"))
if not KEYS_CONFIG.exists():
    print('Config file "{}" does not exist. Specify one in KEYS_CONFIG environment variable.'.format(KEYS_CONFIG))
    sys.exit(1)


github = Github(GITHUB_TOKEN)
github.get_rate_limit()
print("You have {} request(s) left of {}".format(*github.rate_limiting))

config = ConfigParser()
config.read(str(KEYS_CONFIG))


def get_org_members(org, teams=None):
    organization = github.get_organization(org)
    if teams:
        for team in organization.get_teams():
            if team.name in teams:
                print("Getting members from {} team {}".format(org, team.name))
                for member in team.get_members():
                    yield member
    else:
        print("Getting members from {}".format(org))
        for member in organization.get_members():
            yield member

@lru_cache()
def get_keys(user):
    for key in user.get_keys():
        yield key.key



for endpoint, section in config.items():
    if endpoint == "DEFAULT":
        continue
    keys = set()
    members = set()
    print("Collecting keys for {}".format(endpoint))
    org = section.get("org", "").strip()
    if org:
        teams = [team.strip() for team in section.get("teams", "").split(",") if team.strip()]
        members.update(get_org_members(org, teams))
    if section.get("users", "").strip():
        for user in section["users"].split(","):
            user = user.strip()
            if not user:
                continue
            members.add(github.get_user(user))

    for member in members:
        print("  Collecting {} keys".format(member.login))
        keys.update(get_keys(member))

    if not keys:
        continue

    print("Writing all the keys to file {}".format(endpoint))
    with open(endpoint, "w") as f:
        for key in keys:
            f.write(key)
            f.write("\n")
