#!/usr/bin/env python
import os
from django_addon import startup


if __name__ == "__main__":
    startup.manage(path=os.path.dirname(os.path.abspath(__file__)))
