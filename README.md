# Github ssh public key collector

This script can be used to collect ssh public keys of users listed in
`keys.ini` file and write them to a seperate file.
It is also possible to collect keys of users that
are part of a Github organization.

You can then use the generated files for keeping your ssh machines
authorized_keys file up to date with changes to your user ssh keys.

you could for example serve the key output folder over https and then
`curl https://youserver.com/keys/core-team > /root/.ssh/authorized_keys`
in your target machine.

# Installation
1. Copy `keys.service` and `keys.timer` to `/etc/systemd/system` folder
2. Edit `keys.service`
   1. `WorkingDirectory` sets where the final keys are put
   2. Environment variable `GITHUB_TOKEN` is used to access
        organization members
   3. Environment variable `KEYS_CONFIG` sets the path to
        `.ini` config file
   4. In `ExecStart` line point Python to correct `keys.py` path
3. Edit `keys.timer` to set update refresh rate.
4. Create keys.ini file. Here are some examples.

    * Write single user keys to a file `$PWD/authorized_keys`
        ```
        [authorized_keys]
        users = artizirk
        ```
    * Write keys of several users to a file `$PWD/dev_team_keys`
        ```
        [dev_team_keys]
        users = artizirk, CoolUser123
        ```
    * Write keys of all the organization members to `$PWD/all_of_us`
        ```
        [all_of_us]
        org = Teamer
        ```
    * Write keys of only organization members that are part of some teams
        ```
        [core-team]
        org = Teamer
        teams = devs, testers
        ```
    * Write keys of only organization members that are part of some teams
        and add few other users that are not part of the organization
        ```
        [core-team+power-users]
        org = Teamer
        teams = devs, testers
        users = artizirk, CoolUser123
        ```

    `keys.ini` file can contain several sections, each section is
    written to a separate file.

    In each section, the `org` key can contain only a single Github
    Organization.

    `teams` key can contain a list of coma (,) separated
    list of teams who's keys will be included.

    `users` key can contain a list of coma (,) seperated list of any
    github user. User does not have to be apart of any team.

5. Running it

    * `systemctl start keys.service`

    * `GITHUB_TOKEN=sadfsadf python3 keys.py`
