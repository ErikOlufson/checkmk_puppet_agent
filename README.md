# Puppet Module for Check-Mk running on Debian derivates.

The module is working for Puppet 3 and Puppet 4 installations. It requires Python 2.7 and will not run with Python 3. The OS has to be a Debian derivate like Debian itself or Ubuntu.

Requirements:
* Python 2.7
* Python Apt Module

Performance date are:
* execution time of last run in seconds
* size of state.yaml in KB

Checks are:
* Puppet agent is installed?
  * OK if package "puppet" or "puppet-agent" is installed.
  * CRITICAL if not.   
* Puppet agent is running?
  * OK if process is running. 
  * CRITICAL if not.
* Puppet agent was running the last hour and the last day.
  * OK if delta between current timestamp and last_run timestamp < 3600
  * WARNING if delta between current timestamp and last_run timestamp > 3600 and < 86400
  * CRITICAL if delta between current timestamp and last_run > 86400
* Puppet agent ran without errors.
  * OK if failures is 0.
  * CRITICAL if > 0
* Is the size of the state.yaml less than 10 MB
  * OK if size of state.yaml < 5120 KB.
  * WARNING if size of state.yaml > 5120 KB and < 10240 KB.
  * CRITICAL if size of state.yaml > 10240 KB.
* Has an exception been thrown while checking.
  * OK if not.
  * CRITICAL if one was catched by the script.


Installation:
* Copy Python script to "/usr/lib/check_mk_agent/local/".
* Test it via running "check_mk_agent"