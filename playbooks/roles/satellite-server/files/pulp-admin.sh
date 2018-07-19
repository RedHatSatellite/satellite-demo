#!/bin/sh
# Satellite-install pulp-admin helper script
# Copyright (C) 2016  Billy Holmes <billy@gonoph.net>
#
# This file is part of Satellite-install.
#
# Satellite-install is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Satellite-install is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Satellite-install.  If not, see <http://www.gnu.org/licenses/>.

LOGIN=$(grep ^default_login /etc/pulp/server.conf  | cut -d ' ' -f 2)
PASS=$(grep ^default_pass /etc/pulp/server.conf  | cut -d ' ' -f 2)

exec pulp-admin -u "$LOGIN" -p "$PASS" "$@"
