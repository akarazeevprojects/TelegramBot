#!/usr/bin/env python
import datetime

now = datetime.datetime.utcnow()

print(now.strftime("%Y%m%d_%H%M%S"))
